"""Offline audit contracts; no legacy engine imports or provider requests."""

import copy
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts/legacy_audit.py"
SPEC = importlib.util.spec_from_file_location("legacy_audit", MODULE_PATH)
audit = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(audit)


def record(question="question", mode="no_context", score=0.5, details=None):
    return {
        "question": question,
        "ideal_answer": "archived ideal",
        "model_response": "A substantive policy answer.",
        "model_name": "model",
        "evaluation_mode": mode,
        "accuracy_score": score,
        "timestamp": "2025-08-29T12:00:00",
        "scores": {"llm_judge": {
            "score": score,
            "details": details if details is not None else {
                "both_judges_succeeded": True, "judge_1_score": score, "judge_2_score": score,
            },
        }},
    }


class ScoreAccountingTests(unittest.TestCase):
    def test_true_zero_retained_both_failed_zero_excluded(self):
        true_zero = record(score=0.0)
        both_failed = record("failed", score=0.0, details={
            "both_judges_failed": True, "judge_1_score": None, "judge_2_score": None,
        })
        good = record("good", score=1.0)
        stats = audit.summarize([true_zero, both_failed, good])
        self.assertEqual(stats["attempted_records"], 3)
        self.assertEqual(stats["valid_score_n"], 2)
        self.assertEqual(stats["mean"], 0.5)
        self.assertAlmostEqual(stats["recorded_numeric_mean"], 1 / 3)
        self.assertEqual(stats["both_judges_failed_n"], 1)
        self.assertEqual(stats["agreement"]["n"], 2)

    def test_generation_failure_excluded_even_with_numeric_score(self):
        for response in ("MODEL_FAILURE: timeout", "TASK_FAILURE: timeout", "Error: unavailable", "", None):
            with self.subTest(response=response):
                failed = record(score=0.0)
                failed["model_response"] = response
                stats = audit.summarize([failed, record("good", score=0.8)])
                self.assertEqual(stats["generation_failure_n"], 1)
                self.assertEqual(stats["valid_score_n"], 1)
                self.assertEqual(stats["mean"], 0.8)
                self.assertEqual(stats["agreement"]["n"], 1)

    def test_missing_invalid_and_boolean_scores(self):
        rows = [record(str(index), score=score) for index, score in
                enumerate((None, "0.5", True, -0.1, 1.1, float("nan"), float("inf"), 0.0))]
        stats = audit.summarize(rows)
        self.assertEqual(stats["missing_score_n"], 1)
        self.assertEqual(stats["invalid_score_n"], 6)
        self.assertEqual(stats["valid_score_n"], 1)
        self.assertEqual(stats["mean"], 0.0)

    def test_single_fallback_not_dual_agreement(self):
        single = record(score=0.0, details={
            "fallback_to": "judge_2", "judge_1_score": None, "judge_2_score": 0.0,
        })
        stats = audit.summarize([single, record("dual", score=1.0)])
        self.assertEqual(stats["single_fallback_only"], {"n": 1, "mean": 0.0})
        self.assertEqual(stats["dual_only"], {"n": 1, "mean": 1.0})
        self.assertEqual(stats["agreement"]["n"], 1)
        self.assertEqual(stats["valid_score_n"], 2)

    def test_missing_mode_is_not_zero(self):
        stats = audit.summarize([])
        self.assertEqual(stats["status"], "unrun")
        self.assertEqual(stats["attempted_records"], 0)
        self.assertIsNone(stats["mean"])
        comparison = audit.summary_comparisons(
            {"mode_performance": {"raw_files": 0.0}}, {"model": [record()]}, [record()])
        raw = next(c for c in comparison["comparisons"] if c["path"] == "mode_performance.raw_files")
        self.assertFalse(raw["matches"])
        self.assertIsNone(raw["recomputed"])
        self.assertEqual(raw["status"], "unrun")


class PairingTests(unittest.TestCase):
    def test_intersection_only_and_failure_excluded(self):
        rows = [record("paired", score=0.2), record("paired", "vector_db", 0.7),
                record("unpaired", score=0.9), record("failed", score=0.4),
                record("failed", "vector_db", 0.0, {"both_judges_failed": True})]
        pair = audit.paired_delta(rows, bootstrap_samples=100)
        self.assertEqual(pair["n"], 1)
        self.assertAlmostEqual(pair["mean_delta"], 0.5)
        self.assertEqual(pair["excluded_questions"]["missing_mode_question_n"], 1)
        self.assertEqual(pair["excluded_questions"]["invalid_score_question_n"], 1)
        self.assertAlmostEqual(pair["bootstrap"]["percentile_95_interval"][0], 0.5)

    def test_duplicate_keys_never_choose_arbitrary_record(self):
        rows = [record("duplicate"), record("duplicate", score=0.9), record("duplicate", "vector_db")]
        pair = audit.paired_delta(rows, bootstrap_samples=100)
        self.assertEqual(pair["n"], 0)
        self.assertIsNone(pair["mean_delta"])
        self.assertIsNone(pair["bootstrap"]["percentile_95_interval"])
        self.assertEqual(pair["excluded_questions"]["duplicate_key_question_n"], 1)

    def test_bootstrap_deterministic_and_row_order_independent(self):
        rows = [record(str(i), mode, score) for i in range(5)
                for mode, score in (("no_context", i / 10), ("vector_db", 0.7))]
        first = audit.paired_delta(rows, seed=7, bootstrap_samples=200)
        second = audit.paired_delta(list(reversed(rows)), seed=7, bootstrap_samples=200)
        self.assertEqual(first, second)
        self.assertEqual(first["n"], 5)
        self.assertAlmostEqual(first["mean_delta"], 0.5)


class ArchiveTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source = self.root / "source"
        self.archive = self.root / "archive"
        for relative in audit.SOURCES.values():
            path = self.source / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            if path.name == "detailed_results.json":
                value = {"model": [record(), record(mode="vector_db", score=0.75)]}
            else:
                value = {"metadata": {"timestamp": "2025-08-29T13:00:00"}}
            path.write_bytes((json.dumps(value, indent=3) + "\r\n").encode())
        self.dataset = self.root / "dataset.jsonl"
        self.dataset.write_text(json.dumps({"input": "question", "ideal": "new ideal", "id": "q1",
                                            "metadata": {"framework": "example"}}) + "\n")

    def test_six_originals_byte_preserved_and_idempotent(self):
        first = audit.import_archive(self.source, self.archive)
        second = audit.import_archive(self.source, self.archive)
        self.assertEqual(first, second)
        self.assertEqual(len(first["files"]), 6)
        for entry in first["files"]:
            content = (self.source / entry["source"]).read_bytes()
            self.assertEqual((self.archive / entry["path"]).read_bytes(), content)
            self.assertEqual(entry["bytes"], len(content))
            self.assertEqual(entry["sha256"], audit.sha256(content))
            self.assertFalse(Path(entry["source"]).is_absolute())
        self.assertEqual(audit.verify_archive(self.archive), first)

    def test_manifest_only_checkout_restores_missing_originals(self):
        manifest = audit.import_archive(self.source, self.archive)
        for entry in manifest["files"]:
            (self.archive / entry["path"]).unlink()
        restored = audit.import_archive(self.source, self.archive)
        self.assertEqual(restored, manifest)
        for entry in restored["files"]:
            self.assertEqual((self.archive / entry["path"]).read_bytes(),
                             (self.source / entry["source"]).read_bytes())

    def test_mutation_caught_read_only_and_not_overwritten(self):
        audit.import_archive(self.source, self.archive)
        target = self.archive / "root/detailed_results.json"
        before = target.read_bytes()
        mutation = before.replace(b"0.5", b"0.6", 1)
        self.assertEqual(len(mutation), len(before))
        target.write_bytes(mutation)
        manifest_before = (self.archive / "manifest.json").read_bytes()
        with self.assertRaisesRegex(audit.AuditError, "Checksum/byte-count mismatch"):
            audit.verify_archive(self.archive)
        with self.assertRaises(audit.AuditError):
            audit.import_archive(self.source, self.archive)
        self.assertEqual(target.read_bytes(), mutation)
        self.assertEqual((self.archive / "manifest.json").read_bytes(), manifest_before)

    def test_changed_source_rejected_without_replacing_archive(self):
        audit.import_archive(self.source, self.archive)
        source = self.source / "experiment_results/summary.json"
        target = self.archive / "root/summary.json"
        before = target.read_bytes()
        source.write_bytes(source.read_bytes() + b" ")
        with self.assertRaisesRegex(audit.AuditError, "Source differs"):
            audit.import_archive(self.source, self.archive)
        self.assertEqual(target.read_bytes(), before)

    def test_missing_file_and_unexpected_manifest_path_rejected(self):
        audit.import_archive(self.source, self.archive)
        target = self.archive / "root/summary.json"
        target.unlink()
        with self.assertRaisesRegex(audit.AuditError, "Cannot read archived evidence"):
            audit.verify_archive(self.archive)
        manifest_path = self.archive / "manifest.json"
        manifest = json.loads(manifest_path.read_text())
        manifest["files"][0]["path"] = "../outside.json"
        manifest_path.write_text(json.dumps(manifest))
        with self.assertRaisesRegex(audit.AuditError, "Unexpected or duplicate"):
            audit.verify_archive(self.archive)

    def test_audit_separates_runs_and_reports_ideal_drift(self):
        audit.import_archive(self.source, self.archive)
        report = audit.audit_archive(self.archive, self.dataset, bootstrap_samples=20)
        self.assertEqual(report["retained_record_n"], 6)
        self.assertEqual(set(report["runs"]), set(audit.RUNS))
        self.assertEqual(report["all_archive_question_coverage"]["archived_ideal_mismatch_record_n"], 6)
        for run in report["runs"].values():
            self.assertEqual(run["record_n"], 2)
            self.assertIsNone(run["by_mode"]["raw_files"]["mean"])
            self.assertEqual(run["models"]["model"]["paired_vector_minus_no_context"]["n"], 1)
        output = audit.json_bytes(report).decode()
        self.assertNotIn("A substantive policy answer", output)
        self.assertNotIn(str(self.source), output)

    def test_duplicate_current_questions_are_not_arbitrarily_joined(self):
        row = {"input": "question", "ideal": "archived ideal", "metadata": {"framework": "example"}}
        dataset = {audit.question_hash("question"): [row, copy.deepcopy(row)]}
        coverage = audit.question_coverage([record()], dataset)
        self.assertEqual(coverage["ambiguous_current_question_n"], 1)
        self.assertEqual(coverage["metadata_covered_question_n"], 0)
        self.assertIsNone(coverage["questions"][0]["archived_ideal_mismatch_record_n"])


if __name__ == "__main__":
    unittest.main()
