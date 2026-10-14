# Preserved legacy export audit

Retained **710 records in 3 separate runs**. Six originals are byte-preserved and checked against the manifest before analysis. No cross-run leaderboard is produced.

## Interpretation and limits

- **score:** archived accuracy_score, finite numeric [0,1], excluding explicit both-judge failures and generation failures; genuine zero retained
- **attempted records:** stored rows, not provider request/retry counts
- **single fallback:** included when otherwise valid, also reported separately; not dual agreement
- **unrun:** no stored records: mean null, not zero
- **question join:** SHA256(exact UTF-8 question), additionally checked for exact text equality
- **pairing:** within run/model, exact-question intersection with valid scores in both modes; all duplicate question/mode keys excluded
- **scope:** three separate export groups, no cross-run pooled leaderboard or temporal/causal interpretation
- **uncertainty:** question-level percentile bootstrap, fixed seed and sorted question hashes; fixed-panel descriptive uncertainty, not model/judge run-to-run variance
- **provenance:** July 26 2025 authorship is user recollection, not established by these exports; directory 8-19-run is a source label, not a date claim
- **failure caveat:** Failure/fallback counts describe archive flags, not confirmed provider failures. Current legacy scorer accepts judge results only when accuracy_score > 0 (src/scorer.py:dual_llm_judge_score). The two both-failed records contain substantive explanations justifying zero. Excluding their zeros is a flag-filtered sensitivity analysis, not an established correction; compare recorded_numeric_mean. Lost judge scores cannot be reconstructed reliably.
- **Unknown:** actual judge model identifiers and revisions; historical request parameters and provider revisions; token usage and cost; request latency and retry counts; timestamp timezone; independence of collection processes across export groups.

## Evidence manifest

Source labels are relative to the supplied original directory; no absolute machine paths are recorded.

| Preserved file | Original relative source | Bytes | SHA256 |
|---|---|---:|---|
| 11-chunks/detailed_results.json | 11-chunks/experiment_results/detailed_results.json | 3471675 | `7655b106bb58e1187903ddc8158002650e4730a890eb089e4fe1e51b1ce130d6` |
| 11-chunks/summary.json | 11-chunks/experiment_results/summary.json | 2100 | `1c16fbf46fa51f34029bda670d5dcf1e62fab338880eb88b75d6d48a7f8fb8e7` |
| 67-chunks/detailed_results.json | 67-chunks/experiment_results/detailed_results.json | 14341405 | `22ec1d80a26d3362476801bdc25a80ee560a7a2656fa25de20d1ae54fc3825ba` |
| 67-chunks/summary.json | 67-chunks/experiment_results/summary.json | 2139 | `9d10cc6871dee03dd5a6293a1357b2a13ed358e190648256cfb05f0bc2e0be79` |
| root/detailed_results.json | experiment_results/detailed_results.json | 3885615 | `299fd6d07855b51820947f8a7e206473e4def357299b386951d931345637a5b6` |
| root/summary.json | experiment_results/summary.json | 1668 | `c4d825bd6e975692c5ccdb95a94b8b727bf5b962d3c45219f4120ea2eb8a6a68` |

## Current dataset join

Dataset `cyber_evals.jsonl`: 101 rows; SHA256 `088a7f3cafbc160665482047eda24eb2f31042b5a4ff22be25759d25f94be5c5`.
Archived unique questions: 20; exact matches: 20; ambiguous: 0; unmatched: 0; questions with metadata: 20.
Archived/current ideal text mismatches: 0 records / 0 questions (not a quality verdict).
Current dataset duplicate question hashes: 0.
Metadata field coverage (unique archived questions): category=20, created_at=20, difficulty=20, framework=20, question_type=20, sector=4, technology=5, version=20.

## Run: root

