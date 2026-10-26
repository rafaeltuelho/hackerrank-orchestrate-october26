# Evaluation report

## Custom cases A01–A03 (offline)

Measured deterministic assessment assembly using authored source inventories and frozen task doubles. These results do not measure model intent, retrieval, visual interpretation, or live end-to-end accuracy.

| Case | Complete source inventory and policy | Expected | Actual | Exact sequence |
|---|---|---|---|---|
| custom_a01 | Empty: discovery must never execute. | NOT_APPLICABLE | NOT_APPLICABLE | True |
| custom_a02 | Complete: exact subject-linked search readback and enabled connector; SEARCH_INDEX_ENTRY DELETE and active-flow control. | INCOMPLETE | INCOMPLETE | True |
| custom_a03 | Complete: scoped empty account lookup, stable tombstone with all prohibited fields null, and security record retained through 2030; DELETE/REDACT/RETAIN. | COMPLETE | COMPLETE | True |

### Measured custom metrics

- cases: 3
- status_correct: 3
- status_accuracy: 1.0
- sequence_correct: 3
- sequence_accuracy: 1.0
- step_matches: 9
- predicted_steps: 9
- expected_steps: 9
- step_precision: 1.0
- step_recall: 1.0
- fields_correct: 63
- fields_total: 63
- field_accuracy: 1.0

### custom_a01 expected and actual

Request: Please send me a copy of my records. Do not delete my account.

Cutoff: 2026-06-10T12:00:00+00:00. All declared observations and subject links predate this cutoff.

Expected `[]`; actual `[]`. No discovery or planning is authorized.

### custom_a02 expected and actual

Request: Permanently delete my account and remaining copies.

Cutoff: 2026-06-10T12:00:00+00:00. All declared observations and subject links predate this cutoff.

The actual seven-field ordered array exactly matches this expected table.

| step_no | phase | system_id | resource_id | operation | state | evidence_id |
|---|---|---|---|---|---|---|
| 1 | FINDING | search_service | search_custom02 | REPORT_REMAINING_RECORD | PRESENT | custom_e02 |
| 2 | FINDING | integration_service | flow_custom02 | REPORT_ACTIVE_DATA_FLOW | ACTIVE | custom_e02 |
| 3 | REMEDIATION | integration_service | flow_custom02 | DISABLE_DATA_FLOW | DISABLED | `""` |
| 4 | REMEDIATION | search_service | search_custom02 | DELETE_RECORD | ABSENT | `""` |
| 5 | VERIFICATION | search_service | search_custom02 | VERIFY_RECORD_ABSENT | ABSENT | `""` |
| 6 | VERIFICATION | integration_service | flow_custom02 | VERIFY_DATA_FLOW_DISABLED | DISABLED | `""` |

### custom_a03 expected and actual

Request: Delete my personal details, keeping only references required for retained records.

Cutoff: 2026-06-10T12:00:00+00:00. All declared observations and subject links predate this cutoff.

The actual seven-field ordered array exactly matches this expected table.

| step_no | phase | system_id | resource_id | operation | state | evidence_id |
|---|---|---|---|---|---|---|
| 1 | VERIFICATION | account_service | account_custom03 | VERIFY_RECORD_ABSENT | ABSENT | custom_e03 |
| 2 | VERIFICATION | security_service | audit_custom03 | VERIFY_RECORD_PRESENT | PRESENT | custom_e03 |
| 3 | VERIFICATION | identity_service | tombstone_custom03 | VERIFY_RECORD_REDACTED | REDACTED | custom_e03 |

Step matching: exact seven-field multiset intersection, including step_no. Precision divides by predicted steps; recall divides by expected steps. Field matching aligns by array position, counts seven fields per position, and penalizes missing/extra positions. Sequence matching requires equal status and ordered parsed arrays; object key order and whitespace are ignored.

## Public samples (development/regression set)

Not run: no frozen live solver predictions supplied. Hidden truth is unavailable.

## Failures and improvements

The foundation rejects unsupported intent spans, unknown citations, invalid operation/state/phase combinations, unsafe ordering, incomplete coverage, unscoped absence, unresolved ownership, and missing required retained records. A01–A03 test expected assembly; focused pytest failures/rejections are separate from live solver failures. Public-sample evidence gaps remain unresolved pending the live investigation; expected-answer resource IDs are never prediction inputs.

Observed compatibility failures fixed: the SDK rejected arbitrary-key observation dictionaries in strict output schemas, so the SDK boundary now uses duplicate-checked field/value pairs. The SQLite authorizer initially rejected implicit primary-key indexes, REINDEX and the supplied foreign_keys pragma; narrow allowances now load all 24 snapshots while external attachment/extension tests remain blocked. PDFium page objects lacked context-manager support; explicit closing fixed serial rendering.

## Delivery status

No final 518-case run has completed. This report is an intermediate measurement.

## Live pilot measurements

Predictions were generated without expected outputs. Expected answers are opened only by this evaluator after the run. Public samples are a development/regression set, not a holdout. Unsupported or failed cases have no fabricated submission row.

### Live authored A01–A03

Frozen run: `runs/custom-live-v2`.

- cases: 3
- status_correct: 3
- status_accuracy: 1.0
- sequence_correct: 3
- sequence_accuracy: 1.0
- step_matches: 9
- predicted_steps: 9
- expected_steps: 9
- step_precision: 1.0
- step_recall: 1.0
- fields_correct: 63
- fields_total: 63
- field_accuracy: 1.0

| Case | Expected | Actual | Exact ordered array |
|---|---|---|---|
| custom_a01 | NOT_APPLICABLE | NOT_APPLICABLE | True |
| custom_a02 | INCOMPLETE | INCOMPLETE | True |
| custom_a03 | COMPLETE | COMPLETE | True |

These live cases use independent fictional source logs and the supplied policy subset, through real SDK triage/audit runs and deterministic validation. They exercise non-deletion stopping, active-flow control before deletion, stable tombstone redaction, and retention. The exact expected arrays and fixture rationale appear in the custom-case tables above.

### Public-sample pilot

Frozen run: `runs/samples-v5`.

Missing/unresolved cases count as incorrect in the status/sequence denominators and contribute their missing expected steps/fields as errors. These are whole-pilot scores; scoring only the accepted subset would overstate success.

- cases: 32
- status_correct: 1
- status_accuracy: 0.03125
- sequence_correct: 1
- sequence_accuracy: 0.03125
- step_matches: 3
- predicted_steps: 3
- expected_steps: 193
- step_precision: 1.0
- step_recall: 0.015544041450777202
- fields_correct: 21
- fields_total: 1351
- field_accuracy: 0.015544041450777202

