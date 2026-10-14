# Framework sources, citations, and reuse review

This inventory covers **13 bundled Markdown documents in 11 framework folders**. It identifies the editions actually represented in this checkout, not whichever edition a publisher now recommends. These third-party texts are already present in the repository; adding attribution does **not** clear their existing distribution, conversion, inclusion in release archives, or use with an LLM.

See the repository's [third-party notices](../../THIRD_PARTY_NOTICES.md), [framework license notice](LICENSE), and [BibTeX references](../../doc/framework-references.bib). The root project license does not replace third-party rights. This inventory is an evidence record and release-review checklist, not legal advice or a grant of rights.

## Provenance and release rules

- Each folder's `metadata.toml` records `conversion_method = "docling"`, `original_format = "PDF"`, and `converted_date = "2025"`. [ADR 0002](../../doc/architecture/decisions/0002-using-docling-to-prepare-context-for-evals.md), dated August 11, 2025, records the decision to use Docling-converted Markdown. Its historical `docling/` directory name differs from the present layout.
- The transformation recorded for **all 13 documents** is PDF-to-Markdown conversion through Docling. This does not establish faithful or complete conversion: tables, cover pages, copyright notices, and reading order need comparison with the source. The metadata does not identify the exact download date, original PDF hash, Docling version/options, or subsequent edits. A year alone is not a reproducible conversion timestamp.
- Publisher URLs and DOIs below identify the source work; they are **not verified historical download provenance**. General landing pages in metadata cannot establish the exact bytes originally used. Even a revision-specific DOI may serve corrected content later.
- **Conditional release** means a reuse basis has been identified, but source matching, retained notices, third-party exceptions, and the actual proposed distribution/use still require review. **Hold** means no adequate permission/exception for the bundled form has been established; do not treat a citation as clearance. These labels do not themselves remove files or change release packaging.
- U.S. federal works are not automatically equivalent to every item on a `.gov` site. [17 U.S.C. §§101 and 105](https://www.copyright.gov/title17/92chap1.html#105) address works prepared by federal officers/employees in their official duties; transferred copyrights and third-party contributions require separate consideration. This rule is not a blanket license for state, private, or foreign works.
- Primary rights pages were consulted on October 13, 2026. Current terms are evidence for release review, not proof of the terms accepted when an unknown historical download occurred. No educational/research-use exemption or worldwide public-domain status is asserted.

## 1. NIST Cybersecurity Framework 2.0

- **Local path:** [`data/cyber-frameworks/nist-csf/NIST.CSWP.29.md`](nist-csf/NIST.CSWP.29.md).
- **Document:** *The NIST Cybersecurity Framework (CSF) 2.0*, NIST Cybersecurity White Paper 29, February 26, 2024.
- **Author/publisher:** National Institute of Standards and Technology (NIST).
- **Authoritative identifier:** [doi:10.6028/NIST.CSWP.29](https://doi.org/10.6028/NIST.CSWP.29). **BibTeX:** `framework_nist_csf_2024`.
- **Local evidence / metadata:** title and date at lines 1–7; recommended corporate-author citation at lines 505–511. Metadata's version 2.0 agrees; its general cyberframework URL is not an exact download record.
- **Rights:** [NIST Technical Series Publications policy](https://www.nist.gov/open/license#techpubs) states that NIST employee works are not copyright-protected in the United States and grants specified worldwide reprint/derivative-work rights to the extent NIST can assert them, with third-party exceptions. NIST requests its recommended citation and the credit: “Republished courtesy of the National Institute of Standards and Technology.” This credit also applies to the three NIST entries below.
- **Disposition:** **Conditional release** under the applicable NIST publication policy, with citation, conversion notice, source comparison, and review of separately credited material. This is the dated CSF 2.0 publication, not a certification or assurance of current compliance.

## 2. NIST SP 800-53, Revision 5

- **Local path:** [`data/cyber-frameworks/nist-800-53/NIST.SP.800-53r5.md`](nist-800-53/NIST.SP.800-53r5.md).
- **Document:** *Security and Privacy Controls for Information Systems and Organizations*, NIST SP 800-53, Revision 5, September 2020, **including updates as of December 10, 2020**.
- **Author:** Joint Task Force. **Publisher:** NIST.
- **Authoritative identifier:** [doi:10.6028/NIST.SP.800-53r5](https://doi.org/10.6028/NIST.SP.800-53r5). **BibTeX:** `framework_nist_80053r5_2020`.
- **Local evidence / metadata:** lines 1–21 identify author, revision, and update cutoff; the Authority section, line 35, states that the publication is not subject to U.S. copyright and appreciates attribution. Metadata says only Revision 5 and omits the update cutoff; do not silently substitute a later control-catalog release or errata state.
- **Rights:** local Authority notice and [NIST Technical Series policy](https://www.nist.gov/open/license#techpubs), including third-party exceptions and the NIST credit above.
- **Disposition:** **Conditional release** with the December 2020 snapshot clearly labeled, retained notices, and comparison to that source version. Revision number alone does not establish that this is the latest updated text.

## 3. NIST SP 800-171, Revision 3

- **Local path:** [`data/cyber-frameworks/nist-800-171/NIST.SP.800-171r3.md`](nist-800-171/NIST.SP.800-171r3.md).
- **Document:** *Protecting Controlled Unclassified Information in Nonfederal Systems and Organizations*, NIST SP 800-171, Revision 3, May 2024.
- **Authors:** Ron Ross and Victoria Pillitteri. **Publisher:** NIST.
- **Authoritative identifier:** [doi:10.6028/NIST.SP.800-171r3](https://doi.org/10.6028/NIST.SP.800-171r3). **BibTeX:** `framework_nist_800171r3_2024`.
- **Local evidence / metadata:** lines 3–17 and recommended citation at lines 47–49; Authority notice at line 37. Metadata's Revision 3 agrees. The local publication history explicitly supersedes Revision 2; that does not determine which revision any particular contract requires.
- **Rights:** local U.S. non-copyright notice and [NIST Technical Series policy](https://www.nist.gov/open/license#techpubs), including third-party exceptions and the NIST credit above.
- **Disposition:** **Conditional release** with notices and conversion/source checks. Identify this final May 2024 publication, rather than treating all contractual CUI requirements as automatically migrated to it.

## 4. NIST SP 800-66, Revision 2

- **Local path:** [`data/cyber-frameworks/hipaa/NIST.SP.800-66r2.md`](hipaa/NIST.SP.800-66r2.md).
- **Document:** *Implementing the Health Insurance Portability and Accountability Act (HIPAA) Security Rule: A Cybersecurity Resource Guide*, NIST SP 800-66, Revision 2, February 2024.
- **Author:** Jeffrey A. Marron. **Publisher:** NIST.
- **Authoritative identifier:** [doi:10.6028/NIST.SP.800-66r2](https://doi.org/10.6028/NIST.SP.800-66r2). **BibTeX:** `framework_nist_80066r2_2024`.
- **Local evidence / metadata:** lines 1–21 and recommended citation at lines 53–55; Authority notice at line 41; Disclaimer at lines 93–95. Folder metadata groups this guide with the NPRM under “HIPAA Security Rule”; neither document should be mistaken for the operative regulation itself. The HHS landing URL does not identify this NIST publication.
- **Rights:** local U.S. non-copyright notice and [NIST Technical Series policy](https://www.nist.gov/open/license#techpubs), including third-party exceptions and the NIST credit above.
- **Disposition:** **Conditional release** with notices/source checks and its **guidance, not law** status preserved. The guide expressly does not modify federal law and does not guarantee compliance.

## 5. HIPAA Security Rule proposed rule, FR Doc. 2024-30983

- **Local path:** [`data/cyber-frameworks/hipaa/2024-30983.md`](hipaa/2024-30983.md).
- **Document:** *HIPAA Security Rule To Strengthen the Cybersecurity of Electronic Protected Health Information*, notice of proposed rulemaking and notice of Tribal consultation; Federal Register **90 FR 898–1022, January 6, 2025**, FR Doc. 2024-30983, RIN 0945-AA22.
- **Author/issuing agency:** U.S. Department of Health and Human Services, Office for Civil Rights, Office of the Secretary.
- **Authoritative source:** [GovInfo publication record](https://www.govinfo.gov/app/details/FR-2025-01-06/2024-30983); [Federal Register dated text](https://www.federalregister.gov/documents/full_text/text/2025/01/06/2024-30983.txt). **BibTeX:** `framework_hhs_hipaa_nprm_2025`.
- **Local evidence / metadata:** title, agency, and proposed-rule action at lines 1–15; comments due March 7, 2025 at lines 17–19. **Conflict:** metadata's “2024 NPRM” and the identifier's 2024 prefix are not the Federal Register publication year, which is 2025. The local front matter is incomplete as a bibliographic record; the dated official record supplies the publication date and pages.
- **Rights:** federal agency rulemaking text has a U.S. federal-work basis under [17 U.S.C. §105](https://www.copyright.gov/title17/92chap1.html#105), subject to separately protected incorporated material; this is not an independently granted open-source license.
- **Disposition:** **Conditional release** after federal-work/third-party and conversion review, labeled **proposed rule, not current law**. This citation does not determine the present outcome of the rulemaking. Use authoritative regulations and subsequent official actions for any current-law claim.

## 6. GDPR, original Official Journal text

- **Local path:** [`data/cyber-frameworks/gdpr/CELEX_32016R0679_EN_TXT.md`](gdpr/CELEX_32016R0679_EN_TXT.md).
- **Document:** *Regulation (EU) 2016/679 of the European Parliament and of the Council of 27 April 2016 on the protection of natural persons with regard to the processing of personal data and on the free movement of such data, and repealing Directive 95/46/EC (General Data Protection Regulation)*; original Official Journal text, **OJ L 119, May 4, 2016, pp. 1–88**; CELEX 32016R0679.
- **Authors:** European Parliament and Council of the European Union. **Publisher:** Official Journal of the European Union / Publications Office of the European Union.
- **Authoritative source:** [EUR-Lex ELI, original Official Journal edition](https://eur-lex.europa.eu/eli/reg/2016/679/oj); [CELEX record](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32016R0679). **BibTeX:** `framework_eu_gdpr_2016`.
- **Local evidence / metadata:** title, adoption date, and institutions at lines 5–11. Metadata's Regulation 2016/679 agrees. This original-text identifier is not a dated consolidated version containing all later corrigenda or amendments.
- **Rights:** the [EUR-Lex legal notice](https://eur-lex.europa.eu/content/legal-notice/legal-notice.html) permits commercial and non-commercial reuse of legal documents unless otherwise specified, with exceptions for third-party content and excluded intellectual-property rights. Its separate CC BY 4.0 statement for editorial content, summaries, and consolidated texts must not be confused with the basis for this original legal text; its CC0 metadata notice is not a license for the whole document.
- **Disposition:** **Conditional release** under the applicable legal-document reuse notice, retaining attribution and identifying the conversion. The Markdown is not an authentic Official Journal publication or a verified current consolidation; compare against the official text before legal use.

## 7. AICPA Trust Services Criteria

- **Local path:** [`data/cyber-frameworks/soc2-trust-services/Trust-services-criteria.md`](soc2-trust-services/Trust-services-criteria.md).
- **Document:** *2017 Trust Services Criteria for Security, Availability, Processing Integrity, Confidentiality, and Privacy (With Revised Points of Focus – 2022)*, TSP Section 100.
- **Author:** American Institute of Certified Public Accountants (AICPA), Assurance Services Executive Committee (ASEC). **Publisher:** AICPA.
- **Authoritative source:** [publisher's edition-specific resource](https://www.aicpa-cima.com/resources/download/2017-trust-services-criteria-with-revised-points-of-focus-2022). **BibTeX:** `framework_aicpa_tsc_2022`.
- **Local evidence / metadata:** title at lines 1–7; ASEC attribution at line 11; lines 15–25 clarify that the 2022 changes concern points of focus and do not alter the 2017 criteria. Metadata agrees. The publisher resource is dated September 30, 2023; that page date does not replace the document's 2017 criteria / 2022 revision identity. The generic historical SOC 2 metadata link does not prove a download source.
- **Rights:** the local file includes a **COSO ©2019, all rights reserved** attribution at line 56. A complete AICPA copyright/license notice was not found in the converted text; absence is not permission. The publisher explicitly offers a download “with Copyright Information.” Its [Terms & Conditions](https://www.aicpa-cima.com/help/terms-and-conditions), §§2.1–2.3, restrict copying, modification, and republication, and explicitly object to AI training and inclusion in LLM knowledge bases; §3.3 reserves text/data-mining rights subject to applicable law. Current website terms do not establish historical acquisition terms or the legal outcome for this particular use.
- **Disposition:** **HOLD: permission/legal review required** for the existing bundled conversion, redistribution, and intended LLM/benchmark use, including any separately protected COSO material. Free account access and a bibliography are not redistribution or AI-use permission. Obtain applicable document terms and a written permission or documented legal basis covering the actual uses before clearing this text for release.

## 8. PCI DSS, Version 4.0.1

- **Local path:** [`data/cyber-frameworks/pci-dss/PCI-DSS-v4_0_1.md`](pci-dss/PCI-DSS-v4_0_1.md).
- **Document:** *Payment Card Industry Data Security Standard: Requirements and Testing Procedures*, Version 4.0.1, June 2024.
- **Author/publisher:** PCI Security Standards Council, LLC (PCI SSC).
- **Authoritative source:** [publisher's version-specific document](https://docs-prv.pcisecuritystandards.org/PCI%20DSS/Standard/PCI-DSS-v4_0_1.pdf), linked by its [Document Library](https://www.pcisecuritystandards.org/document_library/). **BibTeX:** `framework_pci_dss_401_2024`.
- **Local evidence / metadata:** title, edition, and date at lines 1–7; change history at lines 23–24. Metadata agrees but points only to the publisher home page. No complete publisher copyright/license notice was located in the Markdown.
- **Rights:** this is a privately published standard, not a U.S. government work. The indexed publisher document presents a PCI SSC License Agreement; the direct document request returned HTTP 403 during this review, so its complete applicable grant was not verified. The publisher provides a [Material License Agreement request](https://programs.pcissc.org/mla_registration.aspx). No permission for public redistribution of this converted document has been established.
- **Disposition:** **HOLD: obtain and review the applicable document license and redistribution/conversion permission or other documented legal basis**, including the intended benchmark/LLM use. Restore required notices if release is authorized. Do not infer a right to republish from public download availability, the industry-standard designation, or attribution.

## 9. CMMC Assessment Guide, Level 1

- **Local path:** [`data/cyber-frameworks/cmmc/AssessmentGuideL1.md`](cmmc/AssessmentGuideL1.md).
- **Document:** *CMMC Assessment Guide: Level 1*, Version 2.13, September 2024; DoD-CIO-00002 (ZRIN 0790-ZA18).
- **Author/publisher:** U.S. Department of Defense, Chief Information Officer.
- **Authoritative source:** [DoD CIO edition-specific PDF](https://dodcio.defense.gov/Portals/0/Documents/CMMC/AssessmentGuideL1v2.pdf). **BibTeX:** `framework_dod_cmmc_assessment_l1_2024`.
- **Local evidence / metadata:** edition/identifier at line 1; notices at lines 3–7 and Level 1 purpose at lines 46–58. The cover title is not preserved in the local opening; the official PDF's indexed cover identifies it. A direct PDF request returned HTTP 403. Metadata's version 2.13 agrees; “CMMC 2.0” program terminology must not replace the guide's own version.
- **Rights:** local Distribution Statement A approves public release. The federal-work basis in [17 U.S.C. §105](https://www.copyright.gov/title17/92chap1.html#105) applies to qualifying government-authored portions; a distribution statement alone does not erase third-party copyright.
- **Disposition:** **Conditional release** after source/notice and third-party review. Preserve the notice that the guide does **not have the force and effect of law**; it explains requirements and is not itself the CMMC regulation.

## 10. CMMC Scoping Guide, Level 1

- **Local path:** [`data/cyber-frameworks/cmmc/ScopingGuideL1v2.md`](cmmc/ScopingGuideL1v2.md).
- **Document:** *CMMC Scoping Guide: Level 1*, Version 2.13, September 2024; DoD-CIO-00005 (ZRIN 0790-ZA21).
- **Author/publisher:** U.S. Department of Defense, Chief Information Officer.
- **Authoritative source:** [DoD CIO edition-specific PDF](https://dodcio.defense.gov/Portals/0/Documents/CMMC/ScopingGuideL1v2.pdf). **BibTeX:** `framework_dod_cmmc_scoping_l1_2024`.
- **Local evidence / metadata:** edition/identifier at line 1; notices at lines 3–7; purpose at lines 9–15. As with the assessment guide, the official indexed PDF cover supplies the title missing from the local opening; direct PDF retrieval returned HTTP 403. Metadata agrees on 2.13; the filename's `v2` is not the full edition number.
- **Rights:** local Distribution Statement A approves public release and unlimited distribution; qualifying federal-work portions fall under [17 U.S.C. §105](https://www.copyright.gov/title17/92chap1.html#105), with separate review for protected third-party material.
- **Disposition:** **Conditional release** with notices and source comparison. Preserve its express **guidance, not law** disclaimer; do not substitute newer guide content without changing the benchmark's source identity.

## 11. FBI CJIS Security Policy, Version 5.8

- **Local path:** [`data/cyber-frameworks/cjis/CJIS-Security-Policy_v5-8_20190601.md`](cjis/CJIS-Security-Policy_v5-8_20190601.md).
- **Document:** *Criminal Justice Information Services (CJIS) Security Policy*, Version 5.8, June 1, 2019; CJISD-ITS-DOC-08140-5.8.
- **Author/issuer:** U.S. Department of Justice, Federal Bureau of Investigation, Criminal Justice Information Services Division; prepared by the CJIS Information Security Officer, approved by the CJIS Advisory Policy Board.
- **Authoritative source:** [FBI's dated Version 5.8 PDF](https://www.fbi.gov/file-repository/cjis/cjis-security-policy_v5-8_20190601.pdf). **BibTeX:** `framework_fbi_cjis_58_2019`.
- **Local evidence / metadata:** title/edition/roles at lines 1–15. Metadata agrees. **Outdated edition:** the FBI also publishes [Version 6.0, December 27, 2024](https://le.fbi.gov/file-repository/cjis_security_policy_v6-0_20241227.pdf); this inventory cites 5.8 because that is the bundled text, not because it is current.
- **Rights:** local §1.5, lines 368–370, expressly states that Version 5.0 and later may be posted and shared without restrictions. This is a document-specific distribution basis, alongside the qualifying federal-work rule; review any independently protected third-party material and avoid endorsement implications.
- **Disposition:** **Conditional release** with the distribution statement retained and the text labeled as the **historical 2019 edition**. Do not describe it as the current CJIS policy or silently replace it in reproducibility citations.

## 12. New Jersey Statewide Information Security Manual

- **Local path:** [`data/cyber-frameworks/new-jersey-state/NJ_Statewide_Information_Security_Manual_NOGLOSSARY.md`](new-jersey-state/NJ_Statewide_Information_Security_Manual_NOGLOSSARY.md).
- **Document:** *Executive Branch of New Jersey State Government: Statewide Information Security Manual*; **effective February 2, 2021**. No numbered edition or reliable later revision date is established for the local conversion.
- **Corporate author:** Executive Branch of New Jersey State Government. **Publisher:** New Jersey Office of Homeland Security and Preparedness; the local PM-07 assigns maintenance to the State CISO within NJCCIC.
- **Authoritative source:** [state-hosted 2021 manual](https://www.nj.gov/it/docs/ps/2021-Statewide_Information_Security_Manual.pdf); its cover explicitly identifies the publisher and effective date. **BibTeX:** `framework_nj_sism_2021`.
- **Local evidence / metadata:** cover title at lines 1–5; PM-03, line 415, states the effective date; PM-07, lines 452–467, describes maintenance and changes. **Conflict:** metadata version “Current” is unsupported by this dated text. The `_NOGLOSSARY` filename indicates a potentially abridged local artifact, not an official edition designation; the exact omissions and equivalence to the official PDF have not been established. Cite the 2021 effective-date identity without claiming complete reproduction or a latest revision.
- **Rights:** [New Jersey's Conditions of Use, §F](https://www.nj.gov/nj/facts/legal.shtml) allows viewing, copying, and distributing State information unless a particular restriction applies, but expressly disclaims assurance against third-party copyright/trademark claims; §G separately restricts state/agency seals and logos. The federal §105 rule is not a state-government copyright exemption. Local PM-06 also describes incorporated external standards.
- **Disposition:** **HOLD pending source/version and scope-of-rights review** for the potentially abridged conversion, departmental/document-specific conditions, and embedded third-party material. The general state reuse policy is relevant evidence, not proof that this exact modified artifact is cleared. Resolve the “Current” claim before publication metadata is relied upon.

## 13. FedRAMP RFC-0012 vulnerability-management proposal

- **Local path:** [`data/cyber-frameworks/fedramp/0012-vulnerability-management.md`](fedramp/0012-vulnerability-management.md).
- **Document:** *RFC-0012 Continuous Vulnerability Management Standard*, public-comment **draft opened July 15, 2025**, closing date August 21, 2025; short name `rfc-0012-vulnerability-management`.
- **Author/issuer:** Federal Risk and Authorization Management Program (FedRAMP), U.S. General Services Administration.
- **Authoritative source:** [FedRAMP's July 15, 2025 RFC discussion #59](https://github.com/FedRAMP/community/discussions/59), which links the [RFC PDF](https://github.com/FedRAMP/rfcs/raw/main/rfc/assets/0012-vulnerability-management.pdf). These mutable upstream URLs do not pin the historical downloaded bytes. **BibTeX:** `framework_fedramp_rfc0012_2025`.
- **Local evidence / metadata:** title/front matter at lines 1–17; proposal description at line 33; applicability warning at lines 53–55. **Conflicts:** local status is “Open,” while the official discussion is now marked closed; metadata describes a standard without indicating draft status. Closing a comment period does not make this draft final. The publisher discussion also provides native Markdown/Word, while local metadata records a PDF/Docling workflow; that metadata alone does not identify which PDF bytes were converted.
- **Rights:** qualifying federal-authored text has a basis under [17 U.S.C. §105](https://www.copyright.gov/title17/92chap1.html#105); no document-specific open license was located in the local draft. GitHub hosting alone supplies no general redistribution license, and public comments or third-party contributions must not be swept into the federal-work assumption.
- **Disposition:** **Conditional release** for historical research only after confirming the source and federal/third-party rights basis, preserving draft status and conversion notice. The document explicitly says it does not apply to any FedRAMP authorization and must not be used in draft form. Do not present these requirements as an operative authorization standard.

## Publication blockers and checks

1. **Existing bundled TSC and PCI DSS require clearance**, not just added credits. Establish permission or a documented applicable legal basis for conversion, full-text public redistribution, model-provider transmission, benchmark/evaluation use, and any proposed training use. These are different activities; permission for one does not establish the others. Review outputs, archives, and exports that reproduce the same material.
2. **New Jersey needs exact-artifact and rights review.** Its 2021 effective date contradicts an unqualified “Current” label, and the local no-glossary variant lacks a proven source/change record.
3. **Preserve legal status and historical editions.** The HIPAA NPRM is published in 2025 and is not current law; FedRAMP RFC-0012 is a draft; CMMC documents and NIST's HIPAA guide are guidance; CJIS 5.8 is superseded; GDPR is the original 2016 text; NIST 800-53 has a December 2020 update cutoff.
4. **Before any cleared release**, record source retrieval dates and hashes, original publication notices, Docling version/settings and conversion changes; compare cover pages, tables, omissions, and rights notices with the exact permitted originals. Reconcile folder metadata with this inventory rather than allowing generic URLs or “Current” to stand in for provenance. Source URLs identified here are not proof of that comparison.
5. **Validate the citation artifacts** with a BibTeX parser and check the one-to-one mapping of the 13 citation keys, paths, and editions. This refresh's parser/coverage smoke verified all 13 mappings and local link targets. Publisher checks can require authentication or encounter the HTTP 403 responses noted above. These structural checks do not establish conversion accuracy, legal clearance, or historical download provenance.
