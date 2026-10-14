# Release, paper, and classroom reflection

## Release decision

**Publish the audit and reproducibility tools first.** Suggested release title: *Revisiting a 2025 Cybersecurity Policy Benchmark: Evidence Quality Before Model Rankings*. It remains useful if the contemporary models do not improve. The contribution is a transparent account of what can and cannot be learned from a historical evaluation, plus a reusable method for teaching source verification.

This document contains publication drafts, not a claim that a release, paper submission, experiment, or classroom study has happened. The professor should approve first-person language. “Created July 26, 2025” reflects the author's account; “measured August 29–30, 2025” reflects export timestamps.

### Public artifact contents

- Source code for the offline archive audit and opt-in pilot, with behavioral tests.
- Aggregate audit JSON/Markdown, checksum manifest, limitations, rubric, and reproduction commands.
- Dataset description: 101 current items; archive covers 20, with the root continuity panel covering 15. State uneven framework coverage and unknown historical request/judge configuration.
- A versioned technical note using the abstract and outline below, plus the classroom exercise.
- [Project citation metadata](../CITATION.cff), [third-party notices](../THIRD_PARTY_NOTICES.md), [source register](../data/cyber-frameworks/SOURCES.md), [framework bibliography](framework-references.bib), [methodology bibliography](references.bib), and [software/model credits](software-and-model-credits.md).
- After actual collection/review: contemporary request metadata, observed usage/cost where available, reviewed references, ratings, adjudication record, and paired analysis. Raw outputs require a separate permission/sensitivity decision.

### Publication gate

1. Independently review the highlighted score/missingness findings and source references. Never rebrand a legacy LLM rating as verified accuracy.
2. Check redistribution rights and privacy for raw outputs, retrieved excerpts, prompts, and dataset files using the [source register](../data/cyber-frameworks/SOURCES.md) and [third-party notices](../THIRD_PARTY_NOTICES.md). The root license is custom Apache-derived, not MIT or standard Apache-2.0, and does not grant publisher rights. Raw copied exports are local-only by default, but framework Markdown files already in the repository also require review. A citation, educational intent, or `.gitignore` entry is not permission or a way to remove previously tracked data. Review intended LLM/retrieval use as well as redistribution.
3. Release the audit code, manifest, and aggregates even if raw-data redistribution is blocked. State that exact private-data reproduction requires authorized access. A checksum verifies equality; it does not make restricted data publicly reproducible. For the strongest artifact, obtain permission or make a separately licensed context-free derivative, document every removal, and retain the original privately.
4. Run the documented offline commands and tests. Record the software revision at release, runtime version, exact command, artifact checksums, and any unavailable historical metadata.
5. Manually review the public file list for secrets, absolute personal paths, student data, and copyrighted excerpts. Keep human review identity keys private until blind scoring closes.
6. Create a tagged repository release; archive the cleared release with a DOI service such as Zenodo. Use a title/date that distinguishes project creation from export generation. Record the actual version/date/DOI in `CITATION.cff` and the bibliography only after assignment; do not label the combined artifact MIT/Apache-2.0. No DOI or public release URL exists merely because these instructions exist.
7. Publish the retrospective communication below. Publish a model-improvement claim only after the paired experiment supports it; publish a learning-outcome claim only after a suitable classroom assessment supports it.

For the paper, use the project and source BibTeX files above, plus tool/model citations from the software register for components actually used. Add section-level source references to reviewed answers. For X/LinkedIn link the actual cleared artifact; for Substack include a source/credits footer linking the artifact, primary standards discussed, and the notices. These references do not imply endorsement or redistribution rights.

## Paper route

**Best first target:** a short reproducibility/experience report or computing/security-education workshop paper. A small convenience panel is not a convincing general “best cybersecurity model” paper. Choose a current venue after checking its scope, deadlines, artifact policy, and human-subject requirements; no acceptance or current call is assumed here.

### Working title

*When the Benchmark Becomes the Lesson: Auditing and Reusing a 2025 Cybersecurity-Policy Evaluation*