150 retained rows; 5 model labels; 15 unique questions. Duplicate model/mode/question keys: 0; model-label mismatches: 0.
Record timestamps: `2025-08-29T19:26:18.321906` through `2025-08-29T19:57:26.360158`; source summary timestamp `2025-08-29T20:14:48.454288`. Missing/invalid timestamps: 0; repeated timestamp values: 0. Timezone unknown.
Valid-score n=150; generation failures=0; missing scores=0; invalid numeric scores=0; dual=150; single fallback=0; both failed=0; unknown judge status=0.
Stored numeric mean (including failure-labelled zeros)=0.776167; flag-filtered mean=0.776167. Neither is newly verified accuracy; do not call the difference model improvement.

### Model/mode descriptive scores

Means include eligible single fallbacks; dual-only and fallback-only means are shown independently. Unrun modes have no score. Model rows are alphabetic, not ranked.

| Model | Mode | Attempted | Valid n | Mean | Dual-only mean (n) | Fallback-only mean (n) | Generation failed | Missing / invalid | Both judges failed |
|---|---|---:|---:|---:|---|---|---:|---:|---:|
| deepseek/deepseek-chat-v3.1 | no_context | 15 | 15 | 0.870000 | 0.870000 (15) | unavailable (0) | 0 | 0 / 0 | 0 |
| deepseek/deepseek-chat-v3.1 | raw_files | 0 | 0 | unrun | unavailable (0) | unavailable (0) | 0 | 0 / 0 | 0 |
| deepseek/deepseek-chat-v3.1 | vector_db | 15 | 15 | 0.696667 | 0.696667 (15) | unavailable (0) | 0 | 0 / 0 | 0 |
| google/gemini-2.5-flash | no_context | 15 | 15 | 0.845000 | 0.845000 (15) | unavailable (0) | 0 | 0 / 0 | 0 |
| google/gemini-2.5-flash | raw_files | 0 | 0 | unrun | unavailable (0) | unavailable (0) | 0 | 0 / 0 | 0 |
| google/gemini-2.5-flash | vector_db | 15 | 15 | 0.660000 | 0.660000 (15) | unavailable (0) | 0 | 0 / 0 | 0 |
| google/gemini-2.5-flash-lite | no_context | 15 | 15 | 0.755000 | 0.755000 (15) | unavailable (0) | 0 | 0 / 0 | 0 |
| google/gemini-2.5-flash-lite | raw_files | 0 | 0 | unrun | unavailable (0) | unavailable (0) | 0 | 0 / 0 | 0 |
| google/gemini-2.5-flash-lite | vector_db | 15 | 15 | 0.668333 | 0.668333 (15) | unavailable (0) | 0 | 0 / 0 | 0 |
| gpt-5-mini | no_context | 15 | 15 | 0.878333 | 0.878333 (15) | unavailable (0) | 0 | 0 / 0 | 0 |
| gpt-5-mini | raw_files | 0 | 0 | unrun | unavailable (0) | unavailable (0) | 0 | 0 / 0 | 0 |
| gpt-5-mini | vector_db | 15 | 15 | 0.893333 | 0.893333 (15) | unavailable (0) | 0 | 0 / 0 | 0 |
| openai/gpt-4o-mini | no_context | 15 | 15 | 0.766667 | 0.766667 (15) | unavailable (0) | 0 | 0 / 0 | 0 |
| openai/gpt-4o-mini | raw_files | 0 | 0 | unrun | unavailable (0) | unavailable (0) | 0 | 0 / 0 | 0 |
| openai/gpt-4o-mini | vector_db | 15 | 15 | 0.728333 | 0.728333 (15) | unavailable (0) | 0 | 0 / 0 | 0 |

### Genuine dual-judge agreement

n=150; mean absolute judge-score difference=0.048333; exact agreement=62/150; absolute difference ≤0.10=138/150. Failed/single judgments do not enter this denominator. Per-model/mode agreement is in the JSON report.

### Paired vector-minus-no-context deltas

Only valid, uniquely keyed question intersections within this run/model. Descriptive, not temporal improvement or a causal retrieval effect; fixed-panel bootstrap intervals do not measure all sources of uncertainty.

