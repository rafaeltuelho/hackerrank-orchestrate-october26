# Public sample audit and workflow coverage

The 32 public samples are a useful branch and serialization suite, but they are not sufficient evidence of full challenge coverage. They exercise all 15 allowed operations, yet contain no NOT_APPLICABLE case, no canonical image citation, and several expected resource references that cannot be independently linked to a subject using the inspected evidence available at the cutoff. Use them to shape the workflow, then add explicit edge cases and resolve the evidence-contract questions below.

This is a manual exercise, not a trained solver, prediction run, or measured accuracy result. No hidden answers, generator files, or organizer internals were inspected. Dataset files and solution code were not changed.

## Deliverables and method

- [Case exercises](case_exercises.md): every request, identity route, evidence, policy treatment, risk, exact expected step sequence, and observed limitation.
- [Case matrix](case_matrix.csv): 32 sortable rows summarizing the exercises.
- [Coverage counts](coverage_counts.json): machine-readable aggregate counts.

The review read all 32 request texts and public expected outputs; resolved request emails against current identities and audit history; searched every text/SQL/JSON/log evidence file with exact identifier boundaries; correlated log trace IDs; extracted all four PDFs; OCRed all eleven PNGs; and visually inspected the matching connector/reference/storage screenshots and relevant PDF pages. Main evidence observations were compared with expected answers. Canonical resource IDs were used as diagnostic search seeds to test support, never as prediction inputs. An occurrence search is not a subject-link proof, and OCR misses remain possible. No numerical prediction-accuracy claim is made.

Citations in case exercises link to exact text locations when possible. PDF extraction line numbers are not treated as physical source lines. Readback state, subject attribution, policy applicability, and evidence availability are kept separate.

## Aggregate coverage

| Dimension | Observed sample coverage | What it does not establish |
|---|---|---|
| Expected outcomes | 22 INCOMPLETE, 10 COMPLETE | Zero NOT_APPLICABLE or uncertain-authorization examples |
| Expected steps | 193: 41 findings, 41 remediation, 111 verification | Fixed step counts per case are inappropriate; range is 1–14 |
| Operations | All 15 allowed operations | Operation coverage does not imply all policy conditions or combinations |
| Languages | English 29, Spanish 1, French 1, Japanese 1 | Multilingual negation, mixed intent, ambiguity and other languages |
| Identity | All 32 exact current/history matches; 3 historical-request emails (10,29,30); 7 subjects have history | No sample exact lookup failure or multi-subject collision |
| Historical fields | Email/hash transitions and phone changes | Phone-only discovery, name history, reassigned/shared identifiers |
| Canonical citations | 13 evidence files: 4 SQL, 4 JSON, 3 logs, 1 TXT, 1 PDF | No image citation; limited variety within each parser |
| Temporal range | Sample audit cutoffs Sep3–Oct1, 2026 | Much narrower than the evaluation request range Jan29–Oct1 |
| Flow/restore behavior | Active and disabled flow; unsafe and blocked restore | No incomplete sample combines both active flow and unsafe restore; no dependency cycles |
| Replicas | Primary/failover and primary/read-replica comparisons | Not every topology, cross-replica conflict pattern, or missing-snapshot condition |
| Output structure | All 32 public answers pass checked field, numbering, ordering, evidence-ID and capture-cutoff rules | Syntactic validity is not evidence sufficiency |

The parent independently checked evaluation metadata: 518 evaluation requests, zero case-ID overlap with samples, 20 unmatched by exact current-email plus historical-email lookup, 95 historical-only matches, and no multiple-user exact matches. These are bounded lookup statistics, not unresolved-identity or outcome labels. Normalization or other participant evidence may resolve unmatched requests. No hidden outcome distribution was inferred.

Policy coverage is strong for USER_PROFILE, SEARCH_INDEX_ENTRY, SUPPORT_MESSAGE, SUPPORT_ATTACHMENT, ANALYTICS_PROFILE, USER_EXPORT, SECURITY_AUDIT_LOG, BACKUP_ARCHIVE, and ACCOUNT_TOMBSTONE. Contact-record cases 10/12 suggest SECONDARY_IDENTIFIER or MARKETING_PROFILE treatment, but explicit category metadata is thin. CACHE_ENTRY, PRODUCT_TELEMETRY, EMAIL_DELIVERY_LOG, and a fully grounded active-legal-hold decision are not clearly exercised by canonical sample steps. Retention-boundary, expired-hold and missing-required-record cases are absent.

## What the exercises establish