### Retrospective abstract draft

Rapid changes in language models create pressure to refresh benchmarks before examining whether their historical results support longitudinal comparison. We revisit a cybersecurity-policy evaluation developed in 2025 and audit three exported runs containing 710 response records over 20 distinct questions. The exports record two evaluated context conditions, while their summaries also include a zero-valued condition that was not run. Judge metadata labels 704 dual successes, four single-judge fallbacks, and two both-judge failures. These labels are not conclusive: the current legacy scorer rejects zero scores as failed judgments, and the two both-failed records contain substantive explanations for zero. We preserve the exports with content hashes and report stored scores alongside flag-filtered sensitivity analyses without pooling repeated questions as independent evidence. We provide a low-cost protocol for comparing contemporary outputs with archived responses under a common, source-reviewed human rubric, alongside a classroom exercise on evidence verification and evaluation validity. The retrospective does not establish contemporary model improvement or student learning gains. Its contribution is an auditable research and teaching artifact that makes the limitations of historical AI evaluations explicit.

### Paper structure and evidence needed

| Section | Available now | Required for stronger claims |
|---|---|---|
| Motivation and chronology | Author's origin account; exported response dates | Contemporary lab notes or commit history if asserting precise historical development milestones |
| Dataset and provenance | Three preserved exports, manifest, dataset matching, coverage | Rights-cleared public derivative or authorized data access procedure |
| Measurement audit | Missing condition, failure handling, paired run descriptions | Independent replication of the audit |
| Contemporary pilot | Executable generation/review/compare protocol | Real outputs, reviewed references, blind ratings, uncertainty, actual usage |
| Reliability and validity | Documented threats and predeclared rubric | Independent rater results; balanced held-out questions for broad claims |
| Teaching application | Complete lesson and assessment plan | Actual student artifacts/consent and institutional determination if used as research |

Do not fill a results section with projected gains. Report a null result or regression honestly. The historical 11-chunk versus 67-chunk folders do not isolate retrieval improvements: prompts/configuration and repeated generation may differ, and folder names alone do not verify the runtime retrieval settings. Likewise, two judges are not independent ground truth merely because there are two of them.

## Classroom exercise: “Audit the confident answer”

**Status:** ready-to-use lesson design; not evidence that this lesson has already improved learning.

**Learning objectives:** students distinguish claims from support; verify a control citation and its scope; explain why missing scores are not failures of subject-matter competence; identify an inappropriate comparison; and revise advice using a dated source.

**Materials:** three instructor-reviewed questions from the frozen panel, two anonymized responses per question, the same reviewed source excerpts for everyone, the human rubric, and the aggregate audit. Use only excerpts the class is permitted to access. Legacy responses from two different historical models suffice; contemporary API access is not required.

**A 60-minute session**

1. **0–8 minutes — individual baseline:** independently identify unsupported claims and explain which source would settle them. No model access. Collect a short justification and confidence rating.
2. **8–23 minutes — source audit in pairs:** annotate each material claim with a source section, edition/date, and “supported / unsupported / wrong scope / insufficient facts.” Explicitly check attractive but invented control references.
3. **23–35 minutes — blind scoring:** apply the same rubric to both answers and mark consequential errors. Require rationale, not just a numerical grade.
4. **35–45 minutes — compare judgments:** reconcile disagreements by consulting sources. Reveal identities only after scoring. Discuss why fluent prose, a model name, or an old answer key is not evidence.
5. **45–55 minutes — individual transfer task:** use a different, difficulty-matched scenario and source excerpt. Assess the student's own revised recommendation and explanation, not their ability to copy a model output.
6. **55–60 minutes — exit reflection:** explain what changed their judgment, what remains uncertain, and how an evaluation could mislead its reader.

**Assessable outcomes:** instructor-scored proportion of correctly verified claims, fabricated citations correctly identified, appropriateness of uncertainty, source-to-recommendation traceability, and time to produce a defensible answer. Retain raw denominators, not just percentages. Do not infer benefit from satisfaction surveys alone.