| Model | Paired n | No-context mean | Vector mean | Mean delta | Question-bootstrap 95% interval | Pairs with fallback | Excluded questions |
|---|---:|---:|---:|---:|---|---:|---:|
| deepseek/deepseek-chat-v3.1 | 15 | 0.870000 | 0.696667 | -0.173333 | [-0.288333, -0.075000] | 0 | 0 |
| google/gemini-2.5-flash | 15 | 0.845000 | 0.660000 | -0.185000 | [-0.278333, -0.096667] | 0 | 0 |
| google/gemini-2.5-flash-lite | 15 | 0.755000 | 0.668333 | -0.086667 | [-0.165000, -0.010000] | 0 | 0 |
| gpt-5-mini | 15 | 0.878333 | 0.893333 | 0.015000 | [-0.011667, 0.051667] | 0 | 0 |
| openai/gpt-4o-mini | 15 | 0.766667 | 0.728333 | -0.038333 | [-0.095000, 0.020000] | 0 | 0 |

Bootstrap: 10000 resamples per model, seed 20250830, paired-question resampling with replacement and interpolated percentile endpoints.

### Source summary reconciliation

31 fields compared; 6 differ under flag filtering or explicit missingness. This is sensitivity analysis, not proof that filtered scores are more accurate. All comparisons and stored numeric means are in JSON.

| Summary field | Source | Flag-filtered / missingness-aware | Explanation |
|---|---:|---:|---|
| models.deepseek/deepseek-chat-v3.1.score_by_mode.raw_files | 0.0 | None | unrun, not a zero score |
| models.google/gemini-2.5-flash.score_by_mode.raw_files | 0.0 | None | unrun, not a zero score |
| models.google/gemini-2.5-flash-lite.score_by_mode.raw_files | 0.0 | None | unrun, not a zero score |
| models.gpt-5-mini.score_by_mode.raw_files | 0.0 | None | unrun, not a zero score |
| models.openai/gpt-4o-mini.score_by_mode.raw_files | 0.0 | None | unrun, not a zero score |
| mode_performance.raw_files | 0.0 | None | unrun, not a zero score |

## Run: 11-chunks

280 retained rows; 7 model labels; 20 unique questions. Duplicate model/mode/question keys: 0; model-label mismatches: 0.
Record timestamps: `2025-08-29T21:32:27.038875` through `2025-08-29T22:34:57.981624`; source summary timestamp `2025-08-29T23:06:42.861688`. Missing/invalid timestamps: 0; repeated timestamp values: 0. Timezone unknown.
Valid-score n=278; generation failures=0; missing scores=0; invalid numeric scores=0; dual=275; single fallback=3; both failed=2; unknown judge status=0.
Stored numeric mean (including failure-labelled zeros)=0.753839; flag-filtered mean=0.759263. Neither is newly verified accuracy; do not call the difference model improvement.

### Model/mode descriptive scores

Means include eligible single fallbacks; dual-only and fallback-only means are shown independently. Unrun modes have no score. Model rows are alphabetic, not ranked.