1. **Triage needs an audit-of-prior-deletion branch.** Requests 21 and 25–28 ask to verify a prior deletion. Public answers treat them as deletion-audit cases, not NOT_APPLICABLE. Triage must distinguish those from access/export/correction/marketing-only requests. None of the latter is present in the 32 samples.
2. **Identity is a graph with time, not a single email filter.** Case10 uses two email/hash transitions and a trace join to an old contact; case12 matches an old hash; cases29/30 receive historical request emails and find current-email evidence. Exact boundaries avoid user_48/user_480 collisions.
3. **State needs provenance and scope.** A profile absent in a primary table can survive in a failover/read replica (5,16). A query returning zero rows is not the same as our search finding no string. Store observed state, source table/process, observation time, capture time and subject link independently.
4. **A system name is not a policy category.** Case12's analytics_9914 is expected to be deleted; its contact_lookup/email_opt_in event suggests a contact/marketing record. Blindly mapping analytics_platform to ANONYMIZE would fail. Case10 likewise needs contact-record treatment, not a blanket support-message redaction rule.
5. **Correct retention includes stable references.** Cases31/32 differentiate a compliant stable tombstone from one still exposing name/email/phone/hash. A DELETED status does not establish redaction. Backups are retained with blocked restore, not automatically deleted.
6. **Canonical ordering is deterministic but not a dependency graph.** Every sample follows phase then listed operation order then system/resource lexical order. Cases16/24 place account deletion before search deletion. Do not invent a dependency based on resource names; maintain actual dependency edges separately. Multiple independent searches can still run in parallel.
7. **Output verification covers more than remediation.** Incomplete answers check account absence and retained security records even when only a search entry or connector needs remediation. Coverage obligations must be tracked throughout the case rather than derived only from the remediation list.

## Evidence and contract questions

These are bounded findings requiring clarification or additional grounded evidence. They are not permission to memorize canonical references or to use post-cutoff data.

### Case20: the original gap remains

[evidence_94 search readback](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/evidence/logs/resource_lookup_trace_20260926_103856.log:8) links search_4262 to the request email and returns one hit. The [connector readback](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/evidence/logs/resource_lookup_trace_20260926_103856.log:40) links data_flow_1770 and shows enabled=true. The manifest capture is before audit_at; INCOMPLETE and the two findings are supported.

[activity_3734](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/system_activity.csv:3735) names account_5037 and reports FAILED, but contains no subject ID, email or case ID. It cannot independently establish membership or current account state. audit_record_5569 was not found outside sample_output in any searched participant text, extracted PDF or image OCR. Thus the expected future checks on these IDs are not fully grounded by this review. Similar security-reference gaps occur for case18; cases23/24/29/30 have such security records in evidence_02, captured after their cutoff.

### Observed compliant state is not proof of case membership

For case03, [analytics_9406 readback](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/evidence/logs/resource_lookup_trace_20260926_103856.log:42) has lookup_key=null and null user identifiers. Its state is compatible with anonymization, but no admissible subject-to-resource link was found. The corresponding activity is likewise resource-only. Cases04,21,25–28 show the same distinction for anonymous analytics; several absent-profile readbacks also lack subject lookup keys.

For cases01/02/04, the complete profile-table export in evidence_54 can support subject absence within those tables without a literal resource match. It does not by itself provide the precise expected account ID. Completeness and resource attribution are separate requirements.

### Capture time versus observation time needs an explicit contract

[evidence_02](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/evidence/records/customer_data_snapshot_bundle_20260917.json) is exported/captured Sep17 but contains snapshots dated Sep9 and Sep15 as well as Sep17. [evidence_06](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/evidence/logs/structured_service_events_eu_west_20260918.log) is captured Sep18 but contains Sep16 observations relevant to case09. Under AGENTS.md's explicit prohibition on citing evidence captured after audit_at, these files are inadmissible for the earlier cases, including as identity bridges. A different historical-record admissibility rule would change what can be reconstructed; do not silently switch interpretations.

Case26's stale embedded profile and case27's future profile demonstrate different temporal hazards. Case28's similar-email decoy is in the late file, so that sample alone does not robustly test an admissible contemporaneous decoy.

### Older related artifacts raise scope questions

- Case07: [activity_4007](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/system_activity.csv:4008), dated Feb13, explicitly links object_19/delivery_confirmation_19.pdf exclusively to user_07. [evidence_46](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/evidence/images/object_storage_browser_20260213.png), captured Feb13, visually shows that file in support-attachments storage. The Sep12 expected answer contains only support_001, a different delivery-correction PDF. The sources establish a prior subject-owned attachment candidate; they do not establish equivalence, a later deletion, or continued presence at Sep12. This needs investigation/scope treatment, not an automatic extra finding.
- Case17: [activity_4011](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/system_activity.csv:4012) links tombstone_17 to user_17. [evidence_42](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/evidence/images/deleted_account_reference_20260310.png) shows a stable internal reference and retained relationships on Mar10, before the Sep15 cutoff. It has no exposed direct identifiers in the visible screen. No canonical tombstone verification is present. It is a prior compliant-reference candidate; neither assume a violation nor ignore it solely because the canonical answer omits it.
- The May29 financial retention register names user_08/12/17/21/24/29 with retained-order dates through 2033. Those records are not in their expected sequences. Current existence, exact policy-category mapping and output resource identity require confirmation; an order display is not automatically an active legal hold.

