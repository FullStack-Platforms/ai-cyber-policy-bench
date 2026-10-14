# A defensible refresh of a 2025 cybersecurity-policy benchmark

## Decision

Release a **retrospective evaluation audit and teaching artifact**, then add a small, predeclared contemporary comparison. Do not sell an updated leaderboard as evidence of progress before collecting comparable results. The distinctive contribution is a cybersecurity educator's domain judgment: whether advice is defensible against authoritative sources, not whether prose sounds expert.

This benchmark measures responses to cybersecurity policy and compliance questions. It does not measure exploit development, incident-response execution, operational security, or overall cybersecurity competence.

## What the evidence establishes

- July 26, 2025 is the author's reported creation date; the copied exports do not independently establish it. Current question metadata also contains later dates. Describe the project origin and the experiment dates separately.
- The folder label `8-19-run` is retained for traceability. Embedded response timestamps span August 29–30, 2025 and do not include a timezone.
- Three exports contain 150, 280, and 280 response records. There are 20 distinct questions across the archive, not 710 independent questions. The two larger runs reuse models/questions; do not pool their records into independent observations.
- Only `no_context` and `vector_db` were run. Summary `raw_files: 0.0` entries are not measurements.
- Judge metadata labels 704 dual successes, four single-judge fallbacks, and two both-judge failures. These are **flags, not confirmed infrastructure failures**: the current legacy scorer requires `accuracy_score > 0` to recognize a successful judge, and the two both-failed records contain substantive grading explanations justifying zero. The audit shows stored means alongside flag-filtered sensitivity estimates. Do not treat excluding those zeros as an established correction or improvement. A genuine judge failure is missing measurement; a genuine zero grade must remain zero. The archived flags cannot reliably distinguish them.
- The current JSONL has 101 items, not the six asserted in the historical validation report. All archived questions match current question text, and archived ideals match the current `ideal` field. Exact matching does not establish factual correctness.
- The frozen root panel has 15 questions: ten SOC 2-only, two GDPR, one NIST CSF, one HIPAA, and one SOC 2/GDPR. It is deliberately a continuity panel, not a balanced sample of cybersecurity.

The generated [audit](../reports/legacy-audit.md) is the numeric source of record. Retain run-level/model-level denominators and judge coverage alongside every reported score. Scores are legacy judge ratings, not verified accuracy percentages.

## What changes now

| Dimension | Legacy evidence | Refresh |
|---|---|---|
| Provenance | Folder names and JSON summaries | Byte-preserved exports, SHA-256 manifest, mutation verification |
| Missing conditions | Unrun condition displayed as zero | Explicit not-run state and observed denominators |
| Judge failure | Zero grades can be labelled failed; fallback mixed into summaries | Flags separated, ambiguous zeros disclosed, stored and flag-filtered means retained |
| Comparisons | Temptation to rank pooled runs | Within-run matched questions; no temporal inference from RAG settings |
| New sampling | First items and implicit model selection | Frozen, explicit 15-question panel and requested model IDs |
| New grading | Historically scored against inherited ideals | Source-reviewed references, same blinded human rubric for both eras |
| Execution cost | Heavy retrieval environment and multiple judges | Standard-library offline audit; opt-in no-context generation; manual grading |
| Classroom claim | Anecdote could become causal claim | Proposed lesson and measurable outcomes; no invented learning gains |

These are implemented evidence/workflow improvements. They are not a measured increase in model capability. The existing heavy RAG engine and scorer are retained as historical infrastructure, including the documented zero/failure defect; do not use them for the refreshed comparison. The new pilot bypasses that scorer and uses explicit human ratings.

## Two evaluation tracks, not one moving target

### Track A: frozen continuity panel — supported by the pilot CLI

1. Use all 15 root-run questions, with archived `openai/gpt-4o-mini` responses as the default historical comparator. Select contemporary model IDs explicitly from the provider catalog on execution day. Record why they were chosen before looking at outputs. A useful low-cost pairing is one economical model plus one stronger reference model, not an exhaustive frontier sweep.
2. Keep question text fixed. Reconstruct the no-context prompt from repository code, while disclosing that the archive does not preserve the complete historical request, provider routing, decoding settings, or pinned model revision. This is a contemporary-system versus archived-system comparison, not a causal estimate of training progress.
3. Review every reference against dated, authoritative sources **before grading**. Resolve errors in a separate reviewed reference, retaining the archived ideal unmodified. Apply the corrected reference to both old and new answers. The first SOC 2 ideal's categorical language about required categories and an observation period needs particular scrutiny; do not assume inherited answer keys are authoritative.
4. Regrade both eras blindly with one fixed rubric. Do not subtract a 2025 LLM judge score from a 2026 human or new-LLM score. Do not treat the archive's numeric judge positions as authenticated judge model identities.
5. Report exact complete-rating counts, missing/failed generations, individual paired changes, and a question-level bootstrap interval. The pilot's estimand is **full-panel task utility**: failed/missing generations require an explicit human-entered zero, because no completed service was delivered; unreviewed answers remain blank and block comparison. This is distinct from subject-matter competence or conditional answer accuracy, and from the archive audit's uncertain judge-failure flags. Interpret the interval as exploratory sensitivity to this small panel, not population representativeness or uncertainty over decoding randomness. A single generation per question does not estimate run-to-run variability.
6. Report critical-error rates separately. A polished answer with a fabricated control citation should not disappear inside a high average writing score.

Public benchmark contamination cannot be ruled out. Model aliases may drift. Record actual returned model IDs and usage; a returned alias is not a cryptographic model-version pin.