| Model | Mode | Attempted | Valid n | Mean | Dual-only mean (n) | Fallback-only mean (n) | Generation failed | Missing / invalid | Both judges failed |
|---|---|---:|---:|---:|---|---|---:|---:|---:|
| deepseek/deepseek-chat-v3.1 | no_context | 20 | 20 | 0.870000 | 0.870000 (20) | unavailable (0) | 0 | 0 / 0 | 0 |
| deepseek/deepseek-chat-v3.1 | raw_files | 0 | 0 | unrun | unavailable (0) | unavailable (0) | 0 | 0 / 0 | 0 |
| deepseek/deepseek-chat-v3.1 | vector_db | 20 | 20 | 0.635000 | 0.635000 (20) | unavailable (0) | 0 | 0 / 0 | 0 |
| google/gemini-2.5-flash | no_context | 20 | 20 | 0.833750 | 0.833750 (20) | unavailable (0) | 0 | 0 / 0 | 0 |
| google/gemini-2.5-flash | raw_files | 0 | 0 | unrun | unavailable (0) | unavailable (0) | 0 | 0 / 0 | 0 |
| google/gemini-2.5-flash | vector_db | 20 | 19 | 0.605263 | 0.627778 (18) | 0.200000 (1) | 0 | 0 / 0 | 1 |
| google/gemini-2.5-flash-lite | no_context | 20 | 20 | 0.798750 | 0.798750 (20) | unavailable (0) | 0 | 0 / 0 | 0 |
| google/gemini-2.5-flash-lite | raw_files | 0 | 0 | unrun | unavailable (0) | unavailable (0) | 0 | 0 / 0 | 0 |
| google/gemini-2.5-flash-lite | vector_db | 20 | 19 | 0.628947 | 0.628947 (19) | unavailable (0) | 0 | 0 / 0 | 1 |
| gpt-5-mini | no_context | 20 | 20 | 0.896250 | 0.896250 (20) | unavailable (0) | 0 | 0 / 0 | 0 |
| gpt-5-mini | raw_files | 0 | 0 | unrun | unavailable (0) | unavailable (0) | 0 | 0 / 0 | 0 |
| gpt-5-mini | vector_db | 20 | 20 | 0.868750 | 0.868750 (20) | unavailable (0) | 0 | 0 / 0 | 0 |
| mistralai/mistral-nemo | no_context | 20 | 20 | 0.717500 | 0.717500 (20) | unavailable (0) | 0 | 0 / 0 | 0 |
| mistralai/mistral-nemo | raw_files | 0 | 0 | unrun | unavailable (0) | unavailable (0) | 0 | 0 / 0 | 0 |
| mistralai/mistral-nemo | vector_db | 20 | 20 | 0.730000 | 0.752632 (19) | 0.300000 (1) | 0 | 0 / 0 | 0 |
| openai/gpt-4o-mini | no_context | 20 | 20 | 0.755000 | 0.755000 (20) | unavailable (0) | 0 | 0 / 0 | 0 |
| openai/gpt-4o-mini | raw_files | 0 | 0 | unrun | unavailable (0) | unavailable (0) | 0 | 0 / 0 | 0 |
| openai/gpt-4o-mini | vector_db | 20 | 20 | 0.723750 | 0.723750 (20) | unavailable (0) | 0 | 0 / 0 | 0 |
| qwen/qwen3-coder | no_context | 20 | 20 | 0.811250 | 0.811250 (20) | unavailable (0) | 0 | 0 / 0 | 0 |
| qwen/qwen3-coder | raw_files | 0 | 0 | unrun | unavailable (0) | unavailable (0) | 0 | 0 / 0 | 0 |
| qwen/qwen3-coder | vector_db | 20 | 20 | 0.741250 | 0.732895 (19) | 0.900000 (1) | 0 | 0 / 0 | 0 |

### Genuine dual-judge agreement

n=275; mean absolute judge-score difference=0.052909; exact agreement=119/275; absolute difference ≤0.10=236/275. Failed/single judgments do not enter this denominator. Per-model/mode agreement is in the JSON report.

### Paired vector-minus-no-context deltas

Only valid, uniquely keyed question intersections within this run/model. Descriptive, not temporal improvement or a causal retrieval effect; fixed-panel bootstrap intervals do not measure all sources of uncertainty.

