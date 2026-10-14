# Software and model credits

This inventory accompanies [Third-party notices and citation guidance](../THIRD_PARTY_NOTICES.md). It credits upstream work and records license evidence; it does not relicense third-party material, certify compliance, or constitute a complete software bill of materials. Citation is not permission to reuse software, weights, training data, benchmark inputs, or generated text.

Evidence was consulted on **2026-10-13**. Package versions below come from the checked-in [uv.lock](../uv.lock), not an installed environment or a reconstruction of the historical benchmark environment. License declarations come from version-specific PyPI metadata or tagged upstream license files. Linked service terms and unpinned model cards can change; they do not establish the terms accepted for historical runs.

## Direct Python dependencies

The current [pyproject.toml](../pyproject.toml) declares **15 direct distributions: 10 runtime and 5 development**. The `chunking` extra on `docling-core` is not a separate distribution. Multiple lock entries for a package are conditional resolutions, not additional direct dependencies. The project supports Python `>=3.10,<3.13`; NumPy and scikit-learn have different locked versions within that range.

The table records upstream declarations, not a conclusion that every file or bundled binary shares one license. In particular, retain the full compound license expressions for recent NumPy and PyTorch releases rather than describing them only as BSD or Apache.

| Direct runtime distribution | Exact locked version(s) | Credit / upstream project | Declared license and version-specific evidence |
| --- | --- | --- | --- |
| `chromadb` | `1.5.9` | [Chroma](https://github.com/chroma-core/chroma): vector storage and retrieval | Apache-2.0; [release metadata](https://pypi.org/pypi/chromadb/1.5.9/json), including its license classifier and release description |
| `docling` | `2.112.0` | [Docling](https://github.com/docling-project/docling): document conversion | MIT; [release metadata](https://pypi.org/pypi/docling/2.112.0/json) |
| `docling-core[chunking]` | `2.87.0` | [Docling Core](https://github.com/docling-project/docling-core): document representation and chunking | MIT; [release metadata](https://pypi.org/pypi/docling-core/2.87.0/json) |
| `numpy` | `2.2.6` on Python 3.10; `2.4.6` on 3.11; `2.5.1` on 3.12 | [NumPy](https://github.com/numpy/numpy): numerical arrays and computation | `2.2.6`: BSD-3-Clause for NumPy itself, [tagged license](https://github.com/numpy/numpy/blob/v2.2.6/LICENSE.txt); `2.4.6` and `2.5.1`: `BSD-3-Clause AND 0BSD AND MIT AND Zlib AND CC0-1.0`, [2.4.6 metadata](https://pypi.org/pypi/numpy/2.4.6/json), [2.5.1 metadata](https://pypi.org/pypi/numpy/2.5.1/json). Distribution-specific bundled notices still apply. |
| `openai` | `2.45.0` | [OpenAI Python SDK](https://github.com/openai/openai-python): API client, including OpenAI-compatible endpoints | Apache-2.0; [release metadata](https://pypi.org/pypi/openai/2.45.0/json). This is the SDK license, not an API/model license. |
| `requests` | `2.34.2` | [Requests](https://github.com/psf/requests): HTTP requests | Apache-2.0; [release metadata](https://pypi.org/pypi/requests/2.34.2/json) |
| `scikit-learn` | `1.7.2` on Python 3.10; `1.9.0` on 3.11–3.12 | [scikit-learn](https://github.com/scikit-learn/scikit-learn): numerical and machine-learning utilities | BSD-3-Clause; [1.7.2 metadata](https://pypi.org/pypi/scikit-learn/1.7.2/json), [1.9.0 metadata](https://pypi.org/pypi/scikit-learn/1.9.0/json) |
| `sentence-transformers` | `5.6.0` | [Sentence Transformers](https://github.com/huggingface/sentence-transformers): embedding and cross-encoder tooling | Apache-2.0; [release metadata](https://pypi.org/pypi/sentence-transformers/5.6.0/json). Downloaded models have their own licenses. |
| `toml` | `0.10.2` | [toml](https://github.com/uiri/toml): TOML parsing | MIT; [release metadata](https://pypi.org/pypi/toml/0.10.2/json) |
| `torch` | `2.13.0` | [PyTorch](https://github.com/pytorch/pytorch): tensor operations and model execution | `Apache-2.0 AND Apache-2.0 WITH LLVM-exception AND BSD-2-Clause AND BSD-3-Clause AND BSL-1.0 AND MIT`; [release metadata](https://pypi.org/pypi/torch/2.13.0/json). Do not reduce this release's declaration to a single license. |

| Direct development distribution | Exact locked version | Credit / upstream project | Declared license and version-specific evidence |
| --- | --- | --- | --- |
| `black` | `26.5.1` | [Black](https://github.com/psf/black): code formatting | MIT; [release metadata](https://pypi.org/pypi/black/26.5.1/json), [tagged license](https://github.com/psf/black/blob/26.5.1/LICENSE) |
| `mypy` | `2.2.0` | [mypy](https://github.com/python/mypy): static type checking | MIT; [release metadata](https://pypi.org/pypi/mypy/2.2.0/json) |
| `pre-commit` | `4.6.0` | [pre-commit](https://github.com/pre-commit/pre-commit): development hooks | MIT; [release metadata](https://pypi.org/pypi/pre-commit/4.6.0/json). Hook environments can introduce additional dependencies. |
| `ruff` | `0.15.21` | [Ruff](https://github.com/astral-sh/ruff): linting and formatting | MIT; [release metadata](https://pypi.org/pypi/ruff/0.15.21/json) |
| `types-requests` | `2.33.0.20260712` | [typeshed](https://github.com/python/typeshed): Requests type stubs | Apache-2.0; [release metadata](https://pypi.org/pypi/types-requests/2.33.0.20260712/json) |

### What this package inventory does not clear

- The lock includes **transitive dependencies** beyond these direct requirements. For example, SciPy and Hugging Face Transformers contribute numerical/model tooling but are not direct requirements in this `pyproject.toml`. Their full dependency trees have not been reviewed or cleared by this inventory.
- A source package's top-level license is not a complete inventory of its wheels. Numerical, ML, database, OCR, and document-conversion distributions may bundle native libraries, codecs, runtimes, fonts, or other subcomponents under additional licenses. Inspect the actual platform-specific artifact and its `LICENSE`, `NOTICE`, license directories, and distribution metadata before redistribution. Lock hashes identify artifacts; they are not license clearance.
- Docling's MIT software license does not automatically cover separately downloaded layout, table-recognition, OCR, or other model artifacts. Record and review the exact artifacts selected by the conversion pipeline. The historical conversion model revisions are not established here.
- Installing a package is not evidence it was used in a particular result. The current lock is not proof of historical installed versions. Retain the actual environment record for a new run.
- The current [`scripts/legacy_audit.py`](../scripts/legacy_audit.py) and [`scripts/refresh_pilot.py`](../scripts/refresh_pilot.py) import only Python standard-library modules. Their offline operations do not require installation of the heavy benchmark dependency stack; the pilot's explicitly requested live API execution remains subject to service terms. This statement does not exempt a redistributed Python runtime from its own notices.

## Configured downloadable embedding and reranking models

These are the defaults in [config.example.cfg](../config.example.cfg), not authenticated historical model snapshots. Neither setting pins a model revision. Model-card evidence is separate from the Sentence Transformers and PyTorch package licenses.

| Configuration value | Upstream identity and purpose | License evidence |
| --- | --- | --- |
| `[VectorDatabase] embedding_model = all-mpnet-base-v2` | [`sentence-transformers/all-mpnet-base-v2`](https://huggingface.co/sentence-transformers/all-mpnet-base-v2), a 768-dimensional sentence/paragraph embedding model | Its [model card at evidence revision `e8c3b32edf5434bc2275fc9bab85f82640a19130`](https://huggingface.co/sentence-transformers/all-mpnet-base-v2/blob/e8c3b32edf5434bc2275fc9bab85f82640a19130/README.md) declares `apache-2.0`. The card identifies `microsoft/mpnet-base` as its pretrained base and describes the training mixtures. |
| `[Reranking] model_name = cross-encoder/ms-marco-MiniLM-L-6-v2` | The exact configured URL [`cross-encoder/ms-marco-MiniLM-L-6-v2`](https://huggingface.co/cross-encoder/ms-marco-MiniLM-L-6-v2) redirects to canonical [`cross-encoder/ms-marco-MiniLM-L6-v2`](https://huggingface.co/cross-encoder/ms-marco-MiniLM-L6-v2), an MS MARCO passage reranker. Preserve the configured spelling when reporting the configuration and the resolved identity when reporting the artifact. | The [canonical card at evidence revision `233902d25c440f23af6f7d6e94d2946bac0bee0a`](https://huggingface.co/cross-encoder/ms-marco-MiniLM-L6-v2/blob/233902d25c440f23af6f7d6e94d2946bac0bee0a/README.md) declares `apache-2.0` and identifies the MS MARCO ranking task. |

The evidence revisions above are the Hub revisions observed during this documentation review, **not** assertions about weights used in an archived or future run. For actual use, save the resolved model repository ID, commit SHA, weight/tokenizer hashes, model card, license, applicable notices, and retrieval date. Review training-data permissions separately if obtaining or redistributing training datasets; a model-card license does not grant rights to all listed datasets. Also record preprocessing, truncation, pooling, and reranking settings when these affect the reported method.

## Hosted model APIs are a separate rights layer

The Apache-2.0 license of the OpenAI Python SDK grants no license to OpenAI's hosted models, OpenRouter's service, or another provider's weights. OpenAI-compatible API syntax does not imply OpenAI ownership or terms. Start with the [OpenRouter Terms of Service](https://openrouter.ai/terms), its [provider-routing / model-terms guidance](https://openrouter.ai/docs/features/provider-routing#terms-of-service), and the applicable [OpenAI Services Agreement](https://openai.com/policies/services-agreement/) for direct OpenAI service use. Check the agreement actually applicable to the account, route, region, and execution date.

The archive inventory in [reports/legacy-audit.json](../reports/legacy-audit.json) records the following **seven labels across its runs**; this is not a claim that all seven appear in every run. Catalog links identify labels, not immutable deployments. The larger evaluation/judge lists in `config.example.cfg` are example selections, not evidence those models all ran.

| Archived model label | Primary catalog / model reference | Rights distinction and evidence limit |
| --- | --- | --- |
| `deepseek/deepseek-chat-v3.1` | [OpenRouter catalog](https://openrouter.ai/deepseek/deepseek-chat-v3.1); [DeepSeek-V3.1 card](https://huggingface.co/deepseek-ai/DeepSeek-V3.1) | The upstream downloadable DeepSeek-V3.1 card declares MIT for its repository and weights. Hosted access remains governed by the applicable route/provider terms; the archive does not pin the served weight revision. |
| `google/gemini-2.5-flash` | [OpenRouter catalog](https://openrouter.ai/google/gemini-2.5-flash); [Gemini API Additional Terms](https://ai.google.dev/gemini-api/terms) | Hosted model/service, not a downloadable-weight license supplied by this repository. Direct Gemini API terms are a reference, not proof of the contractual route used in the archive. |
| `google/gemini-2.5-flash-lite` | [OpenRouter catalog](https://openrouter.ai/google/gemini-2.5-flash-lite); [Gemini API Additional Terms](https://ai.google.dev/gemini-api/terms) | Same separation of service terms from software licenses; preserve this distinct model label. |
| `gpt-5-mini` | [OpenAI GPT-5 Mini catalog entry on OpenRouter](https://openrouter.ai/openai/gpt-5-mini); [OpenAI Services Agreement](https://openai.com/policies/services-agreement/) | The archive label is unprefixed. Do not silently rewrite it into proof of an OpenRouter route or a dated OpenAI snapshot. No weight license is inferred. |
| `mistralai/mistral-nemo` | [OpenRouter catalog](https://openrouter.ai/mistralai/mistral-nemo); [Mistral-Nemo-Instruct-2407 card](https://huggingface.co/mistralai/Mistral-Nemo-Instruct-2407) | The related downloadable instruct model declares Apache-2.0; this does not replace hosted-service terms or authenticate the archived endpoint's exact artifact. |
| `openai/gpt-4o-mini` | [OpenRouter catalog](https://openrouter.ai/openai/gpt-4o-mini); [OpenAI Services Agreement](https://openai.com/policies/services-agreement/) | Hosted model/service terms apply; the SDK license is not its model license. The label alone does not recover the historical provider route or deployment revision. |
| `qwen/qwen3-coder` | [OpenRouter catalog, titled Qwen3 Coder 480B A35B](https://openrouter.ai/qwen/qwen3-coder); [Qwen3-Coder-480B-A35B-Instruct card](https://huggingface.co/Qwen/Qwen3-Coder-480B-A35B-Instruct) | That downloadable model card declares Apache-2.0. The API alias is not a pinned weight snapshot, and its service terms remain separate. |

For a new run, record requested and returned model identifiers, endpoint, actual provider route where available, timestamp, applicable terms/version and account settings, and any available deployment revision. If routing information is not returned, disclose it as unknown rather than infer it from the label. Evaluate restrictions on inputs, retention, use, publication, and redistribution for the intended activity.

**Historical terms and output rights have not been recovered or cleared.** Current terms/cards do not establish historical contractual rights, ownership of generated answers, permission to republish third-party quotations in those answers, or rights to send bundled framework text to a service. No blanket permission to redistribute archived responses or their inputs follows from this document.

## Research citations and acknowledgements

Cite the benchmark itself using the root citation guidance. Additionally cite the software, methods, and exact model snapshots that materially contributed to the reported experiment. Cite versions actually used, not merely the newest version or every item installed. A package/paper citation does not substitute for a model-card snapshot citation, and none substitutes for retaining license notices.

Useful canonical research references:

- **Docling:** Christoph Auer et al. (2024), *Docling Technical Report*, [arXiv:2408.09869](https://arxiv.org/abs/2408.09869). Cite this report and the [Docling tool](https://github.com/docling-project/docling) with the conversion version when Docling generated research inputs; record separately the conversion models used.
- **Sentence Transformers:** Nils Reimers and Iryna Gurevych (2019), *Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks*, EMNLP-IJCNLP, [ACL Anthology D19-1410](https://aclanthology.org/D19-1410/). Cite alongside the embedding/reranker model card, not as the identity of either exact checkpoint.
- **MPNet architecture:** Kaitao Song, Xu Tan, Tao Qin, Jianfeng Lu, and Tie-Yan Liu (2020), *MPNet: Masked and Permuted Pre-training for Language Understanding*, [arXiv:2004.09297](https://arxiv.org/abs/2004.09297). This credits the pretrained architecture identified by the `all-mpnet-base-v2` card; the fine-tuned embedding snapshot still needs its own citation.
- **MiniLM architecture:** Wenhui Wang et al. (2020), *MiniLM: Deep Self-Attention Distillation for Task-Agnostic Compression of Pre-Trained Transformers*, [arXiv:2002.10957](https://arxiv.org/abs/2002.10957). Cite when discussing the reranker's architecture, without presenting the architecture paper as a release record for the MS MARCO fine-tuned checkpoint.
- **NumPy:** Charles R. Harris et al. (2020), *Array programming with NumPy*, Nature 585, 357–362, [doi:10.1038/s41586-020-2649-2](https://doi.org/10.1038/s41586-020-2649-2).
- **scikit-learn:** Fabian Pedregosa et al. (2011), *Scikit-learn: Machine Learning in Python*, JMLR 12(85), 2825–2830, [publisher record](https://jmlr.org/papers/v12/pedregosa11a.html).
- **PyTorch:** Adam Paszke et al. (2019), *PyTorch: An Imperative Style, High-Performance Deep Learning Library*, [arXiv:1912.01703](https://arxiv.org/abs/1912.01703).
- **Chroma, SDKs, configuration/HTTP libraries, and development tools:** acknowledge the upstream projects linked in the tables and include their exact used release versions in an environment record. Use an upstream preferred citation if the chosen release supplies one; no paper or DOI is invented here for these tools.

For a software or model snapshot without a preferred scholarly citation, a suitable citation records the upstream author/organization, repository/model title, release version or commit SHA, canonical URL, and access date. A reproducibility appendix should identify the project commit, environment/lock actually used, model snapshots or unresolved API aliases, and which tools produced which artifacts.

## Redistribution obligations and remaining evidence gaps

When distributing packages, containers, wheels, model weights, or modified upstream files, preserve their copyright and license texts, required `NOTICE` content, attribution and change notices, and subcomponent notices as required by the applicable licenses. Keep the corresponding evidence with the exact distributed artifacts; links in this inventory are not a replacement for required included notices. Separately check whether a license requires source availability or other distribution actions for any transitive/bundled component.

This review does **not** establish complete transitive or native-component clearance, historical installed environments, historical model/Docling artifact hashes, historical provider contracts/routes, training-dataset redistribution rights, or archived-answer redistribution rights. The source/framework corpus already present in the repository has a separate rights review; see [THIRD_PARTY_NOTICES.md](../THIRD_PARTY_NOTICES.md). Nothing here assigns that corpus the licenses of the tools used to convert or retrieve it.

## Citation-maintenance tooling used in this refresh

These are isolated documentation-validation tools, not additional benchmark dependencies or proof of historical execution:

- **cffconvert 2.0.0**, Jurriaan H. Spaaks and contributors: validated `CITATION.cff` against CFF 1.2.0 and rendered a BibTeX citation. [Version-specific metadata](https://pypi.org/pypi/cffconvert/2.0.0/json) declares the Apache Software License classifier; retain the distribution's actual license/notice if redistributing the tool. [Upstream project](https://github.com/citation-file-format/cff-converter-python).
- **bibtexparser 1.4.3**, Francois Boulogne and other contributors: parsed both bibliography files during the coverage smoke check. [Version-specific metadata](https://pypi.org/pypi/bibtexparser/1.4.3/json) declares **LGPLv3 or BSD, at the user's choice**; consult that release's COPYING for the actual grants and distribution obligations. [Upstream project](https://github.com/sciunto-org/python-bibtexparser).
- **Citation File Format 1.2.0:** [upstream schema guide](https://github.com/citation-file-format/citation-file-format/blob/main/schema-guide.md) defines the machine-readable citation metadata, not the license of the work cited.

The validation tools ran through isolated `uv` environments using Python 3.12; they were not added to `pyproject.toml` or the benchmark lock. Python/runtime and environment-manager redistribution have their own notices; see the [Python license documentation](https://docs.python.org/3/license.html) and [uv upstream licensing](https://github.com/astral-sh/uv#license). No tool binaries, weights, or third-party license texts were bundled by this documentation update.