For a teaching reflection, distinguish observations from measurements. To estimate an instructional effect, use matched pre/post tasks, counterbalance task order or use an appropriate comparison group, independently score anonymized work, and acknowledge practice/order and selection effects. Obtain institutional guidance on research ethics/IRB before collecting student data for publication; ordinary instructional permission is not necessarily research consent. Provide an equivalent activity without paid accounts and do not send identifiable student work to model APIs without approval.

**Honest first-person bridge:** “This gives me a concrete way to teach students to verify an AI-generated compliance claim rather than accept a fluent answer.” If classroom artifacts substantiate an experience, describe that experience specifically. Do not change this to “student accuracy improved” without an assessment.

## Tweet / X draft

Standalone, publishable after author review; no claim of a completed contemporary experiment:

> I built cybersecurity-policy evals in July 2025. Revisiting 710 archived responses, I found an unrun condition reported as zero. AI moves fast; our measurements need scrutiny too. My classroom takeaway: teach students to verify claims, not trust fluent answers.

A link can go in a reply after an actual release exists. A short thread can add:

> These were 710 response records, not 710 independent questions. Three runs reused a 20-question panel. Before asking which new model wins, I'm preserving the evidence and rechecking the measurement.

> The next comparison will grade old and new answers against the same reviewed sources, blind to model identity. A new judge plus an old score is not a clean measure of progress.

## LinkedIn draft

**Revisiting a cybersecurity benchmark taught me to audit the measurement before celebrating the model.**

I created these cybersecurity-policy evaluations in July 2025. Revisiting the archived experiments, I found a useful reminder of how quickly AI tooling—and our expectations for evaluating it—move.

The exports preserve 710 response records across three runs, but only 20 distinct questions. A context condition that was never run appears as zero in the summaries. More subtly, the legacy scoring code treats a zero grade as judge failure. The saved failure labels therefore need scrutiny too.

Those distinctions matter. Missing measurement is not the same as a wrong answer. Repeated responses are not independent test questions. And a score from a new judge cannot automatically be compared with one from an old judge.

I'm refreshing the project around preserved evidence, explicit limitations, and a small comparison in which old and new answers receive the same source-reviewed rubric. I am not yet claiming today's models perform better on it.

As a cybersecurity educator, I see a practical classroom use: ask students to audit a confident compliance answer, locate the actual authority, check its scope, and defend their correction. That is a more meaningful exercise than asking whether an answer “sounds right.”

The speed of this industry makes the habit of verification more important, not less. The benchmark itself can become a lesson in that habit.

## Substack draft

### My cybersecurity benchmark aged. That made it worth revisiting.

When I created these cybersecurity-policy evaluations in July 2025, I wanted to ask a practical question: can a language model give useful, accurate guidance about cybersecurity frameworks and compliance?

Returning to the saved experiments, I could have started by swapping in newer model names and publishing a fresh ranking. Instead, the archive made a different first step necessary: check what the old measurements actually meant.

The exports contain 710 response records across three runs. That sounds substantial until we ask the denominator question. The runs cover 20 distinct questions, with repeated questions across models and context conditions. The root run covers only 15 questions and is heavily weighted toward SOC 2. This is a useful continuity panel, not a representative exam of all cybersecurity expertise.

There is also a chronology distinction worth keeping. July is the project's origin in my account. The saved response timestamps are from August 29–30, 2025. The folder label is not a reliable substitute for the experiment record.

#### An empty condition is not a score of zero

One of the most useful findings was simple: the summaries include a zero for a context condition that was not evaluated. The response records show two conditions, not three.

A model that answers incorrectly, a generation that fails, and a judge that fails are three different events. Yet the legacy scorer treats a zero grade as a failed judge. The two records labelled “both judges failed” contain substantive explanations for awarding zero. Excluding those records might raise an average without improving its validity. The audit therefore preserves both the stored-score view and the flag-filtered sensitivity view instead of pretending the ambiguity has been resolved.