| Model | Paired n | No-context mean | Vector mean | Mean delta | Question-bootstrap 95% interval | Pairs with fallback | Excluded questions |
|---|---:|---:|---:|---:|---|---:|---:|
| deepseek/deepseek-chat-v3.1 | 20 | 0.870000 | 0.635000 | -0.235000 | [-0.316250, -0.160000] | 0 | 0 |
| google/gemini-2.5-flash | 19 | 0.830263 | 0.605263 | -0.225000 | [-0.315789, -0.136842] | 1 | 1 |
| google/gemini-2.5-flash-lite | 19 | 0.803947 | 0.628947 | -0.175000 | [-0.276316, -0.080263] | 0 | 1 |
| gpt-5-mini | 20 | 0.896250 | 0.868750 | -0.027500 | [-0.066250, 0.001250] | 0 | 0 |
| mistralai/mistral-nemo | 20 | 0.717500 | 0.730000 | 0.012500 | [-0.035000, 0.058750] | 1 | 0 |
| openai/gpt-4o-mini | 20 | 0.755000 | 0.723750 | -0.031250 | [-0.071250, 0.007500] | 0 | 0 |
| qwen/qwen3-coder | 20 | 0.811250 | 0.741250 | -0.070000 | [-0.140000, -0.006250] | 1 | 0 |

Bootstrap: 10000 resamples per model, seed 20250830, paired-question resampling with replacement and interpolated percentile endpoints.

### Source summary reconciliation

41 fields compared; 14 differ under flag filtering or explicit missingness. This is sensitivity analysis, not proof that filtered scores are more accurate. All comparisons and stored numeric means are in JSON.

| Summary field | Source | Flag-filtered / missingness-aware | Explanation |
|---|---:|---:|---|
| overall_stats.average_score | 0.7538392857142857 | 0.7592625899280575 | flag-filtered sensitivity; ambiguous zero/failure classification, not a verified correction |
| models.deepseek/deepseek-chat-v3.1.score_by_mode.raw_files | 0.0 | None | unrun, not a zero score |
| models.google/gemini-2.5-flash.average_score | 0.7043750000000001 | 0.7224358974358974 | flag-filtered sensitivity; ambiguous zero/failure classification, not a verified correction |
| models.google/gemini-2.5-flash.score_by_mode.raw_files | 0.0 | None | unrun, not a zero score |
| models.google/gemini-2.5-flash.score_by_mode.vector_db | 0.575 | 0.6052631578947368 | flag-filtered sensitivity; ambiguous zero/failure classification, not a verified correction |
| models.google/gemini-2.5-flash-lite.average_score | 0.6981250000000001 | 0.716025641025641 | flag-filtered sensitivity; ambiguous zero/failure classification, not a verified correction |
| models.google/gemini-2.5-flash-lite.score_by_mode.raw_files | 0.0 | None | unrun, not a zero score |
| models.google/gemini-2.5-flash-lite.score_by_mode.vector_db | 0.5974999999999999 | 0.6289473684210526 | flag-filtered sensitivity; ambiguous zero/failure classification, not a verified correction |
| models.gpt-5-mini.score_by_mode.raw_files | 0.0 | None | unrun, not a zero score |
| models.mistralai/mistral-nemo.score_by_mode.raw_files | 0.0 | None | unrun, not a zero score |
| models.openai/gpt-4o-mini.score_by_mode.raw_files | 0.0 | None | unrun, not a zero score |
| models.qwen/qwen3-coder.score_by_mode.raw_files | 0.0 | None | unrun, not a zero score |
| mode_performance.raw_files | 0.0 | None | unrun, not a zero score |
| mode_performance.vector_db | 0.6958928571428578 | 0.7059782608695652 | flag-filtered sensitivity; ambiguous zero/failure classification, not a verified correction |

## Run: 67-chunks

280 retained rows; 7 model labels; 20 unique questions. Duplicate model/mode/question keys: 0; model-label mismatches: 0.
Record timestamps: `2025-08-29T23:30:30.101088` through `2025-08-30T00:51:05.557849`; source summary timestamp `2025-08-30T01:15:26.198752`. Missing/invalid timestamps: 0; repeated timestamp values: 0. Timezone unknown.
Valid-score n=280; generation failures=0; missing scores=0; invalid numeric scores=0; dual=279; single fallback=1; both failed=0; unknown judge status=0.
Stored numeric mean (including failure-labelled zeros)=0.774732; flag-filtered mean=0.774732. Neither is newly verified accuracy; do not call the difference model improvement.