### Track B: contemporary relevance — paper extension, not a claimed result

Keep a separate versioned challenge set; never quietly revise Track A. Develop new expert-reviewed cases for source/version conflicts, evidence sufficiency, unsupported legal certainty, fabricated controls, abstention under missing facts, and prompt injection inside retrieved policy text. Include both legitimate instructions and malicious document instructions; score task utility as well as resistance to injection. Compare every candidate on the same frozen corpus/retrieval configuration if adding RAG.

For each new case retain framework edition, jurisdiction, effective/as-of date, authoritative URL and section, required claims, prohibited claims, acceptable uncertainty, and reviewer decisions. Label proposals versus enacted rules. Current NIST CSF means CSF 2.0's **six** Functions, not the old five-Function example in the historical methodology. Check regulatory versions at evaluation time rather than renaming the entire legacy dataset “current.”

A paper-grade extension should add a preregistered, more balanced held-out panel and repeated generations where variability matters. Choose sample size from a stated smallest worthwhile difference and pilot variance; do not promise significance from 15 questions. Keep held-out answers unreleased until collection closes where feasible, then document any contamination limits.

## Human rubric: `cyber-policy-human-v1`

Score each response from 0 to 1 using four anchored components. Keep component rationale in the review notes; enter their weighted total in `score`.

| Component | Weight | Full credit | Half credit | Zero credit |
|---|---:|---|---|---|
| Factual and scope correctness | 0.45 | Material claims correct for stated version, jurisdiction, and scenario | Mostly correct with a material omission | Central recommendation or obligation wrong |
| Source/control support | 0.30 | Required claims traceable to reviewed sources; no fabricated authority | Relevant source but imprecise or incomplete support | Fabricated or materially misattributed authority |
| Practical applicability | 0.15 | Prioritized, feasible actions responsive to the scenario | Generic but usable actions | Unusable or unsafe guidance |
| Calibration | 0.10 | Assumptions and consequential uncertainty explicit | Some unjustified certainty | Unsupported categorical legal/compliance conclusion |

`critical_error=yes` for a material fabricated authority, dangerously incorrect obligation/scope, or recommendation that would create a consequential compliance/security failure. This is a separate outcome, not an automatic hidden change to the numerical score. Record the affected claim and authoritative correction. Fluency alone earns no accuracy credit. A justified refusal or request for missing information can earn calibration credit; blanket refusal is not automatically correct.

The rating packet requires a reviewed reference and an explicit reference-review acknowledgment. That is a procedural check, not automated proof that review happened. Keep the identity key away from the rater; model self-identification and stylistic clues can still compromise blinding. For publication have a second cybersecurity reviewer independently score a prespecified balanced subset (or all 30 answers for a one-model pilot), report raw disagreement/absolute score differences, then adjudicate with rationale. Manual review trades API spend for faculty time; it is not free labor.

## Budget and speed

| Stage | Generation requests | Paid judge requests | Budget decision |
|---|---:|---:|---|
| Archive audit and release preparation | 0 | 0 | No provider spend |
| One contemporary model, full root panel | 15 | 0 | Check provider prices, set provider-side spending limit |
| Two contemporary models, full root panel | 30 | 0 | Same questions, separate model contrasts |

No live API price is asserted here. Estimate before execution as `sum(input_tokens * input_price_per_million + output_tokens * output_price_per_million) / 1_000_000`, including provider-billed reasoning tokens and any fees. As an **illustration, not a quote or cap**, 30 calls averaging 500 input and 1,000 billable output tokens at $1/$5 per million would be $0.165. Real token use and pricing differ; the CLI request/token limits are not a dollar guarantee. Set a small provider-side limit (for example $5 if acceptable) and stop on unexpected billing. Do not spend effort rerunning every 2025 model if unavailable.

Suggested sequence: archive audit and reference review; one-model pilot; blind grading and release; second model and independent review only if they answer a useful question. The faculty reference review, not cloud compute, is likely the dominant work. Do not buy more inference to compensate for a flawed rubric.

## Primary guidance

Use the [project/methodology bibliography](references.bib) and [framework bibliography](framework-references.bib) for publication references. The [source register](../data/cyber-frameworks/SOURCES.md) maps local converted files to exact editions and rights evidence; [third-party notices](../THIRD_PARTY_NOTICES.md) explain citation versus permission. Cite edition and section in every reviewed reference, and record the local file hash separately. Referencing a current publisher download does not prove the bundled historical file is that edition.

- [NIST AI 600-1, Generative AI Profile (2024)](https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.600-1.pdf): provenance, source verification, domain-appropriate testing, and limits on extrapolation.
- [NIST AI 800-3, Expanding the AI Evaluation Toolbox with Statistical Models (2026)](https://www.nist.gov/publications/expanding-ai-evaluation-toolbox-statistical-models): distinguish fixed-benchmark performance from generalization and make uncertainty assumptions explicit. This pilot does not implement the report's mixed-model methodology.
- [Wallach et al., Evaluating Generative AI Systems Is a Social Science Measurement Challenge (2025)](https://arxiv.org/abs/2502.00561): define the construct and interrogate measurement validity.
- [AICPA, Trust Services Criteria, revised points of focus 2022](https://www.aicpa-cima.com/resources/download/2017-trust-services-criteria-with-revised-points-of-focus-2022): authoritative starting point for SOC 2 reference review; access and reuse terms still apply.
- [NIST CSF 2.0](https://doi.org/10.6028/NIST.CSWP.29): version-specific authority, not a guarantee that every local answer key accurately interprets it.
