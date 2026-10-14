#!/usr/bin/env python3
"""Offline, standard-library-only preservation and descriptive audit of six exports."""

import argparse
import hashlib
import json
import math
import random
import statistics
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
DEFAULT_ARCHIVE = REPO / "data/legacy/8-19-run"
DEFAULT_DATASET = REPO / "data/prompts/cyber_evals.jsonl"
RUNS = ("root", "11-chunks", "67-chunks")
MODES = ("no_context", "vector_db", "raw_files")
FILES = ("detailed_results.json", "summary.json")
SOURCES = {
    f"{run}/{name}": f"{'' if run == 'root' else run + '/'}experiment_results/{name}"
    for run in RUNS for name in FILES
}


class AuditError(ValueError):
    """Actionable evidence or input error."""


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def question_hash(question):
    return sha256(question.encode("utf-8"))


def load_json(path):
    try:
        return json.loads(Path(path).read_bytes())
    except (OSError, ValueError) as exc:
        raise AuditError(f"Cannot read JSON {path}: {exc}") from exc


def json_bytes(value):
    return (json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n").encode("utf-8")


def verify_archive(archive):
    """Read only; validate exact manifest layout, sizes and hashes before analysis."""
    archive = Path(archive)
    manifest = load_json(archive / "manifest.json")
    if not isinstance(manifest, dict) or manifest.get("schema_version") != 1:
        raise AuditError("Unsupported or malformed archive manifest")
    entries = manifest.get("files")
    if not isinstance(entries, list) or len(entries) != len(SOURCES):
        raise AuditError("Manifest must contain precisely six original JSON files")
    seen = set()
    for entry in entries:
        if not isinstance(entry, dict):
            raise AuditError("Malformed manifest file entry")
        label = entry.get("path")
        if label not in SOURCES or label in seen:
            raise AuditError(f"Unexpected or duplicate manifest path: {label!r}")
        seen.add(label)
        if entry.get("source") != SOURCES[label]:
            raise AuditError(f"Incorrect relative source label for {label}")
        path = archive / label
        if path.is_symlink() or path.parent.is_symlink():
            raise AuditError(f"Archive evidence must not be a symlink: {label}")
        try:
            content = path.read_bytes()
        except OSError as exc:
            raise AuditError(f"Cannot read archived evidence {label}: {exc}") from exc
        if len(content) != entry.get("bytes") or sha256(content) != entry.get("sha256"):
            raise AuditError(f"Checksum/byte-count mismatch for {label}; evidence has changed")
    actual = {p.relative_to(archive).as_posix() for p in archive.rglob("*.json")}
    if actual != set(SOURCES) | {"manifest.json"}:
        raise AuditError("Archive contains unexpected JSON files outside the six-file manifest")
    return manifest


def import_archive(source, archive):
    """Copy exactly six originals without rewriting JSON or replacing changed evidence."""
    source, archive = Path(source), Path(archive)
    payloads = {}
    for label, relative_source in SOURCES.items():
        try:
            payloads[label] = (source / relative_source).read_bytes()
            json.loads(payloads[label])
        except (OSError, ValueError) as exc:
            raise AuditError(f"Cannot import {relative_source}: {exc}") from exc
    manifest = {
        "schema_version": 1,
        "source_labels_relative_to": "original 8-19-run directory (not a claimed run date)",
        "files": [
            {"path": label, "source": SOURCES[label], "sha256": sha256(content), "bytes": len(content)}
            for label, content in sorted(payloads.items())
        ],
    }
    if (archive / "manifest.json").exists():
        existing = load_json(archive / "manifest.json")
        if existing != manifest:
            raise AuditError("Source differs from the preserved manifest; refusing to overwrite evidence")
        # A public checkout retains only the manifest. Restore absent evidence,
        # but never replace an existing file whose bytes differ.
        for label, content in payloads.items():
            target = archive / label
            if target.is_symlink() or target.parent.is_symlink():
                raise AuditError(f"Archive evidence must not be a symlink: {label}")
            if target.exists() and target.read_bytes() != content:
                raise AuditError(f"Checksum/byte-count mismatch for {label}; evidence has changed")
        for label, content in payloads.items():
            target = archive / label
            if not target.exists():
                target.parent.mkdir(parents=True, exist_ok=True)
                with target.open("xb") as stream:
                    stream.write(content)
        return verify_archive(archive)
    if archive.exists() and any(p.is_file() or p.is_symlink() for p in archive.rglob("*")):
        raise AuditError("Nonempty archive has no manifest; refusing to overwrite untracked evidence")
    archive.mkdir(parents=True, exist_ok=True)
    for label, content in payloads.items():
        target = archive / label
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("xb") as stream:
            stream.write(content)
    with (archive / "manifest.json").open("xb") as stream:
        stream.write(json_bytes(manifest))
    return manifest


def valid_number(value):
    return isinstance(value, (float, int)) and not isinstance(value, bool) and math.isfinite(value) and 0 <= value <= 1


def mean(values):
    return statistics.fmean(values) if values else None


def record_status(row):
    response = row.get("model_response")
    generation_failed = (
        not isinstance(response, str) or not response.strip()
        or response.lstrip().upper().startswith(("MODEL_FAILURE:", "TASK_FAILURE:", "ERROR:"))
        or row.get("generation_failed") is True or row.get("generation_error") not in (None, False, "")
    )
    scores = row.get("scores") or {}
    judge = scores.get("llm_judge") or {}
    details = judge.get("details") or {}
    first, second = details.get("judge_1_score"), details.get("judge_2_score")
    if details.get("both_judges_failed") is True:
        kind = "both_failed"
    elif details.get("both_judges_succeeded") is True and valid_number(first) and valid_number(second):
        kind = "dual"
    elif details.get("fallback_to") in ("judge_1", "judge_2") and valid_number(first) != valid_number(second):
        selected = first if details["fallback_to"] == "judge_1" else second
        kind = "single_fallback" if valid_number(selected) else "unknown"
    else:
        kind = "unknown"
    score = row.get("accuracy_score")
    eligible = valid_number(score) and not generation_failed and kind != "both_failed"
    return {
        "generation_failed": generation_failed,
        "judge_kind": kind,
        "eligible": eligible,
        "score": score if eligible else None,
        "score_missing": score is None,
        "score_invalid": score is not None and not valid_number(score),
        "judge_pair": (first, second) if kind == "dual" and not generation_failed else None,
        "judge_score_mismatch": valid_number(score) and valid_number(judge.get("score"))
        and not math.isclose(score, judge["score"], abs_tol=1e-12),
    }


def summarize(rows):
    statuses = [record_status(row) for row in rows]
    valid = [s["score"] for s in statuses if s["eligible"]]
    dual = [s["score"] for s in statuses if s["eligible"] and s["judge_kind"] == "dual"]
    single = [s["score"] for s in statuses if s["eligible"] and s["judge_kind"] == "single_fallback"]
    pairs = [s["judge_pair"] for s in statuses if s["judge_pair"] is not None]
    differences = [abs(a - b) for a, b in pairs]
    return {
        "status": "observed" if rows else "unrun",
        "attempted_records": len(rows),
        "unique_questions": len({question_hash(r["question"]) for r in rows}),
        "valid_score_n": len(valid), "mean": mean(valid),
        "recorded_numeric_score_n": sum(valid_number(r.get("accuracy_score")) for r in rows),
        "recorded_numeric_mean": mean([r["accuracy_score"] for r in rows if valid_number(r.get("accuracy_score"))]),
        "generation_failure_n": sum(s["generation_failed"] for s in statuses),
        "missing_score_n": sum(s["score_missing"] for s in statuses),
        "invalid_score_n": sum(s["score_invalid"] for s in statuses),
        "excluded_score_n": len(rows) - len(valid),
        "dual_judge_n": sum(s["judge_kind"] == "dual" for s in statuses),
        "single_fallback_n": sum(s["judge_kind"] == "single_fallback" for s in statuses),
        "both_judges_failed_n": sum(s["judge_kind"] == "both_failed" for s in statuses),
        "unknown_judge_status_n": sum(s["judge_kind"] == "unknown" for s in statuses),
        "accuracy_vs_llm_judge_score_mismatch_n": sum(s["judge_score_mismatch"] for s in statuses),
        "dual_only": {"n": len(dual), "mean": mean(dual)},
        "single_fallback_only": {"n": len(single), "mean": mean(single)},
        "agreement": {
            "n": len(pairs), "mean_absolute_difference": mean(differences),
            "exact_agreement_n": sum(math.isclose(d, 0, abs_tol=1e-12) for d in differences),
            "within_0_10_n": sum(d <= 0.10 + 1e-12 for d in differences),
            "denominator": "genuine dual numeric judge results, excluding failed generations",
        },
    }


def percentile(sorted_values, fraction):
    position = (len(sorted_values) - 1) * fraction
    lo, hi = math.floor(position), math.ceil(position)
    return sorted_values[lo] + (sorted_values[hi] - sorted_values[lo]) * (position - lo)


def paired_delta(rows, seed=20250830, bootstrap_samples=10000):
    by_mode = {mode: defaultdict(list) for mode in ("no_context", "vector_db")}
    for row in rows:
        if row["evaluation_mode"] in by_mode:
            by_mode[row["evaluation_mode"]][question_hash(row["question"])].append(row)
    keys = sorted(set(by_mode["no_context"]) | set(by_mode["vector_db"]))
    pairs, excluded = [], Counter()
    for key in keys:
        left, right = by_mode["no_context"].get(key, []), by_mode["vector_db"].get(key, [])
        if not left or not right:
            excluded["missing_mode_question_n"] += 1
        elif len(left) != 1 or len(right) != 1:
            excluded["duplicate_key_question_n"] += 1
        else:
            a, b = record_status(left[0]), record_status(right[0])
            if not a["eligible"] or not b["eligible"]:
                excluded["invalid_score_question_n"] += 1
            else:
                pairs.append({"question_sha256": key, "no_context": a["score"], "vector_db": b["score"],
                              "delta": b["score"] - a["score"],
                              "includes_single_fallback": "single_fallback" in (a["judge_kind"], b["judge_kind"])})
    deltas = [p["delta"] for p in pairs]
    interval = None
    if deltas and bootstrap_samples:
        rng = random.Random(seed)
        draws = sorted(statistics.fmean(deltas[rng.randrange(len(deltas))] for _ in deltas)
                       for _ in range(bootstrap_samples))
        interval = [percentile(draws, 0.025), percentile(draws, 0.975)]
    return {
        "direction": "vector_db minus no_context", "n": len(pairs), "mean_delta": mean(deltas),
        "no_context_paired_mean": mean([p["no_context"] for p in pairs]),
        "vector_db_paired_mean": mean([p["vector_db"] for p in pairs]),
        "single_fallback_pair_n": sum(p["includes_single_fallback"] for p in pairs),
        "excluded_questions": {key: excluded[key] for key in
                               ("missing_mode_question_n", "duplicate_key_question_n", "invalid_score_question_n")},
        "bootstrap": {"seed": seed, "resamples": bootstrap_samples, "percentile_95_interval": interval,
                      "unit": "paired question", "interpretation": "descriptive resampling of this fixed question panel; not causal or temporal evidence"},
        "pairs": pairs,
    }


def load_records(path):
    data = load_json(path)
    if not isinstance(data, dict):
        raise AuditError(f"Expected model-to-record-list object: {path}")
    rows, model_mismatches = [], []
    for model, records in data.items():
        if not isinstance(records, list):
            raise AuditError(f"Expected record list for model {model}: {path}")
        for index, row in enumerate(records):
            if not isinstance(row, dict) or not isinstance(row.get("question"), str) or not isinstance(row.get("evaluation_mode"), str):
                raise AuditError(f"Invalid question/mode record {model}[{index}] in {path}")
            if row.get("model_name") != model:
                model_mismatches.append({"model_group": model, "index": index, "record_model": row.get("model_name")})
            for key in ("scores",):
                if row.get(key) is not None and not isinstance(row[key], dict):
                    raise AuditError(f"Malformed scores in {model}[{index}]")
            judge = (row.get("scores") or {}).get("llm_judge")
            if judge is not None and (not isinstance(judge, dict) or
                                     (judge.get("details") is not None and not isinstance(judge["details"], dict))):
                raise AuditError(f"Malformed judge details in {model}[{index}]")
            rows.append((model, row))
    return data, rows, model_mismatches


def read_dataset(path):
    try:
        content = Path(path).read_bytes()
    except OSError as exc:
        raise AuditError(f"Cannot read current dataset: {exc}") from exc
    index = defaultdict(list)
    for number, line in enumerate(content.splitlines(), 1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
            if not isinstance(row, dict) or not isinstance(row.get("input"), str):
                raise TypeError("expected object with string input")
            index[question_hash(row["input"])].append(row)
        except (ValueError, TypeError) as exc:
            raise AuditError(f"Invalid current dataset line {number}: {exc}") from exc
    return index, content


def question_coverage(rows, dataset):
    questions = defaultdict(list)
    for row in rows:
        questions[question_hash(row["question"])].append(row)
    fields = sorted({key for candidates in dataset.values() for row in candidates
                     for key in (row.get("metadata") or {})})
    field_counts = Counter()
    inventory = []
    for key, archived in sorted(questions.items()):
        candidates = [r for r in dataset.get(key, []) if r["input"] == archived[0]["question"]]
        current = candidates[0] if len(candidates) == 1 else None
        metadata = (current.get("metadata") or {}) if current else {}
        present = [field for field in fields if metadata.get(field) not in (None, "")]
        field_counts.update(present)
        mismatch_n = sum(r.get("ideal_answer") != current.get("ideal") for r in archived) if current else None
        inventory.append({"question_sha256": key, "archived_record_n": len(archived),
                          "current_exact_match_n": len(candidates),
                          "current_id": current.get("id") if current else None,
                          "metadata_fields_present": present,
                          "archived_ideal_mismatch_record_n": mismatch_n,
                          "current_ideal_missing": current is not None and not isinstance(current.get("ideal"), str),
                          "distinct_archived_ideals_n": len({r.get("ideal_answer") for r in archived})})
    return {
        "unique_questions": len(questions),
        "exact_matched_question_n": sum(i["current_exact_match_n"] > 0 for i in inventory),
        "unambiguous_matched_question_n": sum(i["current_exact_match_n"] == 1 for i in inventory),
        "unmatched_question_n": sum(i["current_exact_match_n"] == 0 for i in inventory),
        "ambiguous_current_question_n": sum(i["current_exact_match_n"] > 1 for i in inventory),
        "metadata_covered_question_n": sum(bool(i["metadata_fields_present"]) for i in inventory),
        "metadata_fields_question_n": {field: field_counts[field] for field in fields},
        "archived_ideal_mismatch_record_n": sum(i["archived_ideal_mismatch_record_n"] or 0 for i in inventory),
        "archived_ideal_mismatch_question_n": sum(bool(i["archived_ideal_mismatch_record_n"]) for i in inventory),
        "ideal_comparison": "exact text against current dataset ideal, only unambiguous exact-question matches; not a judgment of answer quality",
        "questions": inventory,
    }


def summary_comparisons(summary, models, rows):
    comparisons = []

    def compare(path, reported, recomputed, raw=None, status="observed"):
        matches = (reported == recomputed if not isinstance(recomputed, (int, float))
                   else isinstance(reported, (int, float)) and not isinstance(reported, bool)
                   and math.isclose(reported, recomputed, rel_tol=1e-10, abs_tol=1e-12))
        comparisons.append({"path": path, "reported": reported, "recomputed": recomputed,
                            "matches": matches, "status": status,
                            "recorded_numeric_mean_including_failure_placeholders": raw})

    def score(path, reported, selected):
        stats = summarize(selected)
        compare(path, reported, stats["mean"], mean([r["accuracy_score"] for r in selected if valid_number(r.get("accuracy_score"))]), stats["status"])

    compare("total_models", summary.get("total_models"), len(models))
    overall = summary.get("overall_stats") or {}
    compare("overall_stats.total_evaluations", overall.get("total_evaluations"), len(rows))
    score("overall_stats.average_score", overall.get("average_score"), rows)
    reported_models = summary.get("models") or {}
    for model in sorted(set(models) | set(reported_models)):
        selected = models.get(model, [])
        reported = reported_models.get(model, {})
        prefix = f"models.{model}"
        compare(prefix + ".total_evaluations", reported.get("total_evaluations"), len(selected))
        score(prefix + ".average_score", reported.get("average_score"), selected)
        modes = reported.get("score_by_mode") or {}
        for mode in sorted(set(MODES) | set(modes) | {r["evaluation_mode"] for r in selected}):
            score(prefix + f".score_by_mode.{mode}", modes.get(mode), [r for r in selected if r["evaluation_mode"] == mode])
    mode_summary = summary.get("mode_performance") or {}
    for mode in sorted(set(MODES) | set(mode_summary) | {r["evaluation_mode"] for r in rows}):
        score(f"mode_performance.{mode}", mode_summary.get(mode), [r for r in rows if r["evaluation_mode"] == mode])
    return {"checked_fields": len(comparisons), "differing_fields": sum(not c["matches"] for c in comparisons), "comparisons": comparisons}


def audit_archive(archive, dataset_path, bootstrap_samples=10000, seed=20250830):
    if bootstrap_samples < 0:
        raise AuditError("Bootstrap resamples must be nonnegative")
    manifest = verify_archive(archive)
    dataset, dataset_bytes = read_dataset(dataset_path)
    report = {
        "schema_version": 1,
        "evidence_manifest": manifest,
        "dataset": {"label": Path(dataset_path).name, "sha256": sha256(dataset_bytes), "bytes": len(dataset_bytes),
                    "rows": sum(map(len, dataset.values())), "unique_question_hashes": len(dataset),
                    "duplicate_question_hashes": {k: len(v) for k, v in sorted(dataset.items()) if len(v) > 1}},
        "method": {
            "score": "archived accuracy_score, finite numeric [0,1], excluding explicit both-judge failures and generation failures; genuine zero retained",
            "attempted_records": "stored rows, not provider request/retry counts",
            "single_fallback": "included when otherwise valid, also reported separately; not dual agreement",
            "unrun": "no stored records: mean null, not zero",
            "question_join": "SHA256(exact UTF-8 question), additionally checked for exact text equality",
            "pairing": "within run/model, exact-question intersection with valid scores in both modes; all duplicate question/mode keys excluded",
            "scope": "three separate export groups, no cross-run pooled leaderboard or temporal/causal interpretation",
            "uncertainty": "question-level percentile bootstrap, fixed seed and sorted question hashes; fixed-panel descriptive uncertainty, not model/judge run-to-run variance",
            "provenance": "July 26 2025 authorship is user recollection, not established by these exports; directory 8-19-run is a source label, not a date claim",
            "unknown": ["actual judge model identifiers and revisions", "historical request parameters and provider revisions", "token usage and cost", "request latency and retry counts", "timestamp timezone", "independence of collection processes across export groups"],
            "failure_caveat": "Failure/fallback counts describe archive flags, not confirmed provider failures. Current legacy scorer accepts judge results only when accuracy_score > 0 (src/scorer.py:dual_llm_judge_score). The two both-failed records contain substantive explanations justifying zero. Excluding their zeros is a flag-filtered sensitivity analysis, not an established correction; compare recorded_numeric_mean. Lost judge scores cannot be reconstructed reliably.",
        },
        "runs": {},
    }
    all_rows = []
    for run in RUNS:
        models, grouped_rows, mismatches = load_records(Path(archive) / run / "detailed_results.json")
        rows = [row for _, row in grouped_rows]
        all_rows.extend(rows)
        summary = load_json(Path(archive) / run / "summary.json")
        if not isinstance(summary, dict):
            raise AuditError(f"Expected summary object for {run}")
        keys = Counter((model, row["evaluation_mode"], question_hash(row["question"])) for model, row in grouped_rows)
        stamps = [r.get("timestamp") for r in rows]
        valid_stamps, invalid_stamps = [], 0
        for stamp in stamps:
            try:
                datetime.fromisoformat(stamp)
                valid_stamps.append(stamp)
            except (TypeError, ValueError):
                invalid_stamps += 1
        counts = Counter(valid_stamps)
        modes = sorted(set(MODES) | {r["evaluation_mode"] for r in rows})
        report["runs"][run] = {
            "record_n": len(rows), "model_n": len(models),
            "counts": summarize(rows),
            "by_mode": {mode: summarize([r for r in rows if r["evaluation_mode"] == mode]) for mode in modes},
            "models": {model: {"counts": summarize(records),
                               "modes": {mode: summarize([r for r in records if r["evaluation_mode"] == mode]) for mode in modes},
                               "paired_vector_minus_no_context": paired_delta(records, seed, bootstrap_samples)}
                       for model, records in sorted(models.items())},
            "question_coverage": question_coverage(rows, dataset),
            "duplicate_keys": [{"model": model, "mode": mode, "question_sha256": key, "record_n": count}
                               for (model, mode, key), count in sorted(keys.items()) if count > 1],
            "model_group_mismatches": mismatches,
            "timestamps": {"source_summary": (summary.get("metadata") or {}).get("timestamp"),
                           "record_min": min(valid_stamps) if valid_stamps else None,
                           "record_max": max(valid_stamps) if valid_stamps else None,
                           "missing_or_invalid_n": invalid_stamps,
                           "repeated_record_timestamps": {k: v for k, v in sorted(counts.items()) if v > 1},
                           "timezone": "not established; timestamps retained verbatim"},
            "source_configuration": (summary.get("metadata") or {}).get("configuration"),
            "source_summary_audit": summary_comparisons(summary, models, rows),
        }
    report["retained_record_n"] = len(all_rows)
    report["all_archive_question_coverage"] = question_coverage(all_rows, dataset)
    return report


def fmt(value):
    return "unavailable" if value is None else f"{value:.6f}"


def render_markdown(report):
    lines = ["# Preserved legacy export audit", "",
             f"Retained **{report['retained_record_n']} records in {len(report['runs'])} separate runs**. Six originals are byte-preserved and checked against the manifest before analysis. No cross-run leaderboard is produced.", "",
             "## Interpretation and limits", ""]
    lines.extend(f"- **{key.replace('_', ' ')}:** {value}" for key, value in report["method"].items() if key != "unknown")
    lines.append("- **Unknown:** " + "; ".join(report["method"]["unknown"]) + ".")
    lines.extend(["", "## Evidence manifest", "", "Source labels are relative to the supplied original directory; no absolute machine paths are recorded.", "",
                  "| Preserved file | Original relative source | Bytes | SHA256 |", "|---|---|---:|---|"])
    for entry in report["evidence_manifest"]["files"]:
        lines.append(f"| {entry['path']} | {entry['source']} | {entry['bytes']} | `{entry['sha256']}` |")
    coverage = report["all_archive_question_coverage"]
    lines.extend(["", "## Current dataset join", "",
                  f"Dataset `{report['dataset']['label']}`: {report['dataset']['rows']} rows; SHA256 `{report['dataset']['sha256']}`.",
                  f"Archived unique questions: {coverage['unique_questions']}; exact matches: {coverage['exact_matched_question_n']}; ambiguous: {coverage['ambiguous_current_question_n']}; unmatched: {coverage['unmatched_question_n']}; questions with metadata: {coverage['metadata_covered_question_n']}.",
                  f"Archived/current ideal text mismatches: {coverage['archived_ideal_mismatch_record_n']} records / {coverage['archived_ideal_mismatch_question_n']} questions (not a quality verdict).",
                  f"Current dataset duplicate question hashes: {len(report['dataset']['duplicate_question_hashes'])}.",
                  "Metadata field coverage (unique archived questions): " + ", ".join(f"{k}={v}" for k, v in coverage["metadata_fields_question_n"].items()) + "."])
    for run, data in report["runs"].items():
        counts, stamps, questions = data["counts"], data["timestamps"], data["question_coverage"]
        lines.extend(["", f"## Run: {run}", "",
                      f"{data['record_n']} retained rows; {data['model_n']} model labels; {questions['unique_questions']} unique questions. Duplicate model/mode/question keys: {len(data['duplicate_keys'])}; model-label mismatches: {len(data['model_group_mismatches'])}.",
                      f"Record timestamps: `{stamps['record_min']}` through `{stamps['record_max']}`; source summary timestamp `{stamps['source_summary']}`. Missing/invalid timestamps: {stamps['missing_or_invalid_n']}; repeated timestamp values: {len(stamps['repeated_record_timestamps'])}. Timezone unknown.",
                      f"Valid-score n={counts['valid_score_n']}; generation failures={counts['generation_failure_n']}; missing scores={counts['missing_score_n']}; invalid numeric scores={counts['invalid_score_n']}; dual={counts['dual_judge_n']}; single fallback={counts['single_fallback_n']}; both failed={counts['both_judges_failed_n']}; unknown judge status={counts['unknown_judge_status_n']}.",
                      f"Stored numeric mean (including failure-labelled zeros)={fmt(counts['recorded_numeric_mean'])}; flag-filtered mean={fmt(counts['mean'])}. Neither is newly verified accuracy; do not call the difference model improvement.",
                      "", "### Model/mode descriptive scores", "",
                      "Means include eligible single fallbacks; dual-only and fallback-only means are shown independently. Unrun modes have no score. Model rows are alphabetic, not ranked.", "",
                      "| Model | Mode | Attempted | Valid n | Mean | Dual-only mean (n) | Fallback-only mean (n) | Generation failed | Missing / invalid | Both judges failed |",
                      "|---|---|---:|---:|---:|---|---|---:|---:|---:|"])
        for model, model_data in data["models"].items():
            for mode, stats in model_data["modes"].items():
                dual, single = stats["dual_only"], stats["single_fallback_only"]
                value = "unrun" if stats["status"] == "unrun" else fmt(stats["mean"])
                lines.append(f"| {model} | {mode} | {stats['attempted_records']} | {stats['valid_score_n']} | {value} | {fmt(dual['mean'])} ({dual['n']}) | {fmt(single['mean'])} ({single['n']}) | {stats['generation_failure_n']} | {stats['missing_score_n']} / {stats['invalid_score_n']} | {stats['both_judges_failed_n']} |")
        agreement = counts["agreement"]
        lines.extend(["", "### Genuine dual-judge agreement", "",
                      f"n={agreement['n']}; mean absolute judge-score difference={fmt(agreement['mean_absolute_difference'])}; exact agreement={agreement['exact_agreement_n']}/{agreement['n']}; absolute difference ≤0.10={agreement['within_0_10_n']}/{agreement['n']}. Failed/single judgments do not enter this denominator. Per-model/mode agreement is in the JSON report.",
                      "", "### Paired vector-minus-no-context deltas", "",
                      "Only valid, uniquely keyed question intersections within this run/model. Descriptive, not temporal improvement or a causal retrieval effect; fixed-panel bootstrap intervals do not measure all sources of uncertainty.", "",
                      "| Model | Paired n | No-context mean | Vector mean | Mean delta | Question-bootstrap 95% interval | Pairs with fallback | Excluded questions |",
                      "|---|---:|---:|---:|---:|---|---:|---:|"])
        for model, model_data in data["models"].items():
            pair = model_data["paired_vector_minus_no_context"]
            interval = pair["bootstrap"]["percentile_95_interval"]
            ci = "unavailable" if interval is None else f"[{fmt(interval[0])}, {fmt(interval[1])}]"
            lines.append(f"| {model} | {pair['n']} | {fmt(pair['no_context_paired_mean'])} | {fmt(pair['vector_db_paired_mean'])} | {fmt(pair['mean_delta'])} | {ci} | {pair['single_fallback_pair_n']} | {sum(pair['excluded_questions'].values())} |")
        bootstrap = next(iter(data["models"].values()))["paired_vector_minus_no_context"]["bootstrap"] if data["models"] else {}
        lines.extend(["", f"Bootstrap: {bootstrap.get('resamples', 0)} resamples per model, seed {bootstrap.get('seed')}, paired-question resampling with replacement and interpolated percentile endpoints.",
                      "", "### Source summary reconciliation", "",
                      f"{data['source_summary_audit']['checked_fields']} fields compared; {data['source_summary_audit']['differing_fields']} differ under flag filtering or explicit missingness. This is sensitivity analysis, not proof that filtered scores are more accurate. All comparisons and stored numeric means are in JSON.", "",
                      "| Summary field | Source | Flag-filtered / missingness-aware | Explanation |", "|---|---:|---:|---|"])
        for item in data["source_summary_audit"]["comparisons"]:
            if not item["matches"]:
                reason = "unrun, not a zero score" if item["status"] == "unrun" else "flag-filtered sensitivity; ambiguous zero/failure classification, not a verified correction"
                lines.append(f"| {item['path']} | {item['reported']} | {item['recomputed']} | {reason} |")
    lines.extend(["", "## Reproduction", "", "From the repository root, with Python 3 and no external packages:", "", "```sh",
                  'python3 scripts/legacy_audit.py import --source "/path/to/original/8-19-run"',
                  "python3 scripts/legacy_audit.py verify",
                  "python3 scripts/legacy_audit.py audit", "```", "",
                  "Import is idempotent only for identical evidence and refuses changed files. Verify is read-only. Audit verifies the archive before writing deterministic reports; the dataset digest records the current metadata/ideal join input. Verification detects divergence from the local manifest, not authenticity against an independently trusted signature. Reports omit response and context text; originals require a separate rights/privacy review before public distribution.", ""])
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("import", "verify", "audit"):
        command = commands.add_parser(name)
        command.add_argument("--archive", type=Path, default=DEFAULT_ARCHIVE)
        if name == "import":
            command.add_argument("--source", type=Path, required=True, help="Original 8-19-run directory; never modified")
        elif name == "audit":
            command.add_argument("--dataset", type=Path, default=DEFAULT_DATASET)
            command.add_argument("--json-report", type=Path, default=REPO / "reports/legacy-audit.json")
            command.add_argument("--markdown-report", type=Path, default=REPO / "reports/legacy-audit.md")
            command.add_argument("--bootstrap-samples", type=int, default=10000)
            command.add_argument("--seed", type=int, default=20250830)
    args = parser.parse_args(argv)
    try:
        if args.command == "import":
            manifest = import_archive(args.source, args.archive)
            print(f"Preserved {len(manifest['files'])} original files ({sum(e['bytes'] for e in manifest['files'])} bytes); manifest: {args.archive / 'manifest.json'}")
        elif args.command == "verify":
            manifest = verify_archive(args.archive)
            print(f"Verified all {len(manifest['files'])} original files against SHA256 and byte counts (read-only)")
        else:
            destinations = (args.json_report.resolve(), args.markdown_report.resolve())
            protected = args.archive.resolve()
            if destinations[0] == destinations[1] or any(p == args.dataset.resolve() or p == protected or protected in p.parents for p in destinations):
                raise AuditError("Report paths must be distinct and outside the evidence archive and dataset")
            report = audit_archive(args.archive, args.dataset, args.bootstrap_samples, args.seed)
            for path in destinations:
                path.parent.mkdir(parents=True, exist_ok=True)
            destinations[0].write_bytes(json_bytes(report))
            destinations[1].write_text(render_markdown(report), encoding="utf-8")
            print(f"Audited {report['retained_record_n']} records in {len(report['runs'])} separate runs; wrote {args.json_report} and {args.markdown_report}")
    except (AuditError, OSError) as exc:
        parser.exit(2, f"error: {exc}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