| Case | Expected | Actual | Exact sequence | Diagnostic |
|---|---|---|---|---|
| case_01 | COMPLETE | UNRESOLVED | False | INCOMPLETE_EVIDENCE_COVERAGE |
| case_02 | COMPLETE | UNRESOLVED | False | INCOMPLETE_EVIDENCE_COVERAGE |
| case_03 | COMPLETE | UNRESOLVED | False | UNSUPPORTED_CATEGORY |
| case_04 | COMPLETE | UNRESOLVED | False | INCOMPLETE_EVIDENCE_COVERAGE |
| case_05 | INCOMPLETE | INCOMPLETE | True |  |
| case_06 | INCOMPLETE | UNRESOLVED | False | INCOMPLETE_EVIDENCE_COVERAGE |
| case_07 | INCOMPLETE | UNRESOLVED | False | INCOMPLETE_EVIDENCE_COVERAGE |
| case_08 | INCOMPLETE | UNRESOLVED | False | UNKNOWN_OBSERVATION_TIME |
| case_09 | INCOMPLETE | UNRESOLVED | False | INCOMPLETE_EVIDENCE_COVERAGE |
| case_10 | INCOMPLETE | UNRESOLVED | False | UNSUPPORTED_SUBJECT_LINK |
| case_11 | INCOMPLETE | UNRESOLVED | False | UNSUPPORTED_ARTIFACT_FIELD |
| case_12 | INCOMPLETE | UNRESOLVED | False | INCOMPLETE_EVIDENCE_COVERAGE |
| case_13 | INCOMPLETE | UNRESOLVED | False | UNSUPPORTED_ARTIFACT_FIELD |
| case_14 | INCOMPLETE | UNRESOLVED | False | CLAIM_NOT_STATE_PROOF |
| case_15 | INCOMPLETE | UNRESOLVED | False | UNRESOLVED_INTENT |
| case_16 | INCOMPLETE | UNRESOLVED | False | INCOMPLETE_EVIDENCE_COVERAGE |
| case_17 | INCOMPLETE | UNRESOLVED | False | UNSUPPORTED_SUBJECT_LINK |
| case_18 | INCOMPLETE | UNRESOLVED | False | INCOMPLETE_EVIDENCE_COVERAGE |
| case_19 | INCOMPLETE | UNRESOLVED | False | UNSUPPORTED_SUBJECT_LINK |
| case_20 | INCOMPLETE | UNRESOLVED | False | INCOMPLETE_EVIDENCE_COVERAGE |
| case_21 | COMPLETE | UNRESOLVED | False | UNKNOWN_OBSERVATION_TIME |
| case_22 | INCOMPLETE | UNRESOLVED | False | INCOMPLETE_EVIDENCE_COVERAGE |
| case_23 | INCOMPLETE | UNRESOLVED | False | INCOMPLETE_EVIDENCE_COVERAGE |
| case_24 | INCOMPLETE | UNRESOLVED | False | UNKNOWN_OBSERVATION_TIME |
| case_25 | COMPLETE | UNRESOLVED | False | INCOMPLETE_EVIDENCE_COVERAGE |
| case_26 | COMPLETE | UNRESOLVED | False | UNSUPPORTED_RISK_CONDITION |
| case_27 | COMPLETE | UNRESOLVED | False | INCOMPLETE_EVIDENCE_COVERAGE |
| case_28 | COMPLETE | UNRESOLVED | False | INCOMPLETE_EVIDENCE_COVERAGE |
| case_29 | INCOMPLETE | UNRESOLVED | False | UNKNOWN_OBSERVATION_TIME |
| case_30 | INCOMPLETE | UNRESOLVED | False | INCOMPLETE_EVIDENCE_COVERAGE |
| case_31 | COMPLETE | UNRESOLVED | False | INCOMPLETE_EVIDENCE_COVERAGE |
| case_32 | INCOMPLETE | UNRESOLVED | False | INCOMPLETE_EVIDENCE_COVERAGE |

### Observed failures and improvements

Development runs found unsupported resource/alias links, mistaken logical service versus physical-replica names, unrecognized table-location category evidence, shell-quote parse errors in ordinary log lines, and exhausted tool budgets. Fixes add exact source receipts, table-scope metadata, narrow identifier-only tools, bounded evidence-backed repair, and explicit challenge flow/restore rules. Deliberately abbreviated file-integrity checksums remain literal and cannot become identity hashes. Genuine capture-cutoff, anonymous ownership and missing retention-condition gaps remain unresolved; no expected resource mapping or post-cutoff source was inserted into prediction logic.

## Current implementation and evaluation-input pilot

Subsequent fixes are newer than the complete 32-public-sample baseline above.
That 1/32 baseline is not presented as a measurement of the current revised code.
The current offline suite passed 98 tests. Live authored A01-A03 previously matched
3/3 statuses, 9/9 steps, 63/63 fields and 3/3 sequences; frozen authored proposals
were also revalidated after later changes without new model calls.

User-approved ASCII email case equivalence on 2026-10-25 resolves all 518 evaluation
identities from pre-cutoff current/history data. Originals are preserved and
cross-subject collisions fail. This is not a deletion-status accuracy result.

The bounded run `runs/evaluation-pilot-v12` used three actual evaluation requests.
No hidden truth is available for them, so acceptance below measures validation,
not accuracy. Expected sample outputs were not prediction inputs.

| Case | Pipeline result | Diagnostic |
|---|---|---|
| case_33 | INCOMPLETE |  |
| case_34 | UNRESOLVED | UNSUPPORTED_CATEGORY |
| case_35 | INCOMPLETE |  |

Accepted rows: 2/3. The requested output CSV was not published because one case
failed. At that earlier pilot checkpoint, root output.csv and submission code.zip had not been produced. See the later candidate measurement for current artifacts.

Further observed fixes include sentence-ending punctuation in exact ID matching,
explicit catalog document-ID bridges, record-level visual extraction, deterministic
literal timestamp normalization (including a caught year-0109 extraction error),
source-derived copy scopes, date-precision intervals, and scoped triage caching.
Cached triage keys include request/cutoff, model, reasoning, prompt and schema.

Case_34 still needs policy applicability grounded before its plan can be claimed
complete: the supplied pre-cutoff readbacks do not establish a retention period for
audit_record_3753 or exclusive attachment ownership for support_9538. The discovered
order references also need scope/category assessment without inventing policy.
These are unresolved findings, not a declaration that the challenge dataset is
defective. An intended authoritative interpretation/source was requested from the
user; no fallback deletion action or unsupported retention date was invented.

The final 518-case run is pending. Development costs, reported usage and unknown
reservations are recorded separately in usage_report.md; they are not fabricated
final-run measurements. Packaging requires both reports to identify the exact
successful final output hash, and includes identical archive-root report copies.

