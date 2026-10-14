# Third-party notices, licensing, and citation

Reviewed for this refresh on 2026-10-13. This is an attribution and evidence inventory, **not a grant of rights, a complete software bill of materials, or legal clearance**. Citation, licensing, permission to use a hosted API, permission to process a document with an LLM, and permission to redistribute an artifact are separate questions.

## Project license: custom terms, not MIT or standard Apache-2.0

The authoritative local terms are in [LICENSE](LICENSE), which names **Copyright 2025 Jason M. Rodriguez**. Its text is Apache-derived but adds section 9 restrictions on commercial AI training/fine-tuning/improvement and commercial redistribution of the dataset as a primary product, with an academic/noncommercial evaluation exception. Therefore do not describe the repository as MIT, use an unqualified `Apache-2.0` SPDX identifier, or claim OSI-approved/open-source licensing for the combined artifact.

This attribution update **does not change those terms**. The scope of the added dataset restrictions versus first-party code should be clarified by the rights holder before choosing release/package metadata. A future decision to use standard Apache-2.0 for code and separate dataset terms would require an explicit licensing decision, contributor-rights review where applicable, and separate files; it is not accomplished by changing a README label. `CITATION.cff` links to the existing license rather than supplying a misleading SPDX identifier.

No first-party license can override a publisher's rights in standards, incorporated third-party content, software, model weights, or trademarks. The existing root license's academic exception does not create permission from those third parties.

## What is covered where

| Material | Attribution and rights evidence | Release treatment |
|---|---|---|
| First-party code, questions, methodology, teaching materials | [LICENSE](LICENSE), [CITATION.cff](CITATION.cff) | Apply actual first-party terms, while checking incorporated third-party material separately |
| Bundled standards, guidance, proposed rules, converted documents | [Per-document source register](data/cyber-frameworks/SOURCES.md), [framework bibliography](doc/framework-references.bib) | Preserve original attribution and notices; review each document's permission and intended use; do not blanket-license the corpus |
| Six copied historical exports | [Evidence manifest](data/legacy/8-19-run/manifest.json), source register for retrieved context | Local-only by default; embedded excerpts and model outputs need their own rights/privacy review |
| Runtime/development software, embedding/reranking models, hosted generation services | [Software and model credits](doc/software-and-model-credits.md), `pyproject.toml`, `uv.lock` | Dependencies' and weights' licenses remain upstream; provider/output terms are not SDK licenses |
| Research informing the refresh and acknowledged benchmark inspiration | [Methodology bibliography](doc/references.bib) | Cite the work actually relied on; a reference does not imply reproduced results or affiliation |

**Existing repository content matters:** the raw-export Git ignore rules do not remove the framework Markdown files already in `data/cyber-frameworks/`, nor do they remove any file from Git history. Do not publish a full source snapshot assuming all third-party excerpts have been excluded. Review the actual release file list and any existing public history; obtain permission or omit uncleared documents from the release artifact. No source documents are deleted or relicensed by this change.

### Standards and converted content

The per-document register maps every currently bundled framework Markdown document to its source, edition, citation key, and rights evidence. It distinguishes government publications from privately published standards and flags uncertain rights. Free download, a `.gov` URL, educational intent, a citation, and conversion to Markdown are **not interchangeable with redistribution permission**. Government sites may include third-party contributions; a government-work exception has a jurisdiction and scope.

The repository records Docling conversion in [architecture decision 0002](doc/architecture/decisions/0002-using-docling-to-prepare-context-for-evals.md). Conversion can introduce omissions and interpretation errors. Credit the original publisher and Docling separately, mark converted/adapted content, preserve required notices, and verify claims against the authoritative original. Do not imply that the publisher endorsed the conversion, benchmark, model, or classroom conclusions.

Current publisher terms are evidence for present release review, not proof of which terms governed acquisition or model processing in 2025. In particular, review AICPA permissions for the intended LLM/retrieval use as well as public redistribution; consult the source register's linked terms. Cite proposed rules as proposals and historical editions as historical, not as proof of current legal obligations.

### Software, model weights, APIs, and outputs

The software register lists direct dependencies at the versions pinned in the current lockfile and separately identifies configured model cards and provider terms. A dependency declaration establishes an intended dependency, not proof that every package was executed in a historical experiment. Current lock versions are not reconstructed 2025 runtime versions. The new archive/pilot CLI tools use the Python standard library; cite Python/version in methods as appropriate, not a GPU stack they did not use.

When distributing wheels, containers, installers, or weights, include the actual upstream license texts, copyright notices, and required NOTICE/attribution files for the distributed versions and bundled components. Links here do not substitute for notices a license requires to accompany a binary. Transitive dependencies and bundled native libraries need a distribution-specific inventory before such packaging; this repository review does not certify them.

Record actual provider, endpoint, requested/returned model, revision if available, use date, and terms relevant to publication. A hosted model alias does not establish the exact downloadable-weight version or its license. Ownership or permission to publish generated output does not automatically clear reproduced source text. Do not cite model-generated prose as an authoritative legal/security source.

### Acknowledged inspiration: EQ-Bench

