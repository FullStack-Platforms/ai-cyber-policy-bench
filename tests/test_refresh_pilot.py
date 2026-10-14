"""Synthetic unit fixtures only; these tests are not API or benchmark evidence."""

import csv
import importlib.util
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/refresh_pilot.py"
SPEC = importlib.util.spec_from_file_location("refresh_pilot", SCRIPT)
pilot = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(pilot)


class PilotTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.archive = self.root / "archive.json"
        self.dataset = self.root / "questions.jsonl"
        self.baseline = "openai/gpt-4o-mini"
        self.models = ["vendor/modern-a", "vendor/modern-b"]
        self.rows = [
            {"question": f"Question {index:02d}?", "ideal_answer": f"Historical reference {index}",
             "model_response": f"Legacy answer {index}", "model_name": self.baseline,
             "evaluation_mode": "no_context", "timestamp": "2025-08-29T12:00:00",
             "accuracy_score": 0.99, "scores": {"llm_judge": {"score": 0.99}}}
            for index in range(15)
        ]
        self.write_archive(self.rows)
        with self.dataset.open("w", encoding="utf-8") as handle:
            for index, row in enumerate(self.rows):
                handle.write(json.dumps({"input": row["question"], "ideal": "DO NOT SUBSTITUTE",
                                         "id": index, "metadata": {"difficulty": "test"}}) + "\n")

    def write_archive(self, rows):
        self.archive.write_text(json.dumps({self.baseline: rows}), encoding="utf-8")

    def plan(self, models=None):
        return pilot.build_plan(self.archive, self.dataset, self.baseline,
                                self.models if models is None else models, 128)

    def saved_run(self, missing=None, failed=None):
        plan = self.plan()
        run = self.root / "run"
        run.mkdir()
        pilot.save_json(run / "plan.json", plan)
        with (run / "results.jsonl").open("w", encoding="utf-8") as handle:
            for item in plan["requests"]:
                pair = (item["request"]["model"], item["question_id"])
                if pair == missing:
                    continue
                handle.write(json.dumps({
                    "question_id": item["question_id"], "requested_model": item["request"]["model"],
                    "requested_parameters": item["request"], "response": "Synthetic modern answer",
                    "actual_model": "vendor/returned-model", "generation_failed": pair == failed,
                    "error": {"type": "synthetic_fixture"} if pair == failed else None,
                    "timestamp": "2026-10-13T12:00:00+00:00", "usage": {"total_tokens": 4},
                    "finish_reason": "stop",
                }) + "\n")
        return run

    def packet(self, **kwargs):
        run = self.saved_run(**kwargs)
        output = self.root / "packet"
        pilot.make_review_packet(run, output, 19, "human-rubric-v1")
        return output

    def read_ratings(self, packet):
        with (packet / "review.csv").open(encoding="utf-8", newline="") as handle:
            return list(csv.DictReader(handle))

    def write_ratings(self, packet, rows):
        with (packet / "review.csv").open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=pilot.FIELDS)
            writer.writeheader()
            writer.writerows(rows)

    def rate(self, packet):
        key = pilot.load_json(packet / "identity-key.json")
        identities = {item["review_id"]: item for item in key["entries"]}
        rows = self.read_ratings(packet)
        for row in rows:
            identity = identities[row["review_id"]]
            row.update(reference_reviewed="yes", critical_error="no",
                       reviewed_reference="Expert-corrected " + row["question"],
                       score="0" if row["generation_status"] != "ok" else
                       "0.25" if identity["arm"] == "legacy" else "0.75")
        self.write_ratings(packet, rows)
        return rows

    def compare(self, packet):
        return pilot.compare_ratings(packet / "review.csv", packet / "identity-key.json", seed=7, samples=200)

    def test_plan_preserves_full_panel_and_ignores_legacy_scores(self):
        plan = self.plan()
        self.assertEqual(plan["request_count"], 30)
        self.assertEqual(plan["maximum_output_tokens"], 3840)
        self.assertEqual([q["question_id"] for q in plan["questions"]], sorted(q["question_id"] for q in plan["questions"]))
        self.assertEqual(plan["questions"][0]["historical_reference"], next(r["ideal_answer"] for r in self.rows if r["question"] == plan["questions"][0]["question"]))
        self.assertNotIn("accuracy_score", json.dumps(plan))
        self.assertNotIn("llm_judge", json.dumps(plan))
        self.write_archive(list(reversed(self.rows)))
        self.assertEqual(plan["questions"], self.plan()["questions"])

    def test_baseline_missing_duplicates_and_partial_panel_rejected(self):
        with self.assertRaisesRegex(ValueError, "baseline model not found"):
            pilot.build_plan(self.archive, self.dataset, "not-present", self.models)
        for rows in (self.rows[:-1], self.rows + [self.rows[0]]):
            with self.subTest(count=len(rows)):
                self.write_archive(rows)
                with self.assertRaises(ValueError):
                    self.plan()

    def test_duplicate_models_and_unbounded_tokens_rejected(self):
        with self.assertRaisesRegex(ValueError, "pseudoreplication"):
            self.plan(["same/model", "same/model"])
        for limit in (0, -1, 4097):
            with self.subTest(limit=limit), self.assertRaises(ValueError):
                pilot.build_plan(self.archive, self.dataset, self.baseline, self.models, limit)

    def test_historical_generation_failure_retained(self):
        for response in ("MODEL_FAILURE: historical timeout", "TASK_FAILURE: interrupted", ""):
            with self.subTest(response=response):
                self.rows[0]["model_response"] = response
                self.write_archive(self.rows)
                item = next(q for q in self.plan()["questions"] if q["question"] == self.rows[0]["question"])
                self.assertTrue(item["legacy"]["generation_failed"])
                self.assertEqual(item["legacy"]["response"], response)
                self.assertIsNone(item["legacy"]["actual_model"])

    def test_request_ceiling_rejected_before_call_or_directory_or_key(self):
        caller = Mock(side_effect=AssertionError("No network call is permitted"))
        destination = self.root / "forbidden"
        with (
            patch.dict(os.environ, {}, clear=True),
            self.assertRaisesRegex(ValueError, "ceiling exceeded"),
        ):
            pilot.execute_run(self.plan(), destination, 29, execute=True, caller=caller)
        caller.assert_not_called()
        self.assertFalse(destination.exists())

    def test_dry_run_never_calls_or_writes_or_needs_key(self):
        caller = Mock(side_effect=AssertionError("No network call is permitted"))
        destination = self.root / "dry"
        with patch.dict(os.environ, {}, clear=True):
            result = pilot.execute_run(self.plan(), destination, 30, caller=caller)
        self.assertTrue(result["dry_run"])
        self.assertEqual(result["network_calls"], 0)
        caller.assert_not_called()
        self.assertFalse(destination.exists())

    def test_existing_run_never_overwritten(self):
        destination = self.root / "existing"
        destination.mkdir()
        caller = Mock()
        with (
            patch.dict(os.environ, {"OPENROUTER_API_KEY": "unit-test-secret"}),
            self.assertRaises(FileExistsError),
        ):
            pilot.execute_run(self.plan(), destination, 30, execute=True, caller=caller)
        caller.assert_not_called()

    def test_secret_redaction_in_nested_provider_fields(self):
        self.assertEqual(pilot.redact({"error": ["contains secret", {"secret": "secret"}]}, "secret"),
                         {"error": ["contains [REDACTED]", {"[REDACTED]": "[REDACTED]"}]})

    def test_packet_seed_reproducible_and_unrated_fields_blank(self):
        packet = self.packet()
        second = self.root / "packet2"
        pilot.make_review_packet(self.root / "run", second, 19, "human-rubric-v1")
        self.assertEqual((packet / "review.csv").read_bytes(), (second / "review.csv").read_bytes())
        rows = self.read_ratings(packet)
        self.assertEqual(len(rows), 45)  # One legacy, not duplicated per modern model.
        self.assertTrue(all(row["score"] == "" and row["critical_error"] == "" for row in rows))
        self.assertNotIn("requested_model", rows[0])
        self.assertNotIn("arm", rows[0])
        with self.assertRaises(FileExistsError):
            pilot.make_review_packet(self.root / "run", packet, 19, "human-rubric-v1")

    def test_complete_pairs_use_each_question_once_per_model(self):
        packet = self.packet()
        rows = self.rate(packet)
        result = self.compare(packet)
        self.assertEqual(len(result["comparisons"]), 2)
        for comparison in result["comparisons"]:
            self.assertEqual(comparison["n"], 15)
            self.assertEqual(comparison["mean_paired_difference"], 0.5)
            self.assertEqual(comparison["bootstrap_95_percent_interval"], [0.5, 0.5])
            self.assertEqual(comparison["legacy"]["missing_ratings"], 0)
        self.write_ratings(packet, list(reversed(rows)))
        self.assertEqual(result, self.compare(packet))

    def test_missing_and_failed_generations_retained_and_human_rated(self):
        qids = [q["question_id"] for q in self.plan()["questions"]]
        packet = self.packet(missing=(self.models[0], qids[0]), failed=(self.models[0], qids[1]))
        rows = self.rate(packet)
        comparison = self.compare(packet)["comparisons"][0]
        self.assertEqual(comparison["n"], 15)
        self.assertEqual(comparison["modern"]["missing_generations"], 1)
        self.assertEqual(comparison["modern"]["generation_failures"], 1)
        self.assertAlmostEqual(comparison["mean_paired_difference"], 0.4)
        failed_row = next(row for row in rows if row["generation_status"] == "missing")
        failed_row["score"] = "0.75"
        self.write_ratings(packet, rows)
        with self.assertRaisesRegex(ValueError, "explicit zero task utility"):
            self.compare(packet)

    def test_missing_invalid_or_nonfinite_ratings_rejected(self):
        packet = self.packet()
        rows = self.rate(packet)
        for score in ("", "NaN", "inf", "-0.1", "1.1", "not-a-number"):
            with self.subTest(score=score):
                altered = [dict(row) for row in rows]
                altered[0]["score"] = score
                self.write_ratings(packet, altered)
                with self.assertRaises(ValueError):
                    self.compare(packet)
        self.write_ratings(packet, rows[:-1])
        with self.assertRaisesRegex(ValueError, "missing rows"):
            self.compare(packet)
        self.write_ratings(packet, rows + [rows[0]])
        with self.assertRaisesRegex(ValueError, "Duplicate"):
            self.compare(packet)

    def test_identity_rubric_reference_and_critical_error_validation(self):
        packet = self.packet()
        rows = self.rate(packet)
        for field, value in (("question", "Changed question"), ("question_id", "wrong"),
                             ("response", "Changed response"), ("historical_reference", "Changed ideal"),
                             ("rubric_version", "other-version"), ("reference_reviewed", ""),
                             ("reviewed_reference", "Mismatched expert correction"),
                             ("critical_error", ""), ("critical_error", "maybe")):
            with self.subTest(field=field, value=value):
                altered = [dict(row) for row in rows]
                altered[0][field] = value
                self.write_ratings(packet, altered)
                with self.assertRaises(ValueError):
                    self.compare(packet)

    def test_bootstrap_deterministic_nonconstant_pairs(self):
        differences = [-0.5, 0.25, 0.75, 0.0]
        first = pilot.bootstrap_interval(differences, 33, 500)
        self.assertEqual(first, pilot.bootstrap_interval(differences, 33, 500))
        self.assertLess(first[0], first[1])
        self.assertGreaterEqual(first[0], min(differences))
        self.assertLessEqual(first[1], max(differences))


if __name__ == "__main__":
    unittest.main()