## Recommended workflow from the evidence

Use one orchestrated case workflow with structured state and specialized evidence tools as the initial implementation. The samples establish a need for reliable extraction, identity/resource joins, temporal filtering, policy application, and deterministic answer assembly; they do not establish that autonomous multi-agent reasoning improves accuracy.

- Shared preprocessing: parse/index the participant sources once, preserving source/file/page/line and observation/capture times. OCR and PDF interpretation may be specialized workers, but their outputs remain observations, not verdicts.
- Per-case triage: authorize deletion or audit of prior deletion; allow an internal unresolved state rather than mapping uncertainty to NOT_APPLICABLE.
- Resolve identity, then run independent evidence searches concurrently. Iterate when a trace, resource ID or alias reveals another source.
- Merge into explicit subject/resource/evidence links; record match strength, conflicts and unknowns. Never assign anonymous records from array order or sample-answer IDs.
- Reconstruct states at the cutoff, evaluate policy conditions, and keep a coverage checklist for both remediation and required retention/absence checks.
- Build a remediation dependency graph where the evidence supplies dependencies. Validate it, then serialize according to the required operation/system/resource order; surface real conflicts rather than guessing.
- Validate schema, provenance, time admissibility, complete obligations, unique steps, ordering and citation semantics deterministically.

Model-assisted evidence interpretation can be bounded by tools and validated outputs. Introduce independent reasoning agents only if measured failure analysis shows a separable investigation bottleneck. A final summarizer should not freely compress the findings; final output must be assembled from validated structured facts and obligations.

## Edge cases to add before calling coverage sufficient

| Priority | Custom exercise | Required behavior |
|---|---|---|
| P0 | Access/export/correction/marketing-only requests, including multilingual negation | NOT_APPLICABLE with [] and no deletion planning |
| P0 | Prior-deletion audit versus hypothetical/conditional deletion question | Correct authorization boundary; preserve internal uncertainty when needed |
| P0 | Unmatched request email, shared/reassigned email, case normalization | Resolve with evidence or record an unresolved identity; never attach a near match |
| P0 | Anonymous resource with and without a legitimate prior resource mapping | Verify only when provenance links it to the subject without reidentifying anonymous data |
| P0 | Pre-cutoff observation in a post-cutoff export | Enforce the agreed availability rule consistently, including identity discovery |
| P0 | Missing evidence, truncated snapshot, query failure, conflicting same-time replicas | Do not confuse unknown with ABSENT or claim COMPLETE without coverage |
| P0 | Missing required retained record | Surface the contract limitation: current output vocabulary has no explicit restore-retained-record remediation |
| P1 | One case with active sync plus unsafe restore plus multiple downstream copies | Disable/block before dependent changes; preserve every required action |
| P1 | Explicit downstream-before-source dependency conflicting with lexical output order | Resolve contract precedence; do not silently reorder or fabricate a graph |
| P1 | Shared support attachment versus sole-subject attachment; expired legal hold | Apply conditions, preserve other people's data, do not use category shortcuts |
| P1 | Cache, product telemetry, email-delivery log, explicit marketing record | Exercise currently weak/missing policy categories |
| P1 | Same identifier in a contemporaneous decoy; identifier appearing only in a screenshot | Exact matching plus visual grounding, not filename or manifest inference |
| P1 | Reactivation after deletion and repeated requests at different audit cutoffs | Separate temporal state and case-local conclusions |
| P1 | Stable tombstone containing a residual hash or indirect identifying field | Inspect fields; DELETED label and null email alone are insufficient |
| P2 | Duplicate observations, cycles, retries, multiple identical system/resource rows | Deduplicate outputs, retain provenance and detect inconsistent ordering |

At least three custom cases are required by the challenge. Three would satisfy that minimum, but would not cover the gaps above. A compact suite can parameterize several related variants while reporting each expected outcome and rationale.

## Validation and limits

Checked all 32 public answer rows, all 193 step objects, exact seven-field schema, consecutive numbering, canonical order, all non-empty citation IDs and their manifest capture cutoffs. Every check passed. All 32 requests have a single exact current/history identity match; the report contains one case section and one CSV row for each. All expected resource occurrences were cross-checked against participant sources, with bounded negative-search results explicitly labeled.

No solver was executed, no hidden-label comparison performed, no prediction accuracy measured, no complete policy-coverage proof established, and no claim made that every apparent canonical inconsistency is a dataset defect. The next concrete work is to resolve the admissibility/provenance questions, define the state/tool contracts, and build the missing custom exercises before optimizing agent topology.