The latest offline increment distinguishes SQL snapshot observation time from row
update time. Exact SQL absence receipts require a previously observed resource,
matching table/schema and manifest origin, an explicit logical origin_system, an
explicit snapshot time, and a complete table with no excluded future rows. These
changes passed the offline suite; their effect on public-sample accuracy has not
been measured. The packaging README now uses the validated archive builder.

## Candidate public-sample replay measurement

Frozen run: `runs/public-candidate-v2`. Predictions used request-only triage, literal readbacks and revalidation of earlier saved model proposals. Expected public answers were opened only after the candidate run finished, by this evaluator. This is a development replay, not a fresh 32-case model investigation or holdout. These metrics include uncertified fallback rows and therefore do not certify evidence completeness.

- cases: 32
- status_correct: 22
- status_accuracy: 0.6875
- sequence_correct: 1
- sequence_accuracy: 0.03125
- step_matches: 27
- predicted_steps: 50
- expected_steps: 193
- step_precision: 0.54
- step_recall: 0.13989637305699482
- fields_correct: 252
- fields_total: 1351
- field_accuracy: 0.18652849740932642

Failures remain substantial: unresolved ownership, missing source clock times, unestablished conditional policy, unclassified resources and incomplete inventory prevent evidence certification. The INCOMPLETE placeholder can match a status by chance while missing its expected steps; status accuracy alone overstates this candidate's usefulness. Step/field/sequence metrics expose that limitation. The earlier strict baseline above is retained as a separate measurement.

## Full candidate output measurement

Output kind: candidate
Run output SHA-256: 014900dd0b17b5d397a7c0e35204b093c61e7df86e1f815a01c8d775078a79df

Measured run: `runs/full-candidate-v2`.
Structurally valid sorted output rows: 518.
Cases passing complete semantic evidence checks: 11/518.
Uncertified INCOMPLETE rows with no steps: 391.
Status distribution: {'INCOMPLETE': 508, 'NOT_APPLICABLE': 10}.

This is a best-supported preliminary candidate, not a fully evidence-validated solution. No hidden expected outputs are available for these requests, so deletion-status, step-level, field-level and sequence accuracy on this file are unavailable. Row coverage and semantic acceptance are not accuracy metrics. The public and authored measured evaluations above remain separately labeled.

INCOMPLETE with an empty step array is an uncertified placeholder imposed by the three-status serialization vocabulary. It does not assert that a remaining record or policy violation was proved. Partial plans contain independently validated treatments; unresolved records are omitted from treatment rather than deleted by default. Unknown retention windows and exclusive ownership remain unknown.

This run used request-only model triage in sequential bounded batches plus cached individual authorizations. The evidence pass used literal readbacks and revalidated saved model proposals where available. It did not perform a fresh model evidence audit for every case. Literal inventory cannot certify that unclassified visual, document, dependency and conditional-policy evidence is exhausted.

The earlier serial model pass was interrupted after four completed cases to implement the full preliminary pass. Its interrupted-call reservation remains charged conservatively. No unknown usage was converted to zero.

General participant-facing clarification remains needed for missing retention periods, exclusive attachment ownership, and the intended answer when a rule condition is unestablished. The clarification draft has not been sent externally.