The existing README credits [EQ-Bench](https://github.com/EQ-bench/EQ-Bench) as inspiration. Credit **Samuel J. Paech**, [*EQ-Bench: An Emotional Intelligence Benchmark for Large Language Models* (2023)](https://arxiv.org/abs/2312.06281), using `paech2023_eqbench`.

The upstream [MIT license](https://github.com/EQ-bench/EQ-Bench/blob/main_v2_4/LICENSE) states **Copyright (c) 2023 Samuel Paech** and requires its copyright and permission notice in copies/substantial portions of its software. The current attribution establishes inspiration, not the extent of any copied code. If a distributed file derives from EQ-Bench, retain that upstream notice and license with the relevant material; a bibliography entry is not a substitute. EQ-Bench's license does not make this repository MIT-licensed.

## How to cite this project

Use the machine-readable [CITATION.cff](CITATION.cff), or BibTeX key `rodriguez_cyber_policy_bench` in [doc/references.bib](doc/references.bib).

Suggested human-readable repository citation:

> Rodriguez, Jason M. *Cyber Policy Benchmark*. Software and evaluation repository. https://github.com/FullStack-Platforms/ai-cyber-policy-bench.

In the publication's methods, add the **exact release/tag or commit used**, access date, dataset hash, archive manifest hash and run labels, and the scoring protocol/rubric version. A living repository citation alone is not enough to reproduce a result. The author's reported July 26, 2025 creation date is not an established software release date, and the August 29–30 export dates are not a paper's publication date. No DOI, ORCID, affiliation, coauthor, release date, or publication venue is invented here. Update the author list from actual contributions and contributor agreement before a paper/release.

Once a real versioned archive receives a DOI, add its actual metadata to `CITATION.cff` and the bibliography. If a paper is subsequently published, add its actual citation; do not substitute the working abstract's title for a published article. Citation is requested scholarly credit, not an additional license condition created by this document.

## How to cite the materials used

1. **Benchmark/data/method:** cite this project plus the exact artifact version. Distinguish author-created questions from quoted or adapted publisher content.
2. **A framework claim or reference answer:** cite the original publisher, exact edition/date, control/article/section or page, authoritative URL/DOI, and access/as-of date. Use the source-register BibTeX key. Cite the local converted file/hash additionally for reproducibility, not instead of the original.
3. **Evaluation theory:** cite the relevant work, not a generic list. `autio2024_genai_profile` supports source/provenance and deployment-validity guidance; `keller2026_evaluation_toolbox` motivates limits on uncertainty/generalization; `wallach2025_measurement` motivates construct validity. The refresh does not claim to implement every method in these works.
4. **Conversion/retrieval/model tooling:** cite upstream software and requested papers/model cards for components actually used, recording versions and weight revisions. See the software register; do not cite a package merely because it appears transitively in a lockfile.
5. **A model result:** cite the benchmark run, exact question/panel, protocol, provider/model identifier, generation date, and ratings. Cite the underlying authority separately when discussing correctness. Explain unknown historical provenance rather than inferring it from current configuration.
6. **Classroom or public communications:** link the project artifact and relevant primary sources. A LinkedIn/Substack acknowledgment should not replace the paper's bibliography or required license notices. Cite/credit student contributions only with appropriate permission and institutional safeguards.

The framework and methodology `.bib` files can be imported together; keys are distinct. The software register supplies additional canonical tool/model references. Preserve upstream bibliographic names and spellings. A formal reference is not a claim that a source validates every local answer key.

## Release checklist additions

- Include `LICENSE`, this notice, `CITATION.cff`, both bibliographies, the source register, and software/model credits with the cleared artifact.
- Resolve the project's custom-license scope before assigning a standard license label in Zenodo, package metadata, or a paper's data-availability statement.
- Record per-document rights evidence and the permission applicable to the proposed use/distribution. Where unclear, hold the document out of the public artifact; do not mark it cleared based on citation alone.
- Keep publisher notices in authorized derivatives; mark conversion/adaptation and cite both original and local version. Do not strip restrictive notices merely to make an export easier to release.
- Archive the terms/notices applicable to the actual release and provider use, within their permitted reuse scope. Dynamic URLs are not historical contracts.
- Confirm all paper citations and public acknowledgments describe work actually used. Package/weight/license changes require refreshing the corresponding inventory.

## Citation validation performed

`cffconvert` 2.0.0 accepted `CITATION.cff` against schema 1.2.0 and successfully exported the project citation to BibTeX. `bibtexparser` 1.4.3 parsed five project/methodology entries and thirteen framework entries with unique keys. A coverage smoke checked every bundled framework path, every framework citation key, all fifteen direct dependency declarations and their locked versions, and local attribution links. These tools are credited in the software register; no benchmark API calls or model reruns were needed for this documentation-only update.

To validate and render the project citation without installing the benchmark stack:

```sh
uvx --python 3.12 --from cffconvert==2.0.0 cffconvert --validate --infile CITATION.cff
uvx --python 3.12 --from cffconvert==2.0.0 cffconvert --infile CITATION.cff --format bibtex
```

Validation proves format/coverage, not ownership, accuracy, endorsement, or permission to redistribute.