This is why the refresh starts with hashes, explicit denominators, missingness, and retained original files. None of those features makes a model smarter. They make it harder for me to tell myself an unsupported story about the model.

#### What would count as progress?

A contemporary comparison needs more than a new model and a higher number. I want old and new answers to face the same reviewed sources and the same rubric, with the rater blinded to identity as far as practical.

The answer key deserves scrutiny too. An inherited “ideal” answer can contain overstatements, incomplete scope, or an outdated interpretation. If I correct it, I must apply that correction to both eras—not quietly give one side a different exam.

The first comparison can stay small: the 15-question continuity panel, an explicitly chosen contemporary model, and human review rather than another layer of paid model judges. It cannot establish broad cybersecurity superiority. It can reveal concrete improvements, persistent mistakes, or regressions on those questions once the experiment and grading are complete.

#### The classroom opportunity

The most interesting teaching artifact may not be the leaderboard. It may be two plausible answers that disagree.

Students can identify the material claims, check a control citation, locate the relevant source, explain its scope, and revise the recommendation. They can also discover that their own rubric needs clarification. That turns an AI answer from something to accept into something to investigate.

I see this as a practical way to teach verification, judgment, and justified uncertainty. That is a proposed benefit and lesson design, not yet a measured learning gain. A claim about student improvement would need student work, a suitable assessment, and appropriate institutional review if used as research.

#### The honest release

The first release should be a transparent retrospective: what survived from the original runs, what can be recomputed, what metadata is missing, and how a small new comparison will be conducted. Copyrighted framework excerpts and sensitive data do not become freely redistributable because they appear inside an evaluation export.

A paper may follow, particularly as a reproducibility or education experience report. But the artifact should be useful before a paper exists—and useful even if the new models do not win.

The industry moves quickly. My responsibility as an educator is not to keep rewriting the victory headline. It is to help students ask what a claim is based on, what would disprove it, and whether the evidence actually supports the conclusion.

## Claims to avoid

- “AI cybersecurity accuracy improved by X%” from different questions, judges, or retrieval settings.
- “710 independent tests,” “raw-file context scored zero,” or “two judges guarantee correctness.”
- “All current models” from one or two selected endpoints; “reasoning improved” from one composite score.
- “The benchmark is fully current” before version-specific reference review.
- “The classroom intervention improved learning” without outcome evidence.
- “Open dataset” before permissions and privacy checks; “published paper” before actual publication.

## Source and credit footer for the reflection

Include this source list with the Substack/article version; use a link to the cleared artifact and its credits for shorter social posts.

- **Project and author:** Jason M. Rodriguez, *Cyber Policy Benchmark* — [citation metadata](../CITATION.cff), [canonical repository](https://github.com/FullStack-Platforms/ai-cyber-policy-bench). Identify the actual release/commit when published.
- **Historical observations:** [recomputed audit](../reports/legacy-audit.md) and [original-export checksum manifest](../data/legacy/8-19-run/manifest.json). These support archive claims, not contemporary model or classroom gains.
- **Evaluation guidance:** Autio et al., [NIST AI 600-1](https://doi.org/10.6028/NIST.AI.600-1); Keller et al., [NIST AI 800-3](https://doi.org/10.6028/NIST.AI.800-3); Wallach et al., [measurement validity](https://arxiv.org/abs/2502.00561). Full bibliographic metadata: [references.bib](references.bib).
- **Original authorities and third-party tools:** [framework sources and rights](../data/cyber-frameworks/SOURCES.md), [software/model credits](software-and-model-credits.md), and [third-party notices](../THIRD_PARTY_NOTICES.md). Link the specific primary authority when discussing a particular control or legal obligation.
- **Acknowledged inspiration:** Samuel J. Paech, [EQ-Bench](https://arxiv.org/abs/2312.06281). Acknowledgment does not imply endorsement or that its emotional-intelligence results transfer to cybersecurity.