| Case | Candidate status | Steps | Evidence validated | Limitations |
|---|---|---:|---|---|
| case_100 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_101 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_102 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_103 | INCOMPLETE | 0 | no | PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit; UNRESOLVED_POLICY_CONDITION; security_service/audit_record_9522/rule_12: UNRESOLVED_POLICY_CONDITION |
| case_104 | INCOMPLETE | 6 | no | PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit; UNRESOLVED_POLICY_CONDITION; security_service/audit_record_6230/rule_12: UNRESOLVED_POLICY_CONDITION; support_platform/support... |
| case_105 | INCOMPLETE | 6 | no | PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit; UNRESOLVED_POLICY_CONDITION; security_service/audit_record_4520/rule_12: UNRESOLVED_POLICY_CONDITION |
| case_106 | INCOMPLETE | 3 | no | PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit; UNRESOLVED_POLICY_CONDITION; security_service/audit_record_8723/rule_12: UNRESOLVED_POLICY_CONDITION |
| case_107 | INCOMPLETE | 0 | no | PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit; UNRESOLVED_POLICY_CONDITION; security_service/audit_record_7572/rule_12: UNRESOLVED_POLICY_CONDITION |
| case_108 | INCOMPLETE | 0 | no | PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit; UNRESOLVED_POLICY_CONDITION; security_service/audit_record_1469/rule_12: UNRESOLVED_POLICY_CONDITION |
| case_109 | INCOMPLETE | 3 | no | PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit; UNRESOLVED_POLICY_CONDITION; security_service/audit_record_2718/rule_12: UNRESOLVED_POLICY_CONDITION |
| case_110 | INCOMPLETE | 3 | no | PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit; UNRESOLVED_POLICY_CONDITION; security_service/audit_record_9268/rule_12: UNRESOLVED_POLICY_CONDITION |
| case_111 | INCOMPLETE | 0 | no | PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit; UNRESOLVED_POLICY_CONDITION; security_service/audit_record_8933/rule_12: UNRESOLVED_POLICY_CONDITION |
| case_112 | INCOMPLETE | 0 | no | PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit; UNRESOLVED_POLICY_CONDITION; backup_service/backup_4863/restore_risk: UNSUPPORTED_RISK_CONDITION; security_service/audit_recor... |
| case_113 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_114 | INCOMPLETE | 3 | no | PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit; UNRESOLVED_POLICY_CONDITION; support_platform/support_3786/rule_05: UNRESOLVED_POLICY_CONDITION |
| case_115 | INCOMPLETE | 6 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_116 | INCOMPLETE | 6 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_117 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_118 | INCOMPLETE | 3 | no | PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit; UNRESOLVED_POLICY_CONDITION; support_platform/support_036/rule_05: UNRESOLVED_POLICY_CONDITION |
| case_119 | INCOMPLETE | 3 | no | PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit; UNRESOLVED_POLICY_CONDITION; support_platform/support_9309/rule_05: UNRESOLVED_POLICY_CONDITION |
| case_120 | INCOMPLETE | 3 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_121 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_122 | INCOMPLETE | 6 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_123 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_124 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_125 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_126 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_127 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_128 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_129 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_130 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_131 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_132 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_133 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_134 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_135 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_136 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_137 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_138 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_139 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_140 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_141 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_142 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_143 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_144 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_145 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_146 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_147 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_148 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_149 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_150 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_151 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_152 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_153 | INCOMPLETE | 6 | no | PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit; UNRESOLVED_POLICY_CONDITION; security_service/audit_record_5652/rule_12: UNRESOLVED_POLICY_CONDITION |
| case_154 | INCOMPLETE | 3 | no | PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit; UNRESOLVED_POLICY_CONDITION; security_service/audit_record_2580/rule_12: UNRESOLVED_POLICY_CONDITION |
| case_155 | INCOMPLETE | 0 | no | PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit; UNRESOLVED_POLICY_CONDITION; backup_service/backup_161/restore_risk: UNSUPPORTED_RISK_CONDITION; security_service/audit_record... |
| case_156 | INCOMPLETE | 3 | no | PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit; UNRESOLVED_POLICY_CONDITION; security_service/audit_record_5890/rule_12: UNRESOLVED_POLICY_CONDITION |
| case_157 | INCOMPLETE | 0 | no | PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit; UNRESOLVED_POLICY_CONDITION; security_service/audit_record_8821/rule_12: UNRESOLVED_POLICY_CONDITION |
| case_158 | INCOMPLETE | 3 | no | PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit; UNRESOLVED_POLICY_CONDITION; security_service/audit_record_9665/rule_12: UNRESOLVED_POLICY_CONDITION |
| case_159 | INCOMPLETE | 0 | no | PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit; UNRESOLVED_POLICY_CONDITION; security_service/audit_record_8742/rule_12: UNRESOLVED_POLICY_CONDITION |
| case_160 | INCOMPLETE | 0 | no | PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit; UNRESOLVED_POLICY_CONDITION; security_service/audit_record_9882/rule_12: UNRESOLVED_POLICY_CONDITION; support_platform/support... |
| case_161 | INCOMPLETE | 3 | no | PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit; UNRESOLVED_POLICY_CONDITION; security_service/audit_record_8002/rule_12: UNRESOLVED_POLICY_CONDITION |
| case_162 | INCOMPLETE | 0 | no | PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit; UNRESOLVED_POLICY_CONDITION; security_service/audit_record_6362/rule_12: UNRESOLVED_POLICY_CONDITION |
| case_163 | INCOMPLETE | 6 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_164 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_165 | INCOMPLETE | 6 | no | PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit; UNRESOLVED_POLICY_CONDITION; support_platform/support_3586/rule_05: UNRESOLVED_POLICY_CONDITION |
| case_166 | INCOMPLETE | 3 | no | PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit; UNRESOLVED_POLICY_CONDITION; support_platform/support_3155/rule_05: UNRESOLVED_POLICY_CONDITION |
| case_167 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_168 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_169 | INCOMPLETE | 6 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_170 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_171 | INCOMPLETE | 3 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_172 | INCOMPLETE | 3 | no | PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit; UNRESOLVED_POLICY_CONDITION; support_platform/support_2322/rule_05: UNRESOLVED_POLICY_CONDITION |
| case_173 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_174 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_175 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_176 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_177 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_178 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_179 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_180 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_181 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_182 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_183 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_184 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_185 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_186 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_187 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_188 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_189 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_190 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_191 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_192 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_193 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_194 | INCOMPLETE | 6 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_195 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_196 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_197 | INCOMPLETE | 3 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_198 | INCOMPLETE | 3 | no | PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit; UNRESOLVED_POLICY_CONDITION; support_platform/support_6131/rule_05: UNRESOLVED_POLICY_CONDITION |
| case_199 | INCOMPLETE | 6 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_200 | INCOMPLETE | 6 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_201 | INCOMPLETE | 9 | no | PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit; UNRESOLVED_POLICY_CONDITION; support_platform/support_2863/rule_05: UNRESOLVED_POLICY_CONDITION |
| case_202 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_203 | INCOMPLETE | 3 | no | PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit; UNRESOLVED_POLICY_CONDITION; security_service/audit_record_1159/rule_12: UNRESOLVED_POLICY_CONDITION |
| case_204 | INCOMPLETE | 0 | no | PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit; UNRESOLVED_POLICY_CONDITION; backup_service/backup_9519/restore_risk: UNSUPPORTED_RISK_CONDITION; security_service/audit_recor... |
| case_205 | INCOMPLETE | 3 | no | PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit; UNRESOLVED_POLICY_CONDITION; security_service/audit_record_5023/rule_12: UNRESOLVED_POLICY_CONDITION |
| case_206 | INCOMPLETE | 0 | no | PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit; UNRESOLVED_POLICY_CONDITION; security_service/audit_record_9878/rule_12: UNRESOLVED_POLICY_CONDITION |
| case_207 | INCOMPLETE | 0 | no | PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit; UNRESOLVED_POLICY_CONDITION; security_service/audit_record_3578/rule_12: UNRESOLVED_POLICY_CONDITION |
| case_208 | INCOMPLETE | 3 | no | PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit; UNRESOLVED_POLICY_CONDITION; security_service/audit_record_2697/rule_12: UNRESOLVED_POLICY_CONDITION; support_platform/support... |
| case_209 | INCOMPLETE | 6 | no | PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit; UNRESOLVED_POLICY_CONDITION; security_service/audit_record_8189/rule_12: UNRESOLVED_POLICY_CONDITION; support_platform/support... |
| case_210 | INCOMPLETE | 3 | no | PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit; UNRESOLVED_POLICY_CONDITION; security_service/audit_record_6796/rule_12: UNRESOLVED_POLICY_CONDITION; support_platform/support... |
| case_211 | INCOMPLETE | 6 | no | PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit; UNRESOLVED_POLICY_CONDITION; security_service/audit_record_7804/rule_12: UNRESOLVED_POLICY_CONDITION |
| case_212 | INCOMPLETE | 3 | no | PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit; UNRESOLVED_POLICY_CONDITION; security_service/audit_record_3261/rule_12: UNRESOLVED_POLICY_CONDITION |
| case_213 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_214 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_215 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_216 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_217 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_218 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_219 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_220 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_221 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_222 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_223 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_224 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_225 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_226 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_227 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_228 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_229 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_230 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_231 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_232 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_233 | INCOMPLETE | 0 | no | PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit; UNRESOLVED_POLICY_CONDITION; support_platform/support_9670/rule_05: UNRESOLVED_POLICY_CONDITION |
| case_234 | INCOMPLETE | 3 | no | PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit; UNRESOLVED_POLICY_CONDITION; support_platform/support_1254/rule_05: UNRESOLVED_POLICY_CONDITION |
| case_235 | INCOMPLETE | 0 | no | PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit; UNRESOLVED_POLICY_CONDITION; support_platform/support_9391/rule_05: UNRESOLVED_POLICY_CONDITION |
| case_236 | INCOMPLETE | 6 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_237 | INCOMPLETE | 6 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_238 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_239 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_240 | INCOMPLETE | 3 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_241 | INCOMPLETE | 6 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_242 | INCOMPLETE | 6 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_243 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_244 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_245 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_246 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_247 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_248 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_249 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_250 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_251 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_252 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_253 | INCOMPLETE | 0 | no | PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit; UNRESOLVED_POLICY_CONDITION; security_service/audit_record_2927/rule_12: UNRESOLVED_POLICY_CONDITION |
| case_254 | INCOMPLETE | 3 | no | PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit; UNRESOLVED_POLICY_CONDITION; security_service/audit_record_9256/rule_12: UNRESOLVED_POLICY_CONDITION |
| case_255 | INCOMPLETE | 0 | no | PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit; UNRESOLVED_POLICY_CONDITION; security_service/audit_record_2513/rule_12: UNRESOLVED_POLICY_CONDITION |
| case_256 | INCOMPLETE | 3 | no | PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit; UNRESOLVED_POLICY_CONDITION; security_service/audit_record_2453/rule_12: UNRESOLVED_POLICY_CONDITION; support_platform/support... |
| case_257 | INCOMPLETE | 0 | no | PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit; UNRESOLVED_POLICY_CONDITION; security_service/audit_record_7193/rule_12: UNRESOLVED_POLICY_CONDITION |
| case_258 | INCOMPLETE | 3 | no | PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit; UNRESOLVED_POLICY_CONDITION; security_service/audit_record_9890/rule_12: UNRESOLVED_POLICY_CONDITION; support_platform/support... |
| case_259 | INCOMPLETE | 6 | no | PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit; UNRESOLVED_POLICY_CONDITION; security_service/audit_record_1421/rule_12: UNRESOLVED_POLICY_CONDITION |
| case_260 | INCOMPLETE | 0 | no | PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit; UNRESOLVED_POLICY_CONDITION; security_service/audit_record_1876/rule_12: UNRESOLVED_POLICY_CONDITION |
| case_261 | INCOMPLETE | 6 | no | PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit; UNRESOLVED_POLICY_CONDITION; legal_service/legal_hold_8017/rule_13: UNRESOLVED_POLICY_CONDITION; security_service/audit_record... |
| case_262 | INCOMPLETE | 3 | no | PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit; UNRESOLVED_POLICY_CONDITION; security_service/audit_record_4812/rule_12: UNRESOLVED_POLICY_CONDITION |
| case_263 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_264 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_265 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_266 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_267 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_268 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_269 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_270 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_271 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_272 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_273 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_274 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_275 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_276 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_277 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_278 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_279 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_280 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_281 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_282 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_283 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_284 | INCOMPLETE | 3 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_285 | INCOMPLETE | 6 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_286 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_287 | INCOMPLETE | 3 | no | PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit; UNRESOLVED_POLICY_CONDITION; support_platform/support_7432/rule_05: UNRESOLVED_POLICY_CONDITION |
| case_288 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_289 | INCOMPLETE | 6 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_290 | INCOMPLETE | 6 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_291 | INCOMPLETE | 3 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_292 | INCOMPLETE | 0 | no | PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit; UNRESOLVED_POLICY_CONDITION; support_platform/support_1526/rule_05: UNRESOLVED_POLICY_CONDITION |
| case_293 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_294 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_295 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_296 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_297 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_298 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_299 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_300 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_301 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_302 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_303 | INCOMPLETE | 0 | no | PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit; UNRESOLVED_POLICY_CONDITION; security_service/audit_record_7923/rule_12: UNRESOLVED_POLICY_CONDITION |
| case_304 | INCOMPLETE | 0 | no | PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit; UNRESOLVED_POLICY_CONDITION; security_service/audit_record_4759/rule_12: UNRESOLVED_POLICY_CONDITION |
| case_305 | INCOMPLETE | 6 | no | PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit; UNRESOLVED_POLICY_CONDITION; security_service/audit_record_507/rule_12: UNRESOLVED_POLICY_CONDITION |
| case_306 | INCOMPLETE | 3 | no | PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit; UNRESOLVED_POLICY_CONDITION; security_service/audit_record_9051/rule_12: UNRESOLVED_POLICY_CONDITION; support_platform/support... |
| case_307 | INCOMPLETE | 6 | no | PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit; UNRESOLVED_POLICY_CONDITION; security_service/audit_record_5129/rule_12: UNRESOLVED_POLICY_CONDITION |
| case_308 | INCOMPLETE | 0 | no | PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit; UNRESOLVED_POLICY_CONDITION; backup_service/backup_4917/restore_risk: UNSUPPORTED_RISK_CONDITION; security_service/audit_recor... |
| case_309 | INCOMPLETE | 0 | no | PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit; UNRESOLVED_POLICY_CONDITION; security_service/audit_record_1945/rule_12: UNRESOLVED_POLICY_CONDITION |
| case_310 | INCOMPLETE | 3 | no | PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit; UNRESOLVED_POLICY_CONDITION; security_service/audit_record_5640/rule_12: UNRESOLVED_POLICY_CONDITION; support_platform/support... |
| case_311 | INCOMPLETE | 3 | no | PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit; UNRESOLVED_POLICY_CONDITION; security_service/audit_record_6245/rule_12: UNRESOLVED_POLICY_CONDITION |
| case_312 | INCOMPLETE | 3 | no | PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit; UNRESOLVED_POLICY_CONDITION; security_service/audit_record_6559/rule_12: UNRESOLVED_POLICY_CONDITION |
| case_313 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_314 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_315 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_316 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_317 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_318 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_319 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_320 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_321 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_322 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_323 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_324 | INCOMPLETE | 0 | no | PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit; UNRESOLVED_POLICY_CONDITION; support_platform/support_7249/rule_05: UNRESOLVED_POLICY_CONDITION |
| case_325 | INCOMPLETE | 6 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_326 | INCOMPLETE | 0 | no | PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit; UNRESOLVED_POLICY_CONDITION; support_platform/support_305/rule_05: UNRESOLVED_POLICY_CONDITION |
| case_327 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_328 | INCOMPLETE | 3 | no | PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit; UNRESOLVED_POLICY_CONDITION; support_platform/support_7926/rule_05: UNRESOLVED_POLICY_CONDITION |
| case_329 | INCOMPLETE | 3 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_33 | INCOMPLETE | 3 | no | CONFLICTING_READBACKS; export_service/export_1260/rule_09: CONFLICTING_READBACKS |
| case_330 | INCOMPLETE | 3 | no | PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit; UNRESOLVED_POLICY_CONDITION; support_platform/support_4851/rule_05: UNRESOLVED_POLICY_CONDITION |
| case_331 | INCOMPLETE | 0 | no | PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit; UNRESOLVED_POLICY_CONDITION; support_platform/support_1403/rule_05: UNRESOLVED_POLICY_CONDITION |
| case_332 | INCOMPLETE | 6 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_333 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_334 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_335 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_336 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_337 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_338 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_339 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_34 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit; OBSERVATION_FIELD_MISMATCH; ORD-20265762 and ORD-20265518 are explicitly subject-linked screen r... |
| case_340 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_341 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_342 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_343 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_344 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_345 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_346 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_347 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_348 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_349 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_35 | INCOMPLETE | 3 | yes |  |
| case_350 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_351 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_352 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_353 | INCOMPLETE | 6 | no | PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit; UNRESOLVED_POLICY_CONDITION; security_service/audit_record_5773/rule_12: UNRESOLVED_POLICY_CONDITION; support_platform/support... |
| case_354 | INCOMPLETE | 0 | no | PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit; UNRESOLVED_POLICY_CONDITION; security_service/audit_record_9286/rule_12: UNRESOLVED_POLICY_CONDITION |
| case_355 | INCOMPLETE | 3 | no | PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit; UNRESOLVED_POLICY_CONDITION; security_service/audit_record_1151/rule_12: UNRESOLVED_POLICY_CONDITION |
| case_356 | INCOMPLETE | 6 | no | PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit; UNRESOLVED_POLICY_CONDITION; security_service/audit_record_771/rule_12: UNRESOLVED_POLICY_CONDITION; support_platform/support_... |
| case_357 | INCOMPLETE | 6 | no | PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit; UNRESOLVED_POLICY_CONDITION; security_service/audit_record_350/rule_12: UNRESOLVED_POLICY_CONDITION |
| case_358 | INCOMPLETE | 3 | no | PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit; UNRESOLVED_POLICY_CONDITION; security_service/audit_record_1395/rule_12: UNRESOLVED_POLICY_CONDITION; support_platform/support... |
| case_359 | INCOMPLETE | 3 | no | PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit; UNRESOLVED_POLICY_CONDITION; security_service/audit_record_2641/rule_12: UNRESOLVED_POLICY_CONDITION |
| case_36 | INCOMPLETE | 7 | no | PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit; UNRESOLVED_POLICY_CONDITION; security_service/audit_record_2966/rule_12: UNRESOLVED_POLICY_CONDITION; The exhausted supplied-c... |
| case_360 | INCOMPLETE | 3 | no | PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit; UNRESOLVED_POLICY_CONDITION; security_service/audit_record_2605/rule_12: UNRESOLVED_POLICY_CONDITION |
| case_361 | INCOMPLETE | 3 | no | PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit; UNRESOLVED_POLICY_CONDITION; security_service/audit_record_7587/rule_12: UNRESOLVED_POLICY_CONDITION |
| case_362 | INCOMPLETE | 0 | no | PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit; UNRESOLVED_POLICY_CONDITION; security_service/audit_record_8638/rule_12: UNRESOLVED_POLICY_CONDITION |
| case_363 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_364 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_365 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_366 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_367 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_368 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_369 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_37 | INCOMPLETE | 4 | no | PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit; UNASSESSED_GROUNDED_RESOURCE; security_service/audit_record_2019/rule_12: UNRESOLVED_POLICY_CONDITION |
| case_370 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_371 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_372 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_373 | INCOMPLETE | 6 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_374 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_375 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_376 | INCOMPLETE | 3 | no | PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit; UNRESOLVED_POLICY_CONDITION; support_platform/support_475/rule_05: UNRESOLVED_POLICY_CONDITION |
| case_377 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_378 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_379 | INCOMPLETE | 6 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_38 | INCOMPLETE | 0 | no | PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit; UNASSESSED_GROUNDED_RESOURCE; security_service/audit_record_633/rule_12: UNRESOLVED_POLICY_CONDITION |
| case_380 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_381 | INCOMPLETE | 3 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_382 | INCOMPLETE | 6 | no | PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit; UNRESOLVED_POLICY_CONDITION; support_platform/support_5071/rule_05: UNRESOLVED_POLICY_CONDITION |
| case_383 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_384 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_385 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_386 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_387 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_388 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_389 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_39 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_390 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_391 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_392 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_393 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_394 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_395 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_396 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_397 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_398 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_399 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_40 | INCOMPLETE | 4 | no | PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit; UNRESOLVED_POLICY_CONDITION; security_service/audit_record_8349/rule_12: UNRESOLVED_POLICY_CONDITION; support_platform/support... |
| case_400 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_401 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_402 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_403 | INCOMPLETE | 0 | no | PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit; UNRESOLVED_POLICY_CONDITION; security_service/audit_record_4733/rule_12: UNRESOLVED_POLICY_CONDITION |
| case_404 | INCOMPLETE | 6 | no | PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit; UNRESOLVED_POLICY_CONDITION; security_service/audit_record_6099/rule_12: UNRESOLVED_POLICY_CONDITION; support_platform/support... |
| case_405 | INCOMPLETE | 6 | no | PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit; UNRESOLVED_POLICY_CONDITION; security_service/audit_record_4522/rule_12: UNRESOLVED_POLICY_CONDITION |
| case_406 | INCOMPLETE | 3 | no | PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit; UNRESOLVED_POLICY_CONDITION; security_service/audit_record_5455/rule_12: UNRESOLVED_POLICY_CONDITION; support_platform/support... |
| case_407 | INCOMPLETE | 6 | no | PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit; UNRESOLVED_POLICY_CONDITION; security_service/audit_record_6152/rule_12: UNRESOLVED_POLICY_CONDITION; support_platform/support... |
| case_408 | INCOMPLETE | 0 | no | PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit; UNRESOLVED_POLICY_CONDITION; security_service/audit_record_4216/rule_12: UNRESOLVED_POLICY_CONDITION |
| case_409 | INCOMPLETE | 0 | no | PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit; UNRESOLVED_POLICY_CONDITION; security_service/audit_record_2559/rule_12: UNRESOLVED_POLICY_CONDITION |
| case_41 | INCOMPLETE | 0 | no | PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit; UNASSESSED_GROUNDED_RESOURCE; backup_service/backup_706/rule_14: UNRESOLVED_POLICY_CONDITION; security_service/audit_record_78... |
| case_410 | INCOMPLETE | 3 | no | PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit; UNRESOLVED_POLICY_CONDITION; security_service/audit_record_896/rule_12: UNRESOLVED_POLICY_CONDITION |
| case_411 | INCOMPLETE | 0 | no | PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit; UNRESOLVED_POLICY_CONDITION; security_service/audit_record_4330/rule_12: UNRESOLVED_POLICY_CONDITION |
| case_412 | INCOMPLETE | 0 | no | PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit; UNRESOLVED_POLICY_CONDITION; security_service/audit_record_5637/rule_12: UNRESOLVED_POLICY_CONDITION |
| case_413 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_414 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_415 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_416 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_417 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_418 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_419 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_42 | INCOMPLETE | 4 | no | PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit; UNRESOLVED_POLICY_CONDITION; security_service/audit_record_6760/rule_12: UNRESOLVED_POLICY_CONDITION; support_platform/support... |
| case_420 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_421 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_422 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_423 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_424 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_425 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_426 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_427 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_428 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_429 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_43 | INCOMPLETE | 3 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_430 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_431 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_432 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_433 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_434 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_435 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_436 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_437 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_438 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_439 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_44 | INCOMPLETE | 0 | no | PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit; UNRESOLVED_POLICY_CONDITION; support_platform/support_1066/rule_05: UNRESOLVED_POLICY_CONDITION |
| case_440 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_441 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_442 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_443 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_444 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_445 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_446 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_447 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_448 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_449 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_45 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_450 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_451 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_452 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_453 | INCOMPLETE | 6 | no | PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit; UNRESOLVED_POLICY_CONDITION; security_service/audit_record_3600/rule_12: UNRESOLVED_POLICY_CONDITION |
| case_454 | INCOMPLETE | 3 | no | PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit; UNRESOLVED_POLICY_CONDITION; security_service/audit_record_2775/rule_12: UNRESOLVED_POLICY_CONDITION |
| case_455 | INCOMPLETE | 3 | no | PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit; UNRESOLVED_POLICY_CONDITION; security_service/audit_record_2788/rule_12: UNRESOLVED_POLICY_CONDITION |
| case_456 | INCOMPLETE | 0 | no | PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit; UNRESOLVED_POLICY_CONDITION; security_service/audit_record_8176/rule_12: UNRESOLVED_POLICY_CONDITION |
| case_457 | INCOMPLETE | 0 | no | PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit; UNRESOLVED_POLICY_CONDITION; security_service/audit_record_1171/rule_12: UNRESOLVED_POLICY_CONDITION |
| case_458 | INCOMPLETE | 0 | no | PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit; UNRESOLVED_POLICY_CONDITION; security_service/audit_record_6750/rule_12: UNRESOLVED_POLICY_CONDITION |
| case_459 | INCOMPLETE | 0 | no | PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit; UNRESOLVED_POLICY_CONDITION; security_service/audit_record_6171/rule_12: UNRESOLVED_POLICY_CONDITION |
| case_46 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_460 | INCOMPLETE | 0 | no | PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit; UNRESOLVED_POLICY_CONDITION; legal_service/legal_hold_5622/rule_13: UNRESOLVED_POLICY_CONDITION; security_service/audit_record... |
| case_461 | INCOMPLETE | 6 | no | PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit; UNRESOLVED_POLICY_CONDITION; security_service/audit_record_3883/rule_12: UNRESOLVED_POLICY_CONDITION; support_platform/support... |
| case_462 | INCOMPLETE | 0 | no | PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit; UNRESOLVED_POLICY_CONDITION; security_service/audit_record_641/rule_12: UNRESOLVED_POLICY_CONDITION |
| case_463 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_464 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_465 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_466 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_467 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_468 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_469 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_47 | INCOMPLETE | 3 | no | PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit; UNRESOLVED_POLICY_CONDITION; support_platform/support_5742/rule_05: UNRESOLVED_POLICY_CONDITION |
| case_470 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_471 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_472 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_473 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_474 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_475 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_476 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_477 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_478 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_479 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_48 | INCOMPLETE | 6 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_480 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_481 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_482 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_483 | INCOMPLETE | 9 | no | PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit; UNRESOLVED_POLICY_CONDITION; support_platform/support_4364/rule_05: UNRESOLVED_POLICY_CONDITION |
| case_484 | INCOMPLETE | 0 | no | PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit; UNRESOLVED_POLICY_CONDITION; support_platform/support_7973/rule_05: UNRESOLVED_POLICY_CONDITION |
| case_485 | INCOMPLETE | 3 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_486 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_487 | INCOMPLETE | 6 | no | PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit; UNRESOLVED_POLICY_CONDITION; support_platform/support_5361/rule_05: UNRESOLVED_POLICY_CONDITION |
| case_488 | INCOMPLETE | 6 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_489 | INCOMPLETE | 6 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_49 | INCOMPLETE | 6 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_490 | INCOMPLETE | 3 | no | PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit; UNRESOLVED_POLICY_CONDITION; support_platform/support_4247/rule_05: UNRESOLVED_POLICY_CONDITION |
| case_491 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_492 | INCOMPLETE | 3 | no | PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit; UNRESOLVED_POLICY_CONDITION; support_platform/support_6737/rule_05: UNRESOLVED_POLICY_CONDITION |
| case_493 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_494 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_495 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_496 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_497 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_498 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_499 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_50 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_500 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_501 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_502 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_503 | INCOMPLETE | 0 | no | PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit; UNRESOLVED_POLICY_CONDITION; security_service/audit_record_5454/rule_12: UNRESOLVED_POLICY_CONDITION |
| case_504 | INCOMPLETE | 0 | no | PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit; UNRESOLVED_POLICY_CONDITION; security_service/audit_record_3733/rule_12: UNRESOLVED_POLICY_CONDITION |
| case_505 | INCOMPLETE | 3 | no | PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit; UNRESOLVED_POLICY_CONDITION; legal_service/legal_hold_2227/rule_13: UNRESOLVED_POLICY_CONDITION; security_service/audit_record... |
| case_506 | INCOMPLETE | 0 | no | PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit; UNRESOLVED_POLICY_CONDITION; security_service/audit_record_1361/rule_12: UNRESOLVED_POLICY_CONDITION |
| case_507 | INCOMPLETE | 0 | no | PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit; UNRESOLVED_POLICY_CONDITION; security_service/audit_record_7627/rule_12: UNRESOLVED_POLICY_CONDITION |
| case_508 | INCOMPLETE | 0 | no | PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit; UNRESOLVED_POLICY_CONDITION; security_service/audit_record_8154/rule_12: UNRESOLVED_POLICY_CONDITION; support_platform/support... |
| case_509 | INCOMPLETE | 6 | no | PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit; UNRESOLVED_POLICY_CONDITION; security_service/audit_record_2323/rule_12: UNRESOLVED_POLICY_CONDITION |
| case_51 | INCOMPLETE | 0 | no | PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit; UNRESOLVED_POLICY_CONDITION; support_platform/support_1097/rule_05: UNRESOLVED_POLICY_CONDITION |
| case_510 | INCOMPLETE | 3 | no | PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit; UNRESOLVED_POLICY_CONDITION; security_service/audit_record_4266/rule_12: UNRESOLVED_POLICY_CONDITION; support_platform/support... |
| case_511 | INCOMPLETE | 3 | no | PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit; UNRESOLVED_POLICY_CONDITION; legal_service/legal_hold_4887/rule_13: UNRESOLVED_POLICY_CONDITION; security_service/audit_record... |
| case_512 | INCOMPLETE | 0 | no | PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit; UNRESOLVED_POLICY_CONDITION; security_service/audit_record_4219/rule_12: UNRESOLVED_POLICY_CONDITION |
| case_513 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit; DISCOVERY_IDENTIFIER_LIMIT |
| case_514 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit; DISCOVERY_IDENTIFIER_LIMIT |
| case_515 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit; DISCOVERY_IDENTIFIER_LIMIT |
| case_516 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_517 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit; DISCOVERY_IDENTIFIER_LIMIT |
| case_518 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit; DISCOVERY_IDENTIFIER_LIMIT |
| case_519 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_52 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_520 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit; DISCOVERY_IDENTIFIER_LIMIT |
| case_521 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_522 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit; DISCOVERY_IDENTIFIER_LIMIT |
| case_523 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_524 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_525 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_526 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_527 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_528 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_529 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_53 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit; DISCOVERY_IDENTIFIER_LIMIT |
| case_530 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_531 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_532 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_533 | NOT_APPLICABLE | 0 | yes |  |
| case_534 | NOT_APPLICABLE | 0 | yes |  |
| case_535 | NOT_APPLICABLE | 0 | yes |  |
| case_536 | NOT_APPLICABLE | 0 | yes |  |
| case_537 | NOT_APPLICABLE | 0 | yes |  |
| case_538 | NOT_APPLICABLE | 0 | yes |  |
| case_539 | NOT_APPLICABLE | 0 | yes |  |
| case_54 | INCOMPLETE | 6 | no | PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit; UNRESOLVED_POLICY_CONDITION; security_service/audit_record_6325/rule_12: UNRESOLVED_POLICY_CONDITION; support_platform/support... |
| case_540 | NOT_APPLICABLE | 0 | yes |  |
| case_541 | NOT_APPLICABLE | 0 | yes |  |
| case_542 | NOT_APPLICABLE | 0 | yes |  |
| case_543 | INCOMPLETE | 0 | no | PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit; UNRESOLVED_POLICY_CONDITION; security_service/audit_record_6244/rule_12: UNRESOLVED_POLICY_CONDITION |
| case_544 | INCOMPLETE | 3 | no | PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit; UNRESOLVED_POLICY_CONDITION; security_service/audit_record_1037/rule_12: UNRESOLVED_POLICY_CONDITION |
| case_545 | INCOMPLETE | 0 | no | PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit; UNRESOLVED_POLICY_CONDITION; security_service/audit_record_5041/rule_12: UNRESOLVED_POLICY_CONDITION |
| case_546 | INCOMPLETE | 3 | no | PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit; UNRESOLVED_POLICY_CONDITION; security_service/audit_record_518/rule_12: UNRESOLVED_POLICY_CONDITION |
| case_547 | INCOMPLETE | 0 | no | PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit; UNRESOLVED_POLICY_CONDITION; security_service/audit_record_7352/rule_12: UNRESOLVED_POLICY_CONDITION |
| case_548 | INCOMPLETE | 3 | no | PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit; UNRESOLVED_POLICY_CONDITION; security_service/audit_record_6970/rule_12: UNRESOLVED_POLICY_CONDITION |
| case_549 | INCOMPLETE | 0 | no | PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit; UNRESOLVED_POLICY_CONDITION; security_service/audit_record_1491/rule_12: UNRESOLVED_POLICY_CONDITION |
| case_55 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_550 | INCOMPLETE | 3 | no | PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit; UNRESOLVED_POLICY_CONDITION; security_service/audit_record_3831/rule_12: UNRESOLVED_POLICY_CONDITION |
| case_56 | INCOMPLETE | 0 | no | PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit; UNRESOLVED_POLICY_CONDITION; security_service/audit_record_4078/rule_12: UNRESOLVED_POLICY_CONDITION |
| case_57 | INCOMPLETE | 0 | no | PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit; UNRESOLVED_POLICY_CONDITION; backup_service/backup_7711/restore_risk: UNSUPPORTED_RISK_CONDITION; security_service/audit_recor... |
| case_58 | INCOMPLETE | 0 | no | PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit; UNRESOLVED_POLICY_CONDITION; security_service/audit_record_8465/rule_12: UNRESOLVED_POLICY_CONDITION |
| case_59 | INCOMPLETE | 0 | no | PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit; UNRESOLVED_POLICY_CONDITION; security_service/audit_record_962/rule_12: UNRESOLVED_POLICY_CONDITION |
| case_60 | INCOMPLETE | 0 | no | PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit; UNRESOLVED_POLICY_CONDITION; security_service/audit_record_629/rule_12: UNRESOLVED_POLICY_CONDITION |
| case_61 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_62 | INCOMPLETE | 6 | no | PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit; UNRESOLVED_POLICY_CONDITION; security_service/audit_record_4889/rule_12: UNRESOLVED_POLICY_CONDITION; support_platform/support... |
| case_63 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_64 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_65 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_66 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_67 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_68 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_69 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_70 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_71 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_72 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_73 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_74 | INCOMPLETE | 3 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_75 | INCOMPLETE | 3 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_76 | INCOMPLETE | 0 | no | PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit; UNRESOLVED_POLICY_CONDITION; support_platform/support_9746/rule_05: UNRESOLVED_POLICY_CONDITION |
| case_77 | INCOMPLETE | 0 | no | PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit; UNRESOLVED_POLICY_CONDITION; support_platform/support_008/rule_05: UNRESOLVED_POLICY_CONDITION |
| case_78 | INCOMPLETE | 3 | no | PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit; UNRESOLVED_POLICY_CONDITION; support_platform/support_9652/rule_05: UNRESOLVED_POLICY_CONDITION |
| case_79 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_80 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_81 | INCOMPLETE | 0 | no | PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit; UNRESOLVED_POLICY_CONDITION; support_platform/support_5953/rule_05: UNRESOLVED_POLICY_CONDITION |
| case_82 | INCOMPLETE | 0 | no | PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit; UNRESOLVED_POLICY_CONDITION; support_platform/support_9166/rule_05: UNRESOLVED_POLICY_CONDITION |
| case_83 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_84 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_85 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_86 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_87 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_88 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_89 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_90 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_91 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_92 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_93 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_94 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_95 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_96 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_97 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_98 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
| case_99 | INCOMPLETE | 0 | no | INCOMPLETE_EVIDENCE_COVERAGE; PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts and dependencies require audit |