### Model/mode descriptive scores

Means include eligible single fallbacks; dual-only and fallback-only means are shown independently. Unrun modes have no score. Model rows are alphabetic, not ranked.

| Model | Mode | Attempted | Valid n | Mean | Dual-only mean (n) | Fallback-only mean (n) | Generation failed | Missing / invalid | Both judges failed |
|---|---|---:|---:|---:|---|---|---:|---:|---:|
| deepseek/deepseek-chat-v3.1 | no_context | 20 | 20 | 0.865000 | 0.865000 (20) | unavailable (0) | 0 | 0 / 0 | 0 |
| deepseek/deepseek-chat-v3.1 | raw_files | 0 | 0 | unrun | unavailable (0) | unavailable (0) | 0 | 0 / 0 | 0 |
| deepseek/deepseek-chat-v3.1 | vector_db | 20 | 20 | 0.728750 | 0.728750 (20) | unavailable (0) | 0 | 0 / 0 | 0 |
| google/gemini-2.5-flash | no_context | 20 | 20 | 0.818750 | 0.818750 (20) | unavailable (0) | 0 | 0 / 0 | 0 |
| google/gemini-2.5-flash | raw_files | 0 | 0 | unrun | unavailable (0) | unavailable (0) | 0 | 0 / 0 | 0 |
| google/gemini-2.5-flash | vector_db | 20 | 20 | 0.702500 | 0.702500 (20) | unavailable (0) | 0 | 0 / 0 | 0 |
| google/gemini-2.5-flash-lite | no_context | 20 | 20 | 0.787500 | 0.787500 (20) | unavailable (0) | 0 | 0 / 0 | 0 |
| google/gemini-2.5-flash-lite | raw_files | 0 | 0 | unrun | unavailable (0) | unavailable (0) | 0 | 0 / 0 | 0 |
| google/gemini-2.5-flash-lite | vector_db | 20 | 20 | 0.677500 | 0.677500 (20) | unavailable (0) | 0 | 0 / 0 | 0 |
| gpt-5-mini | no_context | 20 | 20 | 0.893750 | 0.893750 (20) | unavailable (0) | 0 | 0 / 0 | 0 |
| gpt-5-mini | raw_files | 0 | 0 | unrun | unavailable (0) | unavailable (0) | 0 | 0 / 0 | 0 |
| gpt-5-mini | vector_db | 20 | 20 | 0.898750 | 0.898750 (20) | unavailable (0) | 0 | 0 / 0 | 0 |
| mistralai/mistral-nemo | no_context | 20 | 20 | 0.728750 | 0.756579 (19) | 0.200000 (1) | 0 | 0 / 0 | 0 |
| mistralai/mistral-nemo | raw_files | 0 | 0 | unrun | unavailable (0) | unavailable (0) | 0 | 0 / 0 | 0 |
| mistralai/mistral-nemo | vector_db | 20 | 20 | 0.721250 | 0.721250 (20) | unavailable (0) | 0 | 0 / 0 | 0 |
| openai/gpt-4o-mini | no_context | 20 | 20 | 0.753750 | 0.753750 (20) | unavailable (0) | 0 | 0 / 0 | 0 |
| openai/gpt-4o-mini | raw_files | 0 | 0 | unrun | unavailable (0) | unavailable (0) | 0 | 0 / 0 | 0 |
| openai/gpt-4o-mini | vector_db | 20 | 20 | 0.738750 | 0.738750 (20) | unavailable (0) | 0 | 0 / 0 | 0 |
| qwen/qwen3-coder | no_context | 20 | 20 | 0.788750 | 0.788750 (20) | unavailable (0) | 0 | 0 / 0 | 0 |
| qwen/qwen3-coder | raw_files | 0 | 0 | unrun | unavailable (0) | unavailable (0) | 0 | 0 / 0 | 0 |
| qwen/qwen3-coder | vector_db | 20 | 20 | 0.742500 | 0.742500 (20) | unavailable (0) | 0 | 0 / 0 | 0 |

