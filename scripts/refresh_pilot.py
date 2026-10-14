#!/usr/bin/env python3
"""Small stdlib-only, no-context retrospective pilot; see --help for contracts."""

import argparse
import csv
import hashlib
import json
import math
import os
import random
import statistics
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib import error, request

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ARCHIVE = ROOT / "data/legacy/8-19-run/root/detailed_results.json"
DEFAULT_DATASET = ROOT / "data/prompts/cyber_evals.jsonl"
ENDPOINT = "https://openrouter.ai/api/v1/chat/completions"
SCHEMA = "refresh-pilot-v1"
PANEL_SIZE = 15
WARNING = (
    "Historical ideal answers require expert review; they are not authoritative. "
    "Use one reviewed reference and rubric for both arms. Model identity may leak "
    "through response content despite shuffled labels. Do not share the identity key "
    "with reviewers. Historical judge scores are never used."
)
FIELDS = [
    "review_id", "question_id", "question", "historical_reference", "response",
    "generation_status", "rubric_version", "reviewed_reference", "reference_reviewed",
    "score", "critical_error", "review_notes",
]
IMMUTABLE = FIELDS[:6]


def digest(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def load_json(path):
    with Path(path).open(encoding="utf-8") as handle:
        return json.load(handle)


def save_json(path, value):
    # Exclusive creation: neither runs nor analysis artifacts are silently replaced.
    with Path(path).open("x", encoding="utf-8") as handle:
        json.dump(value, handle, ensure_ascii=False, indent=2, allow_nan=False)
        handle.write("\n")


def reconstructed_request(model, question, max_tokens):
    return {
        "model": model,
        "messages": [{
            "role": "user",
            "content": f"Question: {question}\n\nPlease provide a precise answer based on your knowledge of cybersecurity frameworks and compliance requirements.",
        }],
        "temperature": 0.1,
        "max_tokens": max_tokens,
    }


def legacy_failure(response):
    return not response.strip() or response.startswith(("MODEL_FAILURE:", "TASK_FAILURE:"))


def build_plan(archive=DEFAULT_ARCHIVE, dataset=DEFAULT_DATASET,
               baseline_model="openai/gpt-4o-mini", models=(), max_tokens=1024):
    if not 1 <= max_tokens <= 4096:
        raise ValueError("max-tokens must be between 1 and 4096")
    models = list(models)
    if len(set(models)) != len(models):
        raise ValueError("Duplicate model IDs would create pseudoreplication")
    if any(not model.strip() or model != model.strip() for model in models):
        raise ValueError("Supply exact nonempty model IDs, without surrounding whitespace")
    raw = Path(archive).read_bytes()
    exports = json.loads(raw)
    if not isinstance(exports, dict) or baseline_model not in exports:
        raise ValueError(f"Historical baseline model not found: {baseline_model}")
    metadata = {}
    if dataset is not None:
        with Path(dataset).open(encoding="utf-8") as handle:
            for line in handle:
                if line.strip():
                    row = json.loads(line)
                    question = row.get("input")
                    if question in metadata:
                        raise ValueError("Duplicate exact question in metadata dataset")
                    metadata[question] = {
                        "id": row.get("id"), "question_id": row.get("question_id"),
                        "metadata": row.get("metadata", {}),
                    }
    selected = {}
    for row in exports[baseline_model]:
        if row.get("evaluation_mode") != "no_context":
            continue
        question = row["question"]
        reference = row["ideal_answer"]
        response = row["model_response"]
        if not all(isinstance(value, str) for value in (question, reference, response)):
            raise ValueError("Historical question, reference, and response must be strings")
        if not question or row.get("model_name") != baseline_model:
            raise ValueError("Historical question/model identity is inconsistent")
        qid = digest(question)
        if qid in selected:
            raise ValueError("Duplicate historical no-context question for baseline")
        selected[qid] = {
            "question_id": qid, "question": question, "historical_reference": reference,
            "dataset_exact_match": question in metadata,
            "dataset_metadata": metadata.get(question),
            "legacy": {
                "requested_model": baseline_model, "actual_model": None,
                "response": response, "timestamp": row.get("timestamp"),
                "generation_failed": legacy_failure(response),
                "error": response if legacy_failure(response) else None,
                "source_run": "root", "source_mode": "no_context",
                "reconstructed_request": {
                    key: value for key, value in reconstructed_request(baseline_model, question, max_tokens).items()
                    if key != "max_tokens"
                },
            },
        }
    if len(selected) != PANEL_SIZE:
        raise ValueError(f"Expected the complete {PANEL_SIZE}-question root panel; found {len(selected)}")
    return {
        "schema": SCHEMA, "mode": "no_context", "baseline_model": baseline_model,
        "archive": Path(archive).name, "archive_sha256": hashlib.sha256(raw).hexdigest(),
        "dataset": Path(dataset).name if dataset is not None else None,
        "models": models, "question_count": len(selected),
        "request_count": len(selected) * len(models), "requests_per_model": len(selected),
        "max_tokens": max_tokens, "maximum_output_tokens": len(selected) * len(models) * max_tokens,
        "cost_note": "A request/token ceiling is not a dollar budget; verify provider prices before executing.",
        "warning": WARNING,
        "request_provenance": {
            "reconstruction_source": "src/evaluator.py:create_prompt and query_model (current checkout, not an archived wire request)",
            "historical_reconstruction": "One user message, exact no-context prompt, temperature 0.1; no system message.",
            "differences": [
                "Explicit max_tokens bound added; historical evaluator set no output-token bound.",
                "One attempt per question/model, sequential; historical evaluator allowed retries and concurrency.",
                "Direct OpenRouter HTTPS request; no discovery or alternate model selection by this script.",
                "Exact returned content retained; historical evaluator stripped surrounding whitespace.",
            ],
            "unknowns": [
                "Archived wire requests, historical checkout/configuration, full parameters and provider defaults unavailable.",
                "Historical actual returned model/provider, usage, finish reason, and retry history unavailable.",
                "Exact IDs may be provider aliases, not pinned weights; actual returned model is recorded when supplied.",
            ],
        },
        "questions": [selected[qid] for qid in sorted(selected)],
        "requests": [
            {"question_id": qid, "request": reconstructed_request(model, selected[qid]["question"], max_tokens)}
            for model in models for qid in sorted(selected)
        ],
    }


class NoRedirect(request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None  # Never forward the Authorization header to another endpoint.


def redact(value, secret):
    if isinstance(value, str):
        return value.replace(secret, "[REDACTED]") if secret else value
    if isinstance(value, dict):
        return {redact(key, secret): redact(item, secret) for key, item in value.items()}
    if isinstance(value, list):
        return [redact(item, secret) for item in value]
    return value


def call_openrouter(payload, api_key):
    """Exactly one network request; no retries, model discovery, or fallback calls."""
    result = {
        "timestamp": utc_now(), "actual_model": None, "response": "", "usage": None,
        "finish_reason": None, "provider_created": None, "response_id": None,
        "generation_failed": True, "error": None,
    }
    req = request.Request(
        ENDPOINT, data=json.dumps(payload).encode("utf-8"), method="POST",
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
    )
    try:
        with request.build_opener(NoRedirect()).open(req, timeout=120) as handle:
            body = json.load(handle)
        if not isinstance(body, dict):
            raise TypeError("Provider response is not a JSON object")
        result.update({
            "actual_model": body.get("model"), "usage": body.get("usage"),
            "provider_created": body.get("created"), "response_id": body.get("id"),
        })
        if body.get("error"):
            result["error"] = {"type": "provider_error", "details": body["error"]}
        else:
            choice = body["choices"][0]
            result["finish_reason"] = choice.get("finish_reason")
            content = choice["message"].get("content")
            if isinstance(content, str):
                result["response"] = content
            if not isinstance(content, str) or not content.strip():
                result["error"] = {"type": "empty_response", "message": "No nonempty text content returned"}
            elif choice.get("error") or result["finish_reason"] == "error":
                result["error"] = {"type": "generation_error", "details": choice.get("error")}
            else:
                result["generation_failed"] = False
    except error.HTTPError as exc:
        result["error"] = {
            "type": "http_error", "status": exc.code,
            "message": exc.read(16384).decode("utf-8", errors="replace"),
        }
    except (error.URLError, OSError, ValueError, KeyError, IndexError, TypeError, AttributeError) as exc:
        result["error"] = {"type": type(exc).__name__, "message": str(exc)}
    return redact(result, api_key)


def execute_run(plan, output, max_requests, execute=False, caller=None):
    # All budget checks precede key lookup, filesystem changes and any network call.
    if not plan["models"]:
        raise ValueError("run requires at least one explicit --model ID")
    if max_requests is None or max_requests < 1:
        raise ValueError("run requires a positive explicit --max-requests ceiling")
    count = len(plan["requests"])
    if count > max_requests:
        raise ValueError(f"Request ceiling exceeded: {count} planned > {max_requests}; no calls made")
    if not execute:
        return {"dry_run": True, "network_calls": 0, "max_requests": max_requests, "plan": plan}
    api_key = os.environ.get("OPENROUTER_API_KEY", "").strip()
    if not api_key:
        raise ValueError("Set OPENROUTER_API_KEY in the environment; never pass it on the command line")
    # Prevent even accidentally supplied secret strings in model IDs or source text being persisted.
    if api_key in json.dumps(plan, ensure_ascii=False):
        raise ValueError("Secret value appears in run inputs; refusing to persist them")
    output = Path(output)
    output.mkdir(parents=True, exist_ok=False)
    save_json(output / "plan.json", dict(plan, execution_started=utc_now(), max_requests=max_requests))
    caller = caller or call_openrouter
    with (output / "results.jsonl").open("x", encoding="utf-8") as handle:
        for item in plan["requests"]:
            result = caller(item["request"], api_key)
            record = dict(result, question_id=item["question_id"], requested_model=item["request"]["model"],
                          requested_parameters=item["request"])
            handle.write(json.dumps(redact(record, api_key), ensure_ascii=False, allow_nan=False) + "\n")
            handle.flush()  # A later interruption does not discard completed responses.
    return {"dry_run": False, "requests_attempted": count, "run": str(output)}


def load_run(run):
    run = Path(run)
    plan = load_json(run / "plan.json")
    if plan.get("schema") != SCHEMA or plan.get("mode") != "no_context":
        raise ValueError("Unsupported run schema or mode")
    if not plan.get("models") or len(set(plan["models"])) != len(plan["models"]):
        raise ValueError("Run must have unique explicit model IDs")
    questions = plan["questions"]
    qids = {q["question_id"] for q in questions}
    if len(questions) != PANEL_SIZE or len(qids) != PANEL_SIZE:
        raise ValueError("Run must retain the full unique 15-question root panel")
    if any(digest(q["question"]) != q["question_id"] for q in questions):
        raise ValueError("Run question identity does not match its exact text")
    expected = {(model, qid) for model in plan["models"] for qid in qids}
    results = {}
    path = run / "results.jsonl"
    if path.exists():
        with path.open(encoding="utf-8") as handle:
            for line in handle:
                if not line.strip():
                    continue
                row = json.loads(line)
                pair = (row["requested_model"], row["question_id"])
                if pair not in expected or pair in results:
                    raise ValueError("Unexpected or duplicate model/question result")
                expected_request = reconstructed_request(pair[0], next(q["question"] for q in questions if q["question_id"] == pair[1]), plan["max_tokens"])
                if row.get("requested_parameters") != expected_request:
                    raise ValueError("Saved request does not match the paired question/model")
                results[pair] = row
    return plan, results


def make_review_packet(run, output, seed, rubric_version):
    if not rubric_version.strip():
        raise ValueError("A nonempty reviewed rubric version is required")
    plan, results = load_run(run)
    entries = []
    for question in plan["questions"]:
        qid = question["question_id"]
        arms = [("legacy", plan["baseline_model"], question["legacy"])]
        arms.extend(("modern", model, results.get((model, qid))) for model in plan["models"])
        for arm, model, result in arms:
            status = "missing" if result is None else "failed" if result["generation_failed"] else "ok"
            row = {
                "question_id": qid, "question": question["question"],
                "historical_reference": question["historical_reference"],
                "response": result["response"] if result is not None else "",
                "generation_status": status, "rubric_version": rubric_version,
                "reviewed_reference": question["historical_reference"],
                "reference_reviewed": "", "score": "", "critical_error": "", "review_notes": "",
            }
            entries.append((row, {"arm": arm, "model": model,
                                  "finish_reason": result.get("finish_reason") if result else None}))
    random.Random(seed).shuffle(entries)
    identities = []
    for index, (row, identity) in enumerate(entries, 1):
        row["review_id"] = f"R{index:04d}"
        identities.append(dict(identity, **{field: row[field] for field in IMMUTABLE}))
    output = Path(output)
    output.mkdir(parents=True, exist_ok=False)
    key = {
        "schema": SCHEMA, "seed": seed, "rubric_version": rubric_version,
        "baseline_model": plan["baseline_model"], "models": plan["models"],
        "archive_sha256": plan["archive_sha256"], "source_run": Path(run).name,
        "question_ids": [q["question_id"] for q in plan["questions"]],
        "warning": WARNING, "entries": identities,
    }
    save_json(output / "identity-key.json", key)
    with (output / "review.csv").open("x", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(row for row, _ in entries)
    return {"ratings": str(output / "review.csv"), "private_key": str(output / "identity-key.json"),
            "rows": len(entries), "warning": WARNING,
            "instructions": "Expert-review/correct reviewed_reference identically for all rows of each question; set reference_reviewed=yes. Rate every outcome for full-panel task utility (0..1); explicitly enter 0 for failed/missing generations, not for unreviewed answers. Set critical_error=yes/no for substantive harmful claims (no for absent text). Do not alter identity, question, historical_reference, response, generation_status, or rubric_version. Blank scores are not zero."}


def bootstrap_interval(differences, seed, samples):
    rng = random.Random(seed)
    n = len(differences)
    means = sorted(sum(differences[rng.randrange(n)] for _ in range(n)) / n for _ in range(samples))
    def percentile(p):
        position = (samples - 1) * p
        lower = int(position)
        upper = min(lower + 1, samples - 1)
        return means[lower] + (means[upper] - means[lower]) * (position - lower)
    return [percentile(0.025), percentile(0.975)]


def compare_ratings(ratings_path, key_path, seed=2026, samples=10000):
    if not 100 <= samples <= 100000:
        raise ValueError("bootstrap-samples must be between 100 and 100000")
    key = load_json(key_path)
    if key.get("schema") != SCHEMA or not key.get("rubric_version"):
        raise ValueError("Unsupported key schema or missing rubric version")
    qids = key["question_ids"]
    models = key["models"]
    if len(qids) != PANEL_SIZE or len(set(qids)) != PANEL_SIZE or not models or len(set(models)) != len(models):
        raise ValueError("Key must contain the complete unique panel and unique models")
    identities = {entry["review_id"]: entry for entry in key["entries"]}
    if len(identities) != len(key["entries"]):
        raise ValueError("Duplicate review identities in key")
    expected = {("legacy", key["baseline_model"], qid) for qid in qids}
    expected.update(("modern", model, qid) for model in models for qid in qids)
    actual = {(entry["arm"], entry["model"], entry["question_id"]) for entry in identities.values()}
    if actual != expected or len(actual) != len(identities):
        raise ValueError("Key does not contain exactly one legacy and each modern response per question")
    with Path(ratings_path).open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames != FIELDS:
            raise ValueError("Review CSV columns do not match the packet contract")
        rows = list(reader)
    seen, paired, references = set(), {}, {}
    for row in rows:
        rid = row["review_id"]
        if rid in seen or rid not in identities:
            raise ValueError(f"Duplicate or unexpected review ID: {rid}")
        seen.add(rid)
        entry = identities[rid]
        if any(row[field] != entry[field] for field in IMMUTABLE):
            raise ValueError(f"Exact question/response identity changed for {rid}")
        if digest(row["question"]) != row["question_id"]:
            raise ValueError(f"Question hash mismatch for {rid}")
        if row["rubric_version"] != key["rubric_version"]:
            raise ValueError(f"Incompatible rubric version for {rid}")
        if row["reference_reviewed"].strip().lower() != "yes" or not row["reviewed_reference"].strip():
            raise ValueError(f"Expert reference review is incomplete for {rid}")
        qid = row["question_id"]
        reference = (row["question"], row["historical_reference"], row["reviewed_reference"])
        if qid in references and references[qid] != reference:
            raise ValueError(f"Paired question/reference differs for {qid}")
        references[qid] = reference
        try:
            score = float(row["score"])
        except (TypeError, ValueError):
            raise ValueError(f"Missing or invalid numeric score for {rid}; no comparison produced") from None
        if not math.isfinite(score) or not 0 <= score <= 1:
            raise ValueError(f"Score must be finite and in [0, 1] for {rid}")
        critical = row["critical_error"].strip().lower()
        if critical not in ("yes", "no"):
            raise ValueError(f"critical_error must be yes or no for {rid}")
        if row["generation_status"] not in ("ok", "failed", "missing"):
            raise ValueError(f"Invalid generation status for {rid}")
        if row["generation_status"] != "ok" and score != 0:
            raise ValueError(f"Failed/missing generation requires explicit zero task utility for {rid}")
        if row["generation_status"] == "ok" and not row["response"].strip():
            raise ValueError(f"Successful generation has no response for {rid}")
        paired[(entry["arm"], entry["model"], qid)] = dict(row, score=score, critical_error=critical)
    missing = set(identities) - seen
    if missing:
        raise ValueError(f"Incomplete paired ratings: {len(missing)} missing rows; no comparison produced")
    summaries = []
    for model in models:
        legacy = [paired[("legacy", key["baseline_model"], qid)] for qid in sorted(qids)]
        modern = [paired[("modern", model, qid)] for qid in sorted(qids)]
        differences = [new["score"] - old["score"] for old, new in zip(legacy, modern)]
        def counts(arm):
            return {"generation_failures": sum(row["generation_status"] == "failed" for row in arm),
                    "missing_generations": sum(row["generation_status"] == "missing" for row in arm),
                    "missing_ratings": 0, "critical_errors": sum(row["critical_error"] == "yes" for row in arm)}
        summaries.append({
            "modern_model": model, "legacy_model": key["baseline_model"], "n": len(differences),
            "legacy": dict(counts(legacy), mean_score=statistics.fmean(row["score"] for row in legacy)),
            "modern": dict(counts(modern), mean_score=statistics.fmean(row["score"] for row in modern)),
            "modern_length_finish_reasons": sum(entry["arm"] == "modern" and entry["model"] == model and entry.get("finish_reason") == "length" for entry in identities.values()),
            "mean_paired_difference": statistics.fmean(differences),
            "bootstrap_95_percent_interval": bootstrap_interval(differences, seed, samples),
            "per_question": [{"question_id": qid, "modern_minus_legacy": diff}
                             for qid, diff in zip(sorted(qids), differences)],
        })
    return {
        "schema": SCHEMA, "rubric_version": key["rubric_version"],
        "estimand": "Full-panel task utility: failed/missing generations explicitly rated zero; not conditional answer accuracy or subject-matter competence.",
        "archive_sha256": key["archive_sha256"], "seed": seed, "bootstrap_samples": samples,
        "method": "Paired per-question percentile bootstrap (2.5%, 97.5%); linear quantiles; full panel, no complete-case exclusions. One comparison per requested modern model; baseline ratings reused, never pooled as independent observations.",
        "limitations": "Small selected historical panel, not a population sample; interval is descriptive, not evidence of teaching benefit. No multiplicity correction. Failed/missing generations require explicit zero task utility, never implicit zero-fill of missing ratings. All models share questions/baseline and are not independent experiments.",
        "warning": WARNING, "comparisons": summaries,
    }


def parser():
    command = argparse.ArgumentParser(description=__doc__, epilog=WARNING)
    sub = command.add_subparsers(dest="command", required=True)
    for name, help_text in (("plan", "Offline plan for the full deterministic root 15-question panel"),
                            ("run", "Dry-run by default; --execute alone opts into paid OpenRouter calls")):
        item = sub.add_parser(name, help=help_text, description=help_text)
        item.add_argument("--archive", type=Path, default=DEFAULT_ARCHIVE, help="Copied root detailed_results.json")
        item.add_argument("--dataset", type=Path, default=DEFAULT_DATASET, help="Current JSONL for exact-text metadata only, never replacement references")
        item.add_argument("--baseline-model", default="openai/gpt-4o-mini", help="Explicit historical baseline ID (default: openai/gpt-4o-mini)")
        item.add_argument("--model", action="append", default=[], required=name == "run", help="Exact modern model ID; repeat for multiple models; no discovery")
        item.add_argument("--max-tokens", type=int, default=1024, help="Output-token ceiling per request, 1..4096 (default: 1024)")
        item.add_argument("--output", type=Path, required=name == "run", help="New JSON file for plan, or new run directory; never overwritten")
        if name == "run":
            item.add_argument("--max-requests", type=int, required=True, help="Explicit request ceiling, checked before any call; 15 per model")
            item.add_argument("--execute", action="store_true", help="Actually call fixed OpenRouter endpoint using OPENROUTER_API_KEY; sequential, no retries; dry-run otherwise writes nothing")
    review = sub.add_parser("review-packet", help="Offline shuffled blind CSV plus separate private identity key", epilog=WARNING)
    review.add_argument("--run", type=Path, required=True, help="Saved executed run directory (interrupted runs retain missingness)")
    review.add_argument("--output", type=Path, required=True, help="New directory for review.csv and identity-key.json; share CSV only")
    review.add_argument("--seed", type=int, required=True, help="Reproducible shuffle seed")
    review.add_argument("--rubric-version", required=True, help="Version of the common expert-reviewed human rubric; no historical scores")
    compare = sub.add_parser("compare", help="Offline paired analysis; rejects incomplete/invalid human ratings", epilog=WARNING)
    compare.add_argument("--ratings", type=Path, required=True, help="Completed review.csv: all scores 0..1, critical_error yes/no, reference_reviewed yes")
    compare.add_argument("--key", type=Path, required=True, help="Separate identity-key.json from the same packet")
    compare.add_argument("--seed", type=int, default=2026, help="Per-question bootstrap seed (default: 2026)")
    compare.add_argument("--bootstrap-samples", type=int, default=10000, help="100..100000 resamples (default: 10000)")
    compare.add_argument("--output", type=Path, help="New comparison JSON; otherwise print to stdout")
    return command


def main(argv=None):
    args = parser().parse_args(argv)
    try:
        if args.command in ("plan", "run"):
            plan = build_plan(args.archive, args.dataset, args.baseline_model, args.model, args.max_tokens)
            result = plan if args.command == "plan" else execute_run(plan, args.output, args.max_requests, args.execute)
        elif args.command == "review-packet":
            result = make_review_packet(args.run, args.output, args.seed, args.rubric_version)
        else:
            result = compare_ratings(args.ratings, args.key, args.seed, args.bootstrap_samples)
        if args.command in ("plan", "compare") and args.output:
            save_json(args.output, result)
        else:
            print(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False))
        return 0
    except (ValueError, OSError, KeyError, TypeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
