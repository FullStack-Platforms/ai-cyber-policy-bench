# Run the retrospective refresh

The new tools use only the Python standard library. They do not import the legacy retrieval/scoring engine, download embeddings, or require `uv sync`. Python 3.10+ is sufficient for these tools; the original application retains its separate dependency constraints.

## 1. Preserve and audit authorized local evidence

Run from the repository root:

```sh
python3 scripts/legacy_audit.py import --source "/path/to/original/8-19-run"
python3 scripts/legacy_audit.py verify
python3 scripts/legacy_audit.py audit
```

The six original JSON exports are copied byte-for-byte into `data/legacy/8-19-run/{root,11-chunks,67-chunks}/`. The source remains untouched. Re-import accepts identical files and can restore missing files from a manifest-only public checkout; it refuses to replace changed evidence. `verify` is read-only. Audit verifies the manifest before generating `reports/legacy-audit.json` and `reports/legacy-audit.md`.

The raw originals are ignored by Git because they contain third-party framework excerpts and unreviewed response content. The manifest and aggregate reports can be versioned. A fresh public checkout needs authorized originals to reproduce the audit/pilot; offline synthetic tests do not need them. See the [publication gate](release-and-teaching.md#publication-gate).

**Interpretation:** `raw_files` was not run. Judge failures/fallbacks are archive labels, not proven provider outages. The legacy scorer labels zero grades as failures; the audit preserves stored numeric means alongside flag-filtered sensitivity estimates. Do not advertise a higher filtered mean as corrected accuracy or model improvement.

## 2. Declare and inspect a small pilot

Review the [protocol and rubric](refresh-protocol.md) before choosing models. All 15 root-panel questions are used; default historical comparator is `openai/gpt-4o-mini`. Each explicit contemporary model requires 15 requests. Contemporary IDs are intentionally not hardcoded as “latest”; aliases and availability change.

```sh
# Assign an exact, available model ID after checking its current provider pricing.
MODEL_ID='provider/model-id'
python3 scripts/refresh_pilot.py plan --model "$MODEL_ID"

# Safe by default: prints a plan, makes zero API calls, writes no run directory.
python3 scripts/refresh_pilot.py run \
  --model "$MODEL_ID" --max-requests 15 --max-tokens 1024 \
  --output pilot-runs/current
```

The model string above is a shell example, not an endorsed or existing endpoint. Use `--model` twice and `--max-requests 30` for two selected models. The request ceiling is checked before key lookup or any network activity. Output tokens are bounded; this is **not a guaranteed dollar cap**. Set a provider-side spending limit and inspect reasoning-token billing. One call per question/model, no retries, no automatic substitutions.

## 3. Execute only after budget and reference-review decisions

Set `OPENROUTER_API_KEY` securely in the shell environment. Do not put it in a command argument or tracked file. After reviewing the plan and prices, explicitly opt in:

```sh
python3 scripts/refresh_pilot.py run \
  --model "$MODEL_ID" --max-requests 15 --max-tokens 1024 \
  --output pilot-runs/current --execute
```

The tool targets OpenRouter's HTTPS chat-completions endpoint, refuses redirects, and saves `plan.json` plus append-flushed `results.jsonl`. Existing output directories are never overwritten. Exact questions, reconstructed requests, archive hash, requested/returned model, timestamps, usage where returned, finish reason, and errors are retained. Blank content is failure, not a successful answer. Token-limit finishes retain their partial answer and are counted separately in comparison. API incompatibility, service errors, and interruptions may leave failed/missing generations; do not silently drop them or rerun until a desired answer appears.

Historical wire requests/provider revisions are unavailable. The reconstructed prompt and new token ceiling are documented in the plan. A dry run verifies planning, not live model availability or HTTP compatibility.

## 4. Blind review, using the same corrected references

```sh
python3 scripts/refresh_pilot.py review-packet \
  --run pilot-runs/current --output pilot-runs/review \
  --seed 2026 --rubric-version cyber-policy-human-v1
```

Share **only** `pilot-runs/review/review.csv` with the rater. Keep `identity-key.json`, the seed, and the run metadata away from the rater until review closes. There are 30 rows for one contemporary model, 45 for two: historical answers are not duplicated per comparison. Content/style can still leak identity; this is not guaranteed blinding.

For every question, review the historical answer key against authoritative versioned sources before scoring. In all rows for that question, set the same `reviewed_reference`, including the supporting URL/section and as-of date, and set `reference_reviewed=yes`. Do not change `historical_reference`. Record component rationales and corrections in `review_notes`.

Fill `score` in `[0,1]` using the weighted rubric, and `critical_error=yes/no`. Do not change question/response/identity fields or the rubric version. For failed/missing generations explicitly enter **0 task utility**; this is a prespecified service-outcome rule, not a competence claim. Mark substantive harmful claims separately; absent text is not itself a fabricated citation. **Blank ratings are unreviewed, never zero.** The tool requires acknowledgment of review but cannot certify domain expertise or source correctness.

## 5. Compare and publish only what was measured

```sh
python3 scripts/refresh_pilot.py compare \
  --ratings pilot-runs/review/review.csv \
  --key pilot-runs/review/identity-key.json \
  --output pilot-runs/comparison.json
```

Comparison rejects incomplete/invalid ratings, altered question/response identities, mismatched references, and incompatible rubric versions. For each contemporary model it reports full-panel task-utility means, paired change, a deterministic question-bootstrap interval, critical-error counts, failed/missing generations, token-limit finishes, and per-question changes. Divide critical-error counts by the stated panel denominator if reporting rates; also disclose how many responses were actually delivered.

These are selected-panel, one-generation-per-item descriptive results, not a causal measure of model progress or student learning. Do not pool the model contrasts as independent evidence. A paper-grade study needs independent review and broader validity work described in the protocol.

## Offline regression tests

```sh
python3 -m unittest discover -s tests -p 'test_*.py' -v
```

Tests use isolated synthetic fixtures, not live provider requests or fabricated benchmark evidence. The new CI job runs them without installing the legacy ML dependencies. The unchanged legacy `test_scoring.py` is a separate demonstration script, not part of this offline suite.

## Verification performed for this refresh

- Python 3.15.0: all 29 offline behavioral tests passed. CI's Python 3.11 job was added but has not been run remotely here.
- Six copied files matched their original source bytes (21,704,602 bytes total); the read-only checksum verification passed.
- The real archive audit processed all 710 records and produced the checked-in aggregate reports.
- Actual CLI planning/dry-run used the archived 15-question panel; 15 requests against a ceiling of 14 were refused before execution.
- The review and comparison CLIs were exercised with a temporary **archived-response replay fixture**, not contemporary model outputs: 30 review rows, rejection of unreviewed ratings, and recovery of the known zero paired delta across 15 items. The fixture was removed and is not research evidence.
- Ruff passed for both new scripts and both test files. Local documentation links resolved; the standalone X draft is 261 characters.
- No paid model requests, live provider compatibility checks, contemporary benchmark results, or classroom intervention were performed. The unchanged legacy ML application was not smoke-tested.

When opening review CSVs in spreadsheet software, import response/reference columns as text rather than executable formulas; model-generated text is untrusted.