### Genuine dual-judge agreement

n=279; mean absolute judge-score difference=0.050000; exact agreement=118/279; absolute difference ≤0.10=247/279. Failed/single judgments do not enter this denominator. Per-model/mode agreement is in the JSON report.

### Paired vector-minus-no-context deltas

Only valid, uniquely keyed question intersections within this run/model. Descriptive, not temporal improvement or a causal retrieval effect; fixed-panel bootstrap intervals do not measure all sources of uncertainty.

| Model | Paired n | No-context mean | Vector mean | Mean delta | Question-bootstrap 95% interval | Pairs with fallback | Excluded questions |
|---|---:|---:|---:|---:|---|---:|---:|
| deepseek/deepseek-chat-v3.1 | 20 | 0.865000 | 0.728750 | -0.136250 | [-0.215000, -0.061250] | 0 | 0 |
| google/gemini-2.5-flash | 20 | 0.818750 | 0.702500 | -0.116250 | [-0.200000, -0.033750] | 0 | 0 |
| google/gemini-2.5-flash-lite | 20 | 0.787500 | 0.677500 | -0.110000 | [-0.176250, -0.041250] | 0 | 0 |
| gpt-5-mini | 20 | 0.893750 | 0.898750 | 0.005000 | [-0.010000, 0.018750] | 0 | 0 |
| mistralai/mistral-nemo | 20 | 0.728750 | 0.721250 | -0.007500 | [-0.056250, 0.041250] | 1 | 0 |
| openai/gpt-4o-mini | 20 | 0.753750 | 0.738750 | -0.015000 | [-0.058750, 0.033750] | 0 | 0 |
| qwen/qwen3-coder | 20 | 0.788750 | 0.742500 | -0.046250 | [-0.108750, 0.015000] | 0 | 0 |

Bootstrap: 10000 resamples per model, seed 20250830, paired-question resampling with replacement and interpolated percentile endpoints.

### Source summary reconciliation

41 fields compared; 8 differ under flag filtering or explicit missingness. This is sensitivity analysis, not proof that filtered scores are more accurate. All comparisons and stored numeric means are in JSON.

| Summary field | Source | Flag-filtered / missingness-aware | Explanation |
|---|---:|---:|---|
| models.deepseek/deepseek-chat-v3.1.score_by_mode.raw_files | 0.0 | None | unrun, not a zero score |
| models.google/gemini-2.5-flash.score_by_mode.raw_files | 0.0 | None | unrun, not a zero score |
| models.google/gemini-2.5-flash-lite.score_by_mode.raw_files | 0.0 | None | unrun, not a zero score |
| models.gpt-5-mini.score_by_mode.raw_files | 0.0 | None | unrun, not a zero score |
| models.mistralai/mistral-nemo.score_by_mode.raw_files | 0.0 | None | unrun, not a zero score |
| models.openai/gpt-4o-mini.score_by_mode.raw_files | 0.0 | None | unrun, not a zero score |
| models.qwen/qwen3-coder.score_by_mode.raw_files | 0.0 | None | unrun, not a zero score |
| mode_performance.raw_files | 0.0 | None | unrun, not a zero score |

## Reproduction

From the repository root, with Python 3 and no external packages:

```sh
python3 scripts/legacy_audit.py import --source "/path/to/original/8-19-run"
python3 scripts/legacy_audit.py verify
python3 scripts/legacy_audit.py audit
```

Import is idempotent only for identical evidence and refuses changed files. Verify is read-only. Audit verifies the archive before writing deterministic reports; the dataset digest records the current metadata/ideal join input. Verification detects divergence from the local manifest, not authenticity against an independently trusted signature. Reports omit response and context text; originals require a separate rights/privacy review before public distribution.
