# Public sample case exercises

This is a manual evidence and coverage audit, not a solver accuracy result. Public expected outputs were inspected to identify what needs checking; their resource IDs were used as diagnostic search seeds only. State evidence and subject linkage are evaluated separately. These answer-derived seeds must never become solver inputs. All cases authorize deletion or auditing a prior deletion; none exercises NOT_APPLICABLE.

Each case lists the exact expected sequence, directly inspected evidence, and gaps. Evidence search covers every participant text/SQL/JSON/log file, all four PDFs via extraction, and all eleven PNGs via OCR; matching screenshots and relevant PDF pages were visually inspected. OCR negatives are not proof that a visual identifier is absent. An empty/full-snapshot table can support absence without a literal resource-ID match, subject to scope completeness.

## case_01 — expected COMPLETE

- Request: [sample_deletion_requests.csv](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/sample_deletion_requests.csv:2). Expected answer: [sample_output.csv](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/sample_output.csv:2).
- Intent: Simple closure; English. Identity: `user_01`; request email is current; 0 history rows.
- Cutoff: `2026-09-03T11:30:00Z`; reported claim: `COMPLETE`.
- Branch exercised: Primary/failover SQL absence. Policy: USER_PROFILE DELETE; complete verification.
- Observations: Both full exported profile tables in evidence_54 contain only unrelated subjects. This supports absence within that snapshot, but account_001 is known only from the expected answer and an activity claim; no subject-to-account_001 link is established.
- Limitations / decisions: Account-ID provenance and snapshot completeness assumption.
- Expected phase counts: FINDING=0, REMEDIATION=0, VERIFICATION=1. Cited formats: .sql.

| # | Phase | System / resource | Operation → state | Evidence ID |
|---|---|---|---|---|
| 1 | VERIFICATION | `account_service` / `account_001` | `VERIFY_RECORD_ABSENT` → `ABSENT` | `evidence_54` |

Evidence locations (a literal resource match establishes occurrence, not automatically ownership or policy applicability):

| Resource | Admissible evidence occurrence | Other references |
|---|---|---|
| `account_001` | No literal match; inspect absence/snapshot qualification above | [activity_3342](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/system_activity.csv:3343) |

Cited manifest timing: `evidence_54` captured `2026-09-02T23:00:00Z`.

## case_02 — expected COMPLETE

- Request: [sample_deletion_requests.csv](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/sample_deletion_requests.csv:3). Expected answer: [sample_output.csv](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/sample_output.csv:3).
- Intent: Retry failed deletion; Spanish. Identity: `user_02`; request email is current; 0 history rows.
- Cutoff: `2026-09-04T15:00:00Z`; reported claim: `PARTIALLY_COMPLETE`.
- Branch exercised: Reported PARTIALLY_COMPLETE versus observed absence. Policy: USER_PROFILE DELETE; complete verification.
- Observations: The same complete SQL tables contain no matching subject. The worker reports PARTIAL; do not use that to override the snapshot. account_002 lacks an independently established subject link.
- Limitations / decisions: Negative lookup is valid within inspected tables; global completeness is a separate question.
- Expected phase counts: FINDING=0, REMEDIATION=0, VERIFICATION=1. Cited formats: .sql.

| # | Phase | System / resource | Operation → state | Evidence ID |
|---|---|---|---|---|
| 1 | VERIFICATION | `account_service` / `account_002` | `VERIFY_RECORD_ABSENT` → `ABSENT` | `evidence_54` |

Evidence locations (a literal resource match establishes occurrence, not automatically ownership or policy applicability):

| Resource | Admissible evidence occurrence | Other references |
|---|---|---|
| `account_002` | No literal match; inspect absence/snapshot qualification above | [activity_3376](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/system_activity.csv:3377) |

Cited manifest timing: `evidence_54` captured `2026-09-02T23:00:00Z`.

## case_03 — expected COMPLETE

- Request: [sample_deletion_requests.csv](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/sample_deletion_requests.csv:4). Expected answer: [sample_output.csv](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/sample_output.csv:4).
- Intent: Permanent deletion; French. Identity: `user_43`; request email is current; 0 history rows.
- Cutoff: `2026-09-26T11:00:00Z`; reported claim: `COMPLETE`.
- Branch exercised: Account absence, security retention, anonymized analytics. Policy: USER_PROFILE DELETE; SECURITY_AUDIT_LOG RETAIN; ANALYTICS_PROFILE ANONYMIZE.
- Observations: evidence_94 links account_7566 to the request email and returns zero rows; audit_record_2016 links user_43 and has retention_until in 2034. analytics_9406 has all identifiers null, but neither its readback nor activity supplies a subject link.
- Limitations / decisions: Anonymized state is observed; attribution of analytics_9406 to this case is answer-seeded, not independently grounded.
- Expected phase counts: FINDING=0, REMEDIATION=0, VERIFICATION=3. Cited formats: .log.

| # | Phase | System / resource | Operation → state | Evidence ID |
|---|---|---|---|---|
| 1 | VERIFICATION | `account_service` / `account_7566` | `VERIFY_RECORD_ABSENT` → `ABSENT` | `evidence_94` |
| 2 | VERIFICATION | `security_service` / `audit_record_2016` | `VERIFY_RECORD_PRESENT` → `PRESENT` | `evidence_94` |
| 3 | VERIFICATION | `analytics_platform` / `analytics_9406` | `VERIFY_RECORD_ANONYMIZED` → `ANONYMIZED` | `evidence_94` |

Evidence locations (a literal resource match establishes occurrence, not automatically ownership or policy applicability):

| Resource | Admissible evidence occurrence | Other references |
|---|---|---|
| `account_7566` | [evidence_94:18](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/evidence/logs/resource_lookup_trace_20260926_103856.log:18) | [activity_3851](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/system_activity.csv:3852) |
| `analytics_9406` | [evidence_94:42](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/evidence/logs/resource_lookup_trace_20260926_103856.log:42) | [activity_3852](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/system_activity.csv:3853) |
| `audit_record_2016` | [evidence_94:34](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/evidence/logs/resource_lookup_trace_20260926_103856.log:34) | No other match found in searched sources |

Cited manifest timing: `evidence_94` captured `2026-09-26T10:38:56Z`.

## case_04 — expected COMPLETE

- Request: [sample_deletion_requests.csv](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/sample_deletion_requests.csv:5). Expected answer: [sample_output.csv](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/sample_output.csv:5).
- Intent: Delete but keep anonymous statistics; English. Identity: `user_04`; request email is current; 0 history rows.
- Cutoff: `2026-09-07T10:20:00Z`; reported claim: `COMPLETE`.
- Branch exercised: SQL absence plus anonymous JSON. Policy: USER_PROFILE DELETE; ANALYTICS_PROFILE ANONYMIZE.
- Observations: evidence_54 contains no matching profile; evidence_56 analytics_901 has null user_id/email/phone/hash. No subject-to-analytics_901 link was found, and account_004 has no literal occurrence outside the public expected answer in searched text/PDF/OCR.
- Limitations / decisions: A compliant anonymous record cannot be assigned to a person by its position or ID pattern.
- Expected phase counts: FINDING=0, REMEDIATION=0, VERIFICATION=2. Cited formats: .json, .sql.

| # | Phase | System / resource | Operation → state | Evidence ID |
|---|---|---|---|---|
| 1 | VERIFICATION | `account_service` / `account_004` | `VERIFY_RECORD_ABSENT` → `ABSENT` | `evidence_54` |
| 2 | VERIFICATION | `analytics_platform` / `analytics_901` | `VERIFY_RECORD_ANONYMIZED` → `ANONYMIZED` | `evidence_56` |

Evidence locations (a literal resource match establishes occurrence, not automatically ownership or policy applicability):

| Resource | Admissible evidence occurrence | Other references |
|---|---|---|
| `account_004` | No literal match; inspect absence/snapshot qualification above | No other match found in searched sources |
| `analytics_901` | [evidence_56:7](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/evidence/records/customer_analytics_report_20260907.json:7) | [activity_3463](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/system_activity.csv:3464) |

Cited manifest timing: `evidence_54` captured `2026-09-02T23:00:00Z`; `evidence_56` captured `2026-09-07T09:45:00Z`.

## case_05 — expected INCOMPLETE

- Request: [sample_deletion_requests.csv](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/sample_deletion_requests.csv:6). Expected answer: [sample_output.csv](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/sample_output.csv:6).
- Intent: Finish deletion despite recognized email; English. Identity: `user_05`; request email is current; 0 history rows.
- Cutoff: `2026-09-08T13:40:00Z`; reported claim: `COMPLETE`.
- Branch exercised: Primary/replica divergence. Policy: USER_PROFILE DELETE.
- Observations: evidence_54 has account_005 only in the failover replica, with exact subject identifiers. Primary absence does not erase replica presence; SUCCESS activity is contradicted by the readback.
- Limitations / decisions: INCOMPLETE finding is directly grounded; one logical resource represents the replica violation.
- Expected phase counts: FINDING=1, REMEDIATION=1, VERIFICATION=1. Cited formats: .sql.

| # | Phase | System / resource | Operation → state | Evidence ID |
|---|---|---|---|---|
| 1 | FINDING | `account_service` / `account_005` | `REPORT_REMAINING_RECORD` → `PRESENT` | `evidence_54` |
| 2 | REMEDIATION | `account_service` / `account_005` | `DELETE_RECORD` → `ABSENT` | empty (future work) |
| 3 | VERIFICATION | `account_service` / `account_005` | `VERIFY_RECORD_ABSENT` → `ABSENT` | empty (future work) |

Evidence locations (a literal resource match establishes occurrence, not automatically ownership or policy applicability):

| Resource | Admissible evidence occurrence | Other references |
|---|---|---|
| `account_005` | [evidence_54:13](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/evidence/databases/customer_accounts_failover_replica_20260902.sql:13) | [activity_3482](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/system_activity.csv:3483); [activity_3483](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/system_activity.csv:3484) |

Cited manifest timing: `evidence_54` captured `2026-09-02T23:00:00Z`.

## case_06 — expected INCOMPLETE

- Request: [sample_deletion_requests.csv](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/sample_deletion_requests.csv:7). Expected answer: [sample_output.csv](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/sample_output.csv:7).
- Intent: Remove lingering search result; English. Identity: `user_06`; request email is current; 0 history rows.
- Cutoff: `2026-09-10T09:15:00Z`; reported claim: `PARTIALLY_COMPLETE`.
- Branch exercised: Search SQL and foreign-key linkage. Policy: SEARCH_INDEX_ENTRY DELETE; USER_PROFILE absence check.
- Observations: evidence_57 search_001 contains the request email and source account_006. This grounds both resource identities and the remaining search record; account absence is a future check, not established by its worker SUCCESS.
- Limitations / decisions: Do not turn deletion-worker SUCCESS into present-state proof.
- Expected phase counts: FINDING=1, REMEDIATION=1, VERIFICATION=2. Cited formats: .sql.

| # | Phase | System / resource | Operation → state | Evidence ID |
|---|---|---|---|---|
| 1 | FINDING | `search_service` / `search_001` | `REPORT_REMAINING_RECORD` → `PRESENT` | `evidence_57` |
| 2 | REMEDIATION | `search_service` / `search_001` | `DELETE_RECORD` → `ABSENT` | empty (future work) |
| 3 | VERIFICATION | `account_service` / `account_006` | `VERIFY_RECORD_ABSENT` → `ABSENT` | empty (future work) |
| 4 | VERIFICATION | `search_service` / `search_001` | `VERIFY_RECORD_ABSENT` → `ABSENT` | empty (future work) |

Evidence locations (a literal resource match establishes occurrence, not automatically ownership or policy applicability):

| Resource | Admissible evidence occurrence | Other references |
|---|---|---|
| `account_006` | [evidence_57:9](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/evidence/databases/customer_search_primary_20260910.sql:9) | [activity_3545](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/system_activity.csv:3546) |
| `search_001` | [evidence_57:9](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/evidence/databases/customer_search_primary_20260910.sql:9) | [activity_3546](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/system_activity.csv:3547) |

Cited manifest timing: `evidence_57` captured `2026-09-10T08:45:00Z`.

## case_07 — expected INCOMPLETE

- Request: [sample_deletion_requests.csv](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/sample_deletion_requests.csv:8). Expected answer: [sample_output.csv](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/sample_output.csv:8).
- Intent: Delete account and support document; English. Identity: `user_07`; request email is current; 0 history rows.
- Cutoff: `2026-09-12T08:00:00Z`; reported claim: `COMPLETE`.
- Branch exercised: PDF extraction and attachment scope. Policy: SUPPORT_ATTACHMENT DELETE; USER_PROFILE absence check.
- Observations: evidence_58 is a delivery-address-correction PDF with support_001 and exact subject contact fields. It is the evidence artifact, not the current user request. activity_4007 additionally links object_19 exclusively to user_07; evidence_46 shows delivery_confirmation_19.pdf in object storage.
- Limitations / decisions: Canonical output includes support_001 only. object_19 is an additional pre-request candidate; no explicit equivalence to support_001 or later disposition was found. Classify as a scope/identity question, not a proven extra current violation.
- Expected phase counts: FINDING=1, REMEDIATION=1, VERIFICATION=2. Cited formats: .pdf.

| # | Phase | System / resource | Operation → state | Evidence ID |
|---|---|---|---|---|
| 1 | FINDING | `support_platform` / `support_001` | `REPORT_REMAINING_RECORD` → `PRESENT` | `evidence_58` |
| 2 | REMEDIATION | `support_platform` / `support_001` | `DELETE_RECORD` → `ABSENT` | empty (future work) |
| 3 | VERIFICATION | `account_service` / `account_007` | `VERIFY_RECORD_ABSENT` → `ABSENT` | empty (future work) |
| 4 | VERIFICATION | `support_platform` / `support_001` | `VERIFY_RECORD_ABSENT` → `ABSENT` | empty (future work) |

Evidence locations (a literal resource match establishes occurrence, not automatically ownership or policy applicability):

| Resource | Admissible evidence occurrence | Other references |
|---|---|---|
| `account_007` | No literal match; inspect absence/snapshot qualification above | [activity_3590](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/system_activity.csv:3591) |
| `support_001` | [evidence_58 (PDF)](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/evidence/documents/delivery_correction_attachment.pdf) | No other match found in searched sources |

Cited manifest timing: `evidence_58` captured `2026-09-12T07:30:00Z`.

## case_08 — expected INCOMPLETE

- Request: [sample_deletion_requests.csv](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/sample_deletion_requests.csv:9). Expected answer: [sample_output.csv](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/sample_output.csv:9).
- Intent: Delete working export; English. Identity: `user_08`; request email is current; 0 history rows.
- Cutoff: `2026-09-14T16:10:00Z`; reported claim: `PARTIALLY_COMPLETE`.
- Branch exercised: JSON export and retention candidate. Policy: USER_EXPORT DELETE; USER_PROFILE absence check.
- Observations: evidence_59 export_001 matches the request email and download_available=true, with expiry after audit_at. evidence_27 also lists a retained order for user_08.
- Limitations / decisions: Expected account_008 is activity-only and not independently subject-linked. The older financial retention row is an additional obligation candidate requiring policy mapping/current-state confirmation.
- Expected phase counts: FINDING=1, REMEDIATION=1, VERIFICATION=2. Cited formats: .json.

| # | Phase | System / resource | Operation → state | Evidence ID |
|---|---|---|---|---|
| 1 | FINDING | `export_service` / `export_001` | `REPORT_REMAINING_RECORD` → `PRESENT` | `evidence_59` |
| 2 | REMEDIATION | `export_service` / `export_001` | `DELETE_RECORD` → `ABSENT` | empty (future work) |
| 3 | VERIFICATION | `account_service` / `account_008` | `VERIFY_RECORD_ABSENT` → `ABSENT` | empty (future work) |
| 4 | VERIFICATION | `export_service` / `export_001` | `VERIFY_RECORD_ABSENT` → `ABSENT` | empty (future work) |

Evidence locations (a literal resource match establishes occurrence, not automatically ownership or policy applicability):

| Resource | Admissible evidence occurrence | Other references |
|---|---|---|
| `account_008` | No literal match; inspect absence/snapshot qualification above | [activity_3554](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/system_activity.csv:3555) |
| `export_001` | [evidence_59:7](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/evidence/records/customer_export_jobs_20260914.json:7) | [activity_3555](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/system_activity.csv:3556) |

Cited manifest timing: `evidence_59` captured `2026-09-14T15:40:00Z`.

## case_09 — expected INCOMPLETE

- Request: [sample_deletion_requests.csv](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/sample_deletion_requests.csv:10). Expected answer: [sample_output.csv](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/sample_output.csv:10).
- Intent: Permanent deletion; English. Identity: `user_61`; request email is current; 0 history rows.
- Cutoff: `2026-09-16T09:00:00Z`; reported claim: `NOT_STARTED`.
- Branch exercised: Restore risk with collection-time cutoff. Policy: BACKUP_ARCHIVE retain/block restore; SECURITY_AUDIT_LOG retention check.
- Observations: evidence_93 backup_4978 matches the request email and restore_allowed=1. evidence_06 contains account_3960 absence and audit_record_4902 presence observations dated before audit_at, but its manifest capture is Sep18, after Sep16 audit_at.
- Limitations / decisions: Under the stated evidence-capture rule evidence_06 cannot ground the future-check resource links for this case; keep observation time and evidence availability separate.
- Expected phase counts: FINDING=1, REMEDIATION=1, VERIFICATION=3. Cited formats: .sql.

| # | Phase | System / resource | Operation → state | Evidence ID |
|---|---|---|---|---|
| 1 | FINDING | `backup_service` / `backup_4978` | `REPORT_RESTORE_RISK` → `ACTIVE` | `evidence_93` |
| 2 | REMEDIATION | `backup_service` / `backup_4978` | `BLOCK_RESTORE` → `BLOCKED` | empty (future work) |
| 3 | VERIFICATION | `account_service` / `account_3960` | `VERIFY_RECORD_ABSENT` → `ABSENT` | empty (future work) |
| 4 | VERIFICATION | `security_service` / `audit_record_4902` | `VERIFY_RECORD_PRESENT` → `PRESENT` | empty (future work) |
| 5 | VERIFICATION | `backup_service` / `backup_4978` | `VERIFY_RESTORE_BLOCKED` → `BLOCKED` | empty (future work) |

Evidence locations (a literal resource match establishes occurrence, not automatically ownership or policy applicability):

| Resource | Admissible evidence occurrence | Other references |
|---|---|---|
| `account_3960` | No literal match; inspect absence/snapshot qualification above | [activity_3703](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/system_activity.csv:3704) ; [evidence_06 AFTER CUTOFF](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/evidence/logs/structured_service_events_eu_west_20260918.log:86) |
| `audit_record_4902` | No literal match; inspect absence/snapshot qualification above | [evidence_06 AFTER CUTOFF](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/evidence/logs/structured_service_events_eu_west_20260918.log:28) |
| `backup_4978` | [evidence_93:24](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/evidence/databases/customer_data_inventory_20260916.sql:24) | [activity_3709](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/system_activity.csv:3710) ; [evidence_06 AFTER CUTOFF](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/evidence/logs/structured_service_events_eu_west_20260918.log:83) |

Cited manifest timing: `evidence_93` captured `2026-09-16T08:37:39Z`.

## case_10 — expected INCOMPLETE

- Request: [sample_deletion_requests.csv](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/sample_deletion_requests.csv:11). Expected answer: [sample_output.csv](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/sample_output.csv:11).
- Intent: Delete old and current email records; English. Identity: `user_10`; request email is historical; 4 history rows (email, email_hash).
- Cutoff: `2026-09-18T12:25:00Z`; reported claim: `COMPLETE`.
- Branch exercised: Two email/hash transitions and trace join. Policy: Contact/secondary identifier DELETE; USER_PROFILE absence check.
- Observations: The request email is historical. Four audit rows form two email/hash transitions. evidence_61 joins lookup by the earliest email to support_002 through trace_id; rows=1 and deletion_marker=false prove a surviving contact record despite worker SUCCESS.
- Limitations / decisions: Record type must follow contents, not support_ prefix. account_010 is activity-only with no independently found subject link.
- Expected phase counts: FINDING=1, REMEDIATION=1, VERIFICATION=2. Cited formats: .log.

| # | Phase | System / resource | Operation → state | Evidence ID |
|---|---|---|---|---|
| 1 | FINDING | `support_platform` / `support_002` | `REPORT_REMAINING_RECORD` → `PRESENT` | `evidence_61` |
| 2 | REMEDIATION | `support_platform` / `support_002` | `DELETE_RECORD` → `ABSENT` | empty (future work) |
| 3 | VERIFICATION | `account_service` / `account_010` | `VERIFY_RECORD_ABSENT` → `ABSENT` | empty (future work) |
| 4 | VERIFICATION | `support_platform` / `support_002` | `VERIFY_RECORD_ABSENT` → `ABSENT` | empty (future work) |

Evidence locations (a literal resource match establishes occurrence, not automatically ownership or policy applicability):

| Resource | Admissible evidence occurrence | Other references |
|---|---|---|
| `account_010` | No literal match; inspect absence/snapshot qualification above | [activity_3595](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/system_activity.csv:3596) |
| `support_002` | [evidence_61:5](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/evidence/logs/support_replica.log:5) | [activity_3596](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/system_activity.csv:3597) |

Cited manifest timing: `evidence_61` captured `2026-09-17T22:00:19Z`.

## case_11 — expected INCOMPLETE

- Request: [sample_deletion_requests.csv](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/sample_deletion_requests.csv:12). Expected answer: [sample_output.csv](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/sample_output.csv:12).
- Intent: Erase account and copies; English. Identity: `user_32`; request email is current; 0 history rows.
- Cutoff: `2026-10-01T12:00:00Z`; reported claim: `COMPLETE`.
- Branch exercised: Four violations with mixed treatments. Policy: SEARCH_INDEX_ENTRY DELETE; SUPPORT_MESSAGE REDACT; ANALYTICS_PROFILE ANONYMIZE; DATA_FLOW disable; SECURITY_AUDIT_LOG retain.
- Observations: evidence_03 at exactly audit_at links account_4248 absent, search_052 present, support_864 identifiable, analytics_2034 identifiable, data_flow_9522 active, and audit_record_9394 present to the subject.
- Limitations / decisions: All expected resources have subject-linked handover observations. Conditional support retention/security retention context is less explicit than the state labels; do not assume policy solely from IDs.
- Expected phase counts: FINDING=4, REMEDIATION=4, VERIFICATION=6. Cited formats: .txt.

| # | Phase | System / resource | Operation → state | Evidence ID |
|---|---|---|---|---|
| 1 | FINDING | `search_service` / `search_052` | `REPORT_REMAINING_RECORD` → `PRESENT` | `evidence_03` |
| 2 | FINDING | `analytics_platform` / `analytics_2034` | `REPORT_EXPOSED_PII` → `PRESENT` | `evidence_03` |
| 3 | FINDING | `support_platform` / `support_864` | `REPORT_EXPOSED_PII` → `PRESENT` | `evidence_03` |
| 4 | FINDING | `integration_service` / `data_flow_9522` | `REPORT_ACTIVE_DATA_FLOW` → `ACTIVE` | `evidence_03` |
| 5 | REMEDIATION | `integration_service` / `data_flow_9522` | `DISABLE_DATA_FLOW` → `DISABLED` | empty (future work) |
| 6 | REMEDIATION | `search_service` / `search_052` | `DELETE_RECORD` → `ABSENT` | empty (future work) |
| 7 | REMEDIATION | `support_platform` / `support_864` | `REDACT_RECORD` → `REDACTED` | empty (future work) |
| 8 | REMEDIATION | `analytics_platform` / `analytics_2034` | `ANONYMIZE_RECORD` → `ANONYMIZED` | empty (future work) |
| 9 | VERIFICATION | `account_service` / `account_4248` | `VERIFY_RECORD_ABSENT` → `ABSENT` | empty (future work) |
| 10 | VERIFICATION | `search_service` / `search_052` | `VERIFY_RECORD_ABSENT` → `ABSENT` | empty (future work) |
| 11 | VERIFICATION | `security_service` / `audit_record_9394` | `VERIFY_RECORD_PRESENT` → `PRESENT` | empty (future work) |
| 12 | VERIFICATION | `support_platform` / `support_864` | `VERIFY_RECORD_REDACTED` → `REDACTED` | empty (future work) |
| 13 | VERIFICATION | `analytics_platform` / `analytics_2034` | `VERIFY_RECORD_ANONYMIZED` → `ANONYMIZED` | empty (future work) |
| 14 | VERIFICATION | `integration_service` / `data_flow_9522` | `VERIFY_DATA_FLOW_DISABLED` → `DISABLED` | empty (future work) |

Evidence locations (a literal resource match establishes occurrence, not automatically ownership or policy applicability):

| Resource | Admissible evidence occurrence | Other references |
|---|---|---|
| `account_4248` | [evidence_03:11](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/evidence/records/customer_account_handover_20261001.txt:11) | [activity_3801](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/system_activity.csv:3802) |
| `analytics_2034` | [evidence_03:16](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/evidence/records/customer_account_handover_20261001.txt:16) | [activity_3816](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/system_activity.csv:3817) |
| `audit_record_9394` | [evidence_03:40](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/evidence/records/customer_account_handover_20261001.txt:40) | No other match found in searched sources |
| `data_flow_9522` | [evidence_03:25](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/evidence/records/customer_account_handover_20261001.txt:25) | [activity_3817](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/system_activity.csv:3818) |
| `search_052` | [evidence_03:26](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/evidence/records/customer_account_handover_20261001.txt:26) | [activity_3814](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/system_activity.csv:3815) |
| `support_864` | [evidence_03:46](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/evidence/records/customer_account_handover_20261001.txt:46) | [activity_3815](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/system_activity.csv:3816) |

Cited manifest timing: `evidence_03` captured `2026-10-01T12:00:00Z`.

## case_12 — expected INCOMPLETE

- Request: [sample_deletion_requests.csv](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/sample_deletion_requests.csv:13). Expected answer: [sample_output.csv](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/sample_output.csv:13).
- Intent: Delete old email including undisplayed identifiers; English. Identity: `user_12`; request email is current; 2 history rows (email, email_hash).
- Cutoff: `2026-09-15T12:00:00Z`; reported claim: `COMPLETE`.
- Branch exercised: Historical hash and category versus system name. Policy: Contact/marketing record DELETE rather than analytics ANONYMIZE.
- Observations: History supplies the old email hash; evidence_01 contact_lookup_completed on analytics_9914 uses that hash and rows=1/email_opt_in=true. Account absence and security presence are independently linked by correlation key/trace.
- Limitations / decisions: The public answer chooses DELETE. Analytics platform and analytics_ prefix do not establish ANALYTICS_PROFILE. The event suggests a contact/marketing record, but explicit category metadata is sparse. evidence_27 adds a retained-order candidate.
- Expected phase counts: FINDING=1, REMEDIATION=1, VERIFICATION=3. Cited formats: .log.

| # | Phase | System / resource | Operation → state | Evidence ID |
|---|---|---|---|---|
| 1 | FINDING | `analytics_platform` / `analytics_9914` | `REPORT_REMAINING_RECORD` → `PRESENT` | `evidence_01` |
| 2 | REMEDIATION | `analytics_platform` / `analytics_9914` | `DELETE_RECORD` → `ABSENT` | empty (future work) |
| 3 | VERIFICATION | `account_service` / `account_9797` | `VERIFY_RECORD_ABSENT` → `ABSENT` | empty (future work) |
| 4 | VERIFICATION | `analytics_platform` / `analytics_9914` | `VERIFY_RECORD_ABSENT` → `ABSENT` | empty (future work) |
| 5 | VERIFICATION | `security_service` / `audit_record_2945` | `VERIFY_RECORD_PRESENT` → `PRESENT` | empty (future work) |

Evidence locations (a literal resource match establishes occurrence, not automatically ownership or policy applicability):

| Resource | Admissible evidence occurrence | Other references |
|---|---|---|
| `account_9797` | [evidence_01:76](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/evidence/logs/service_events_ap_south_20260915.log:76) | [activity_3432](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/system_activity.csv:3433) |
| `analytics_9914` | [evidence_01:92](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/evidence/logs/service_events_ap_south_20260915.log:92) | [activity_3435](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/system_activity.csv:3436) |
| `audit_record_2945` | [evidence_01:63](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/evidence/logs/service_events_ap_south_20260915.log:63) | No other match found in searched sources |

Cited manifest timing: `evidence_01` captured `2026-09-15T11:59:39Z`.

## case_13 — expected INCOMPLETE

- Request: [sample_deletion_requests.csv](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/sample_deletion_requests.csv:14). Expected answer: [sample_output.csv](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/sample_output.csv:14).
- Intent: Close account and delete personal data; English. Identity: `user_33`; request email is current; 0 history rows.
- Cutoff: `2026-10-01T12:00:00Z`; reported claim: `NOT_STARTED`.
- Branch exercised: Two delete categories plus retention. Policy: SEARCH_INDEX_ENTRY DELETE; SUPPORT_ATTACHMENT DELETE; SECURITY_AUDIT_LOG RETAIN.
- Observations: evidence_03 links account_9335 absent, search_1308 present, support_4218 SUPPORT_ATTACHMENT present, and audit_record_4816 present.
- Limitations / decisions: Canonical deletion order is search then support by system_id, with no demonstrated source dependency between them. Exclusive attachment ownership is not separately explicit.
- Expected phase counts: FINDING=2, REMEDIATION=2, VERIFICATION=4. Cited formats: .txt.

| # | Phase | System / resource | Operation → state | Evidence ID |
|---|---|---|---|---|
| 1 | FINDING | `search_service` / `search_1308` | `REPORT_REMAINING_RECORD` → `PRESENT` | `evidence_03` |
| 2 | FINDING | `support_platform` / `support_4218` | `REPORT_REMAINING_RECORD` → `PRESENT` | `evidence_03` |
| 3 | REMEDIATION | `search_service` / `search_1308` | `DELETE_RECORD` → `ABSENT` | empty (future work) |
| 4 | REMEDIATION | `support_platform` / `support_4218` | `DELETE_RECORD` → `ABSENT` | empty (future work) |
| 5 | VERIFICATION | `account_service` / `account_9335` | `VERIFY_RECORD_ABSENT` → `ABSENT` | empty (future work) |
| 6 | VERIFICATION | `search_service` / `search_1308` | `VERIFY_RECORD_ABSENT` → `ABSENT` | empty (future work) |
| 7 | VERIFICATION | `support_platform` / `support_4218` | `VERIFY_RECORD_ABSENT` → `ABSENT` | empty (future work) |
| 8 | VERIFICATION | `security_service` / `audit_record_4816` | `VERIFY_RECORD_PRESENT` → `PRESENT` | empty (future work) |

Evidence locations (a literal resource match establishes occurrence, not automatically ownership or policy applicability):

| Resource | Admissible evidence occurrence | Other references |
|---|---|---|
| `account_9335` | [evidence_03:15](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/evidence/records/customer_account_handover_20261001.txt:15) | [activity_3739](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/system_activity.csv:3740) |
| `audit_record_4816` | [evidence_03:34](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/evidence/records/customer_account_handover_20261001.txt:34) | No other match found in searched sources |
| `search_1308` | [evidence_03:27](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/evidence/records/customer_account_handover_20261001.txt:27) | [activity_3756](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/system_activity.csv:3757) |
| `support_4218` | [evidence_03:43](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/evidence/records/customer_account_handover_20261001.txt:43) | [activity_3752](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/system_activity.csv:3753) |

Cited manifest timing: `evidence_03` captured `2026-10-01T12:00:00Z`.

## case_14 — expected INCOMPLETE

- Request: [sample_deletion_requests.csv](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/sample_deletion_requests.csv:15). Expected answer: [sample_output.csv](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/sample_output.csv:15).
- Intent: Permanent deletion; Japanese. Identity: `user_37`; request email is current; 0 history rows.
- Cutoff: `2026-10-01T12:00:00Z`; reported claim: `COMPLETE`.
- Branch exercised: Active backup while account absent. Policy: BACKUP_ARCHIVE retain/block restore; SECURITY_AUDIT_LOG retain.
- Observations: evidence_03 at audit_at links account_3677 absent, backup_3870 ACTIVE, and audit_record_987 present.
- Limitations / decisions: BLOCK_RESTORE preserves the archive; do not invent DELETE_RECORD for the backup.
- Expected phase counts: FINDING=1, REMEDIATION=1, VERIFICATION=3. Cited formats: .txt.

| # | Phase | System / resource | Operation → state | Evidence ID |
|---|---|---|---|---|
| 1 | FINDING | `backup_service` / `backup_3870` | `REPORT_RESTORE_RISK` → `ACTIVE` | `evidence_03` |
| 2 | REMEDIATION | `backup_service` / `backup_3870` | `BLOCK_RESTORE` → `BLOCKED` | empty (future work) |
| 3 | VERIFICATION | `account_service` / `account_3677` | `VERIFY_RECORD_ABSENT` → `ABSENT` | empty (future work) |
| 4 | VERIFICATION | `security_service` / `audit_record_987` | `VERIFY_RECORD_PRESENT` → `PRESENT` | empty (future work) |
| 5 | VERIFICATION | `backup_service` / `backup_3870` | `VERIFY_RESTORE_BLOCKED` → `BLOCKED` | empty (future work) |

Evidence locations (a literal resource match establishes occurrence, not automatically ownership or policy applicability):

| Resource | Admissible evidence occurrence | Other references |
|---|---|---|
| `account_3677` | [evidence_03:9](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/evidence/records/customer_account_handover_20261001.txt:9) | [activity_3686](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/system_activity.csv:3687) |
| `audit_record_987` | [evidence_03:41](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/evidence/records/customer_account_handover_20261001.txt:41) | No other match found in searched sources |
| `backup_3870` | [evidence_03:19](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/evidence/records/customer_account_handover_20261001.txt:19) | [activity_3690](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/system_activity.csv:3691) |

Cited manifest timing: `evidence_03` captured `2026-10-01T12:00:00Z`.

## case_15 — expected INCOMPLETE

- Request: [sample_deletion_requests.csv](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/sample_deletion_requests.csv:16). Expected answer: [sample_output.csv](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/sample_output.csv:16).
- Intent: Close account and stop integration; English. Identity: `user_15`; request email is current; 1 history rows (phone).
- Cutoff: `2026-09-15T12:00:00Z`; reported claim: `COMPLETE`.
- Branch exercised: Only active flow violates policy. Policy: DATA_FLOW disable; USER_PROFILE absence; SECURITY_AUDIT_LOG retain.
- Observations: evidence_01 joins connector heartbeat to the request email: enabled=true/scheduler_registered=true. Account absent and security record present are linked. evidence_14 image corroborates the same connector earlier, visually inspected.
- Limitations / decisions: The old phone audit row expands identity but is not needed for this evidence. No remaining-record finding is needed when the only violation is an active flow.
- Expected phase counts: FINDING=1, REMEDIATION=1, VERIFICATION=3. Cited formats: .log.

| # | Phase | System / resource | Operation → state | Evidence ID |
|---|---|---|---|---|
| 1 | FINDING | `integration_service` / `data_flow_9846` | `REPORT_ACTIVE_DATA_FLOW` → `ACTIVE` | `evidence_01` |
| 2 | REMEDIATION | `integration_service` / `data_flow_9846` | `DISABLE_DATA_FLOW` → `DISABLED` | empty (future work) |
| 3 | VERIFICATION | `account_service` / `account_4745` | `VERIFY_RECORD_ABSENT` → `ABSENT` | empty (future work) |
| 4 | VERIFICATION | `security_service` / `audit_record_1596` | `VERIFY_RECORD_PRESENT` → `PRESENT` | empty (future work) |
| 5 | VERIFICATION | `integration_service` / `data_flow_9846` | `VERIFY_DATA_FLOW_DISABLED` → `DISABLED` | empty (future work) |

Evidence locations (a literal resource match establishes occurrence, not automatically ownership or policy applicability):

| Resource | Admissible evidence occurrence | Other references |
|---|---|---|
| `account_4745` | [evidence_01:22](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/evidence/logs/service_events_ap_south_20260915.log:22) | [activity_3382](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/system_activity.csv:3383) |
| `audit_record_1596` | [evidence_01:103](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/evidence/logs/service_events_ap_south_20260915.log:103) | No other match found in searched sources |
| `data_flow_9846` | [evidence_01:88](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/evidence/logs/service_events_ap_south_20260915.log:88) | [activity_3386](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/system_activity.csv:3387) |

Cited manifest timing: `evidence_01` captured `2026-09-15T11:59:39Z`.

## case_16 — expected INCOMPLETE

- Request: [sample_deletion_requests.csv](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/sample_deletion_requests.csv:17). Expected answer: [sample_output.csv](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/sample_output.csv:17).
- Intent: Permanent deletion; English. Identity: `user_53`; request email is current; 0 history rows.
- Cutoff: `2026-09-21T10:00:00Z`; reported claim: `NOT_STARTED`.
- Branch exercised: Read-replica drift plus search copy. Policy: USER_PROFILE DELETE; SEARCH_INDEX_ENTRY DELETE; SECURITY_AUDIT_LOG RETAIN.
- Observations: evidence_05 primary lacks account_994 while read replica contains exact identifiers; search_1007 and audit_record_9528 occur in primary and replica.
- Limitations / decisions: Canonical order deletes account before search. Do not infer search must be first merely from its name; dependency-safe order requires an explicit edge. Deduplicate identical logical resource IDs across replicas while retaining copy-level proof.
- Expected phase counts: FINDING=2, REMEDIATION=2, VERIFICATION=3. Cited formats: .sql.

| # | Phase | System / resource | Operation → state | Evidence ID |
|---|---|---|---|---|
| 1 | FINDING | `account_service` / `account_994` | `REPORT_REMAINING_RECORD` → `PRESENT` | `evidence_05` |
| 2 | FINDING | `search_service` / `search_1007` | `REPORT_REMAINING_RECORD` → `PRESENT` | `evidence_05` |
| 3 | REMEDIATION | `account_service` / `account_994` | `DELETE_RECORD` → `ABSENT` | empty (future work) |
| 4 | REMEDIATION | `search_service` / `search_1007` | `DELETE_RECORD` → `ABSENT` | empty (future work) |
| 5 | VERIFICATION | `account_service` / `account_994` | `VERIFY_RECORD_ABSENT` → `ABSENT` | empty (future work) |
| 6 | VERIFICATION | `search_service` / `search_1007` | `VERIFY_RECORD_ABSENT` → `ABSENT` | empty (future work) |
| 7 | VERIFICATION | `security_service` / `audit_record_9528` | `VERIFY_RECORD_PRESENT` → `PRESENT` | empty (future work) |

Evidence locations (a literal resource match establishes occurrence, not automatically ownership or policy applicability):

| Resource | Admissible evidence occurrence | Other references |
|---|---|---|
| `account_994` | [evidence_05:52](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/evidence/databases/customer_data_read_replica_20260921.sql:52) | [activity_3571](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/system_activity.csv:3572); [activity_3577](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/system_activity.csv:3578) |
| `audit_record_9528` | [evidence_05:29](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/evidence/databases/customer_data_read_replica_20260921.sql:29) | No other match found in searched sources |
| `search_1007` | [evidence_05:37](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/evidence/databases/customer_data_read_replica_20260921.sql:37) | [activity_3580](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/system_activity.csv:3581) |

Cited manifest timing: `evidence_05` captured `2026-09-21T10:00:00Z`.

## case_17 — expected INCOMPLETE

- Request: [sample_deletion_requests.csv](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/sample_deletion_requests.csv:18). Expected answer: [sample_output.csv](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/sample_output.csv:18).
- Intent: Close account; backups may remain if blocked; English. Identity: `user_17`; request email is current; 0 history rows.
- Cutoff: `2026-09-15T12:00:00Z`; reported claim: `NOT_STARTED`.
- Branch exercised: Restore risk and additional tombstone candidate. Policy: BACKUP_ARCHIVE block restore; SECURITY_AUDIT_LOG retain; candidate ACCOUNT_TOMBSTONE redact/retain reference.
- Observations: evidence_01 links account_4092 absent, backup_3245 eligible=true/deletion_block=false, audit_record_1797 present. activity_4011 links tombstone_17 to user_17; evidence_42 visually shows only the retained stable user reference and related records.
- Limitations / decisions: Expected output omits the older tombstone and legal-order candidates. Their current scope is unresolved; do not delete a stable reference simply because it identifies the internal subject.
- Expected phase counts: FINDING=1, REMEDIATION=1, VERIFICATION=3. Cited formats: .log.

| # | Phase | System / resource | Operation → state | Evidence ID |
|---|---|---|---|---|
| 1 | FINDING | `backup_service` / `backup_3245` | `REPORT_RESTORE_RISK` → `ACTIVE` | `evidence_01` |
| 2 | REMEDIATION | `backup_service` / `backup_3245` | `BLOCK_RESTORE` → `BLOCKED` | empty (future work) |
| 3 | VERIFICATION | `account_service` / `account_4092` | `VERIFY_RECORD_ABSENT` → `ABSENT` | empty (future work) |
| 4 | VERIFICATION | `security_service` / `audit_record_1797` | `VERIFY_RECORD_PRESENT` → `PRESENT` | empty (future work) |
| 5 | VERIFICATION | `backup_service` / `backup_3245` | `VERIFY_RESTORE_BLOCKED` → `BLOCKED` | empty (future work) |

Evidence locations (a literal resource match establishes occurrence, not automatically ownership or policy applicability):

| Resource | Admissible evidence occurrence | Other references |
|---|---|---|
| `account_4092` | [evidence_01:21](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/evidence/logs/service_events_ap_south_20260915.log:21) | [activity_3383](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/system_activity.csv:3384) |
| `audit_record_1797` | [evidence_01:33](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/evidence/logs/service_events_ap_south_20260915.log:33) | No other match found in searched sources |
| `backup_3245` | [evidence_01:53](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/evidence/logs/service_events_ap_south_20260915.log:53) | [activity_3385](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/system_activity.csv:3386) |

Cited manifest timing: `evidence_01` captured `2026-09-15T11:59:39Z`.

## case_18 — expected INCOMPLETE

- Request: [sample_deletion_requests.csv](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/sample_deletion_requests.csv:19). Expected answer: [sample_output.csv](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/sample_output.csv:19).
- Intent: Remove account and personal data; English. Identity: `user_50`; request email is current; 1 history rows (phone).
- Cutoff: `2026-09-26T11:00:00Z`; reported claim: `COMPLETE`.
- Branch exercised: Four observed violations, incomplete verification provenance. Policy: DELETE search; REDACT support; ANONYMIZE analytics; DISABLE flow.
- Observations: evidence_94 links search_4013 present, support_5569 exposed, analytics_037 exposed and data_flow_4890 enabled to the request email.
- Limitations / decisions: account_5521 is an unlinked activity claim; audit_record_6645 is not found outside expected answers in searched participant text/PDF/OCR. The INCOMPLETE verdict is grounded, but the full expected verification scope is not.
- Expected phase counts: FINDING=4, REMEDIATION=4, VERIFICATION=6. Cited formats: .log.

| # | Phase | System / resource | Operation → state | Evidence ID |
|---|---|---|---|---|
| 1 | FINDING | `search_service` / `search_4013` | `REPORT_REMAINING_RECORD` → `PRESENT` | `evidence_94` |
| 2 | FINDING | `analytics_platform` / `analytics_037` | `REPORT_EXPOSED_PII` → `PRESENT` | `evidence_94` |
| 3 | FINDING | `support_platform` / `support_5569` | `REPORT_EXPOSED_PII` → `PRESENT` | `evidence_94` |
| 4 | FINDING | `integration_service` / `data_flow_4890` | `REPORT_ACTIVE_DATA_FLOW` → `ACTIVE` | `evidence_94` |
| 5 | REMEDIATION | `integration_service` / `data_flow_4890` | `DISABLE_DATA_FLOW` → `DISABLED` | empty (future work) |
| 6 | REMEDIATION | `search_service` / `search_4013` | `DELETE_RECORD` → `ABSENT` | empty (future work) |
| 7 | REMEDIATION | `support_platform` / `support_5569` | `REDACT_RECORD` → `REDACTED` | empty (future work) |
| 8 | REMEDIATION | `analytics_platform` / `analytics_037` | `ANONYMIZE_RECORD` → `ANONYMIZED` | empty (future work) |
| 9 | VERIFICATION | `account_service` / `account_5521` | `VERIFY_RECORD_ABSENT` → `ABSENT` | empty (future work) |
| 10 | VERIFICATION | `search_service` / `search_4013` | `VERIFY_RECORD_ABSENT` → `ABSENT` | empty (future work) |
| 11 | VERIFICATION | `security_service` / `audit_record_6645` | `VERIFY_RECORD_PRESENT` → `PRESENT` | empty (future work) |
| 12 | VERIFICATION | `support_platform` / `support_5569` | `VERIFY_RECORD_REDACTED` → `REDACTED` | empty (future work) |
| 13 | VERIFICATION | `analytics_platform` / `analytics_037` | `VERIFY_RECORD_ANONYMIZED` → `ANONYMIZED` | empty (future work) |
| 14 | VERIFICATION | `integration_service` / `data_flow_4890` | `VERIFY_DATA_FLOW_DISABLED` → `DISABLED` | empty (future work) |

Evidence locations (a literal resource match establishes occurrence, not automatically ownership or policy applicability):

| Resource | Admissible evidence occurrence | Other references |
|---|---|---|
| `account_5521` | No literal match; inspect absence/snapshot qualification above | [activity_3732](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/system_activity.csv:3733) |
| `analytics_037` | [evidence_94:22](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/evidence/logs/resource_lookup_trace_20260926_103856.log:22) | [activity_3751](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/system_activity.csv:3752) |
| `audit_record_6645` | No literal match; inspect absence/snapshot qualification above | No other match found in searched sources |
| `data_flow_4890` | [evidence_94:24](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/evidence/logs/resource_lookup_trace_20260926_103856.log:24) | [activity_3753](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/system_activity.csv:3754) |
| `search_4013` | [evidence_94:52](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/evidence/logs/resource_lookup_trace_20260926_103856.log:52) | [activity_3747](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/system_activity.csv:3748) |
| `support_5569` | [evidence_94:10](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/evidence/logs/resource_lookup_trace_20260926_103856.log:10) | [activity_3744](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/system_activity.csv:3745) |

Cited manifest timing: `evidence_94` captured `2026-09-26T10:38:56Z`.

## case_19 — expected INCOMPLETE

- Request: [sample_deletion_requests.csv](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/sample_deletion_requests.csv:20). Expected answer: [sample_output.csv](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/sample_output.csv:20).
- Intent: Delete profile; retain shared conversation context; English. Identity: `user_19`; request email is current; 0 history rows.
- Cutoff: `2026-09-15T12:00:00Z`; reported claim: `PARTIALLY_COMPLETE`.
- Branch exercised: Trace correlation and explicit shared-context retention. Policy: SEARCH_INDEX_ENTRY DELETE; SUPPORT_MESSAGE REDACT; SECURITY_AUDIT_LOG retain.
- Observations: evidence_01 joins email to search_6083 hit, support_9553 PII scan, account_9102 absent and audit_record_6793 present. The request explicitly explains why the conversation must remain.
- Limitations / decisions: Strong example for redaction versus deletion. Trace IDs carry the identity across interleaved log lines.
- Expected phase counts: FINDING=2, REMEDIATION=2, VERIFICATION=4. Cited formats: .log.

| # | Phase | System / resource | Operation → state | Evidence ID |
|---|---|---|---|---|
| 1 | FINDING | `search_service` / `search_6083` | `REPORT_REMAINING_RECORD` → `PRESENT` | `evidence_01` |
| 2 | FINDING | `support_platform` / `support_9553` | `REPORT_EXPOSED_PII` → `PRESENT` | `evidence_01` |
| 3 | REMEDIATION | `search_service` / `search_6083` | `DELETE_RECORD` → `ABSENT` | empty (future work) |
| 4 | REMEDIATION | `support_platform` / `support_9553` | `REDACT_RECORD` → `REDACTED` | empty (future work) |
| 5 | VERIFICATION | `account_service` / `account_9102` | `VERIFY_RECORD_ABSENT` → `ABSENT` | empty (future work) |
| 6 | VERIFICATION | `search_service` / `search_6083` | `VERIFY_RECORD_ABSENT` → `ABSENT` | empty (future work) |
| 7 | VERIFICATION | `security_service` / `audit_record_6793` | `VERIFY_RECORD_PRESENT` → `PRESENT` | empty (future work) |
| 8 | VERIFICATION | `support_platform` / `support_9553` | `VERIFY_RECORD_REDACTED` → `REDACTED` | empty (future work) |

Evidence locations (a literal resource match establishes occurrence, not automatically ownership or policy applicability):

| Resource | Admissible evidence occurrence | Other references |
|---|---|---|
| `account_9102` | [evidence_01:72](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/evidence/logs/service_events_ap_south_20260915.log:72) | [activity_3323](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/system_activity.csv:3324) |
| `audit_record_6793` | [evidence_01:44](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/evidence/logs/service_events_ap_south_20260915.log:44) | No other match found in searched sources |
| `search_6083` | [evidence_01:36](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/evidence/logs/service_events_ap_south_20260915.log:36) | [activity_3332](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/system_activity.csv:3333) |
| `support_9553` | [evidence_01:15](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/evidence/logs/service_events_ap_south_20260915.log:15) | [activity_3329](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/system_activity.csv:3330) |

Cited manifest timing: `evidence_01` captured `2026-09-15T11:59:39Z`.

## case_20 — expected INCOMPLETE

- Request: [sample_deletion_requests.csv](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/sample_deletion_requests.csv:21). Expected answer: [sample_output.csv](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/sample_output.csv:21).
- Intent: Permanent deletion; English. Identity: `user_48`; request email is current; 0 history rows.
- Cutoff: `2026-09-26T11:00:00Z`; reported claim: `NOT_STARTED`.
- Branch exercised: Search plus active connector. Policy: SEARCH_INDEX_ENTRY DELETE; DATA_FLOW disable.
- Observations: evidence_94 links search_4262 hit and data_flow_1770 enabled to the request email. Both are before the cutoff.
- Limitations / decisions: account_5037 occurs only in activity_3734, without subject ID/email/case ID. audit_record_5569 is absent from searched text, extracted PDFs and image OCR outside sample_output. No independent support for those two future-check IDs was found.
- Expected phase counts: FINDING=2, REMEDIATION=2, VERIFICATION=4. Cited formats: .log.

| # | Phase | System / resource | Operation → state | Evidence ID |
|---|---|---|---|---|
| 1 | FINDING | `search_service` / `search_4262` | `REPORT_REMAINING_RECORD` → `PRESENT` | `evidence_94` |
| 2 | FINDING | `integration_service` / `data_flow_1770` | `REPORT_ACTIVE_DATA_FLOW` → `ACTIVE` | `evidence_94` |
| 3 | REMEDIATION | `integration_service` / `data_flow_1770` | `DISABLE_DATA_FLOW` → `DISABLED` | empty (future work) |
| 4 | REMEDIATION | `search_service` / `search_4262` | `DELETE_RECORD` → `ABSENT` | empty (future work) |
| 5 | VERIFICATION | `account_service` / `account_5037` | `VERIFY_RECORD_ABSENT` → `ABSENT` | empty (future work) |
| 6 | VERIFICATION | `search_service` / `search_4262` | `VERIFY_RECORD_ABSENT` → `ABSENT` | empty (future work) |
| 7 | VERIFICATION | `security_service` / `audit_record_5569` | `VERIFY_RECORD_PRESENT` → `PRESENT` | empty (future work) |
| 8 | VERIFICATION | `integration_service` / `data_flow_1770` | `VERIFY_DATA_FLOW_DISABLED` → `DISABLED` | empty (future work) |

Evidence locations (a literal resource match establishes occurrence, not automatically ownership or policy applicability):

| Resource | Admissible evidence occurrence | Other references |
|---|---|---|
| `account_5037` | No literal match; inspect absence/snapshot qualification above | [activity_3734](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/system_activity.csv:3735) |
| `audit_record_5569` | No literal match; inspect absence/snapshot qualification above | No other match found in searched sources |
| `data_flow_1770` | [evidence_94:40](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/evidence/logs/resource_lookup_trace_20260926_103856.log:40) | [activity_3745](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/system_activity.csv:3746) |
| `search_4262` | [evidence_94:8](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/evidence/logs/resource_lookup_trace_20260926_103856.log:8) | [activity_3750](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/system_activity.csv:3751) |

Cited manifest timing: `evidence_94` captured `2026-09-26T10:38:56Z`.

## case_21 — expected COMPLETE

- Request: [sample_deletion_requests.csv](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/sample_deletion_requests.csv:22). Expected answer: [sample_output.csv](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/sample_output.csv:22).
- Intent: Audit prior deletion; English. Identity: `user_21`; request email is current; 0 history rows.
- Cutoff: `2026-09-15T12:00:00Z`; reported claim: `COMPLETE`.
- Branch exercised: Complete readbacks but anonymous-resource linkage gap. Policy: USER_PROFILE absent; ANALYTICS_PROFILE anonymized; SECURITY_AUDIT_LOG retained.
- Observations: evidence_92 shows account_6440 404, analytics_5335 null identifiers, and audit_record_3737 linked to user_21 with retention through 2034.
- Limitations / decisions: Account/analytics states exist but are not subject-linked in admissible evidence. evidence_02 is exported after audit_at and cannot repair this. evidence_27 supplies a separate retained-order candidate.
- Expected phase counts: FINDING=0, REMEDIATION=0, VERIFICATION=3. Cited formats: .json.

| # | Phase | System / resource | Operation → state | Evidence ID |
|---|---|---|---|---|
| 1 | VERIFICATION | `account_service` / `account_6440` | `VERIFY_RECORD_ABSENT` → `ABSENT` | `evidence_92` |
| 2 | VERIFICATION | `security_service` / `audit_record_3737` | `VERIFY_RECORD_PRESENT` → `PRESENT` | `evidence_92` |
| 3 | VERIFICATION | `analytics_platform` / `analytics_5335` | `VERIFY_RECORD_ANONYMIZED` → `ANONYMIZED` | `evidence_92` |

Evidence locations (a literal resource match establishes occurrence, not automatically ownership or policy applicability):

| Resource | Admissible evidence occurrence | Other references |
|---|---|---|
| `account_6440` | [evidence_92:46](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/evidence/records/service_resource_export_20260915_114455.json:46) | [activity_3661](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/system_activity.csv:3662) |
| `analytics_5335` | [evidence_92:105](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/evidence/records/service_resource_export_20260915_114455.json:105) | [activity_3665](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/system_activity.csv:3666) ; [evidence_02 AFTER CUTOFF](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/evidence/records/customer_data_snapshot_bundle_20260917.json:59) |
| `audit_record_3737` | [evidence_92:288](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/evidence/records/service_resource_export_20260915_114455.json:288) | [evidence_02 AFTER CUTOFF](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/evidence/records/customer_data_snapshot_bundle_20260917.json:398) |

Cited manifest timing: `evidence_92` captured `2026-09-15T11:44:55Z`.

## case_22 — expected INCOMPLETE

- Request: [sample_deletion_requests.csv](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/sample_deletion_requests.csv:23). Expected answer: [sample_output.csv](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/sample_output.csv:23).
- Intent: Erase account; English. Identity: `user_51`; request email is current; 0 history rows.
- Cutoff: `2026-09-21T10:00:00Z`; reported claim: `COMPLETE`.
- Branch exercised: SQL search and analytics violations. Policy: SEARCH_INDEX_ENTRY DELETE; ANALYTICS_PROFILE ANONYMIZE; SECURITY_AUDIT_LOG retain.
- Observations: evidence_05 links search_8911 and analytics_4440 exposed in both primary and read replica, and audit_record_3482 present.
- Limitations / decisions: account_4990 is activity-only; empty profile coverage can support absence in those tables, but does not supply its subject-to-resource mapping.
- Expected phase counts: FINDING=2, REMEDIATION=2, VERIFICATION=4. Cited formats: .sql.

| # | Phase | System / resource | Operation → state | Evidence ID |
|---|---|---|---|---|
| 1 | FINDING | `search_service` / `search_8911` | `REPORT_REMAINING_RECORD` → `PRESENT` | `evidence_05` |
| 2 | FINDING | `analytics_platform` / `analytics_4440` | `REPORT_EXPOSED_PII` → `PRESENT` | `evidence_05` |
| 3 | REMEDIATION | `search_service` / `search_8911` | `DELETE_RECORD` → `ABSENT` | empty (future work) |
| 4 | REMEDIATION | `analytics_platform` / `analytics_4440` | `ANONYMIZE_RECORD` → `ANONYMIZED` | empty (future work) |
| 5 | VERIFICATION | `account_service` / `account_4990` | `VERIFY_RECORD_ABSENT` → `ABSENT` | empty (future work) |
| 6 | VERIFICATION | `search_service` / `search_8911` | `VERIFY_RECORD_ABSENT` → `ABSENT` | empty (future work) |
| 7 | VERIFICATION | `security_service` / `audit_record_3482` | `VERIFY_RECORD_PRESENT` → `PRESENT` | empty (future work) |
| 8 | VERIFICATION | `analytics_platform` / `analytics_4440` | `VERIFY_RECORD_ANONYMIZED` → `ANONYMIZED` | empty (future work) |

Evidence locations (a literal resource match establishes occurrence, not automatically ownership or policy applicability):

| Resource | Admissible evidence occurrence | Other references |
|---|---|---|
| `account_4990` | No literal match; inspect absence/snapshot qualification above | [activity_3573](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/system_activity.csv:3574) |
| `analytics_4440` | [evidence_05:17](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/evidence/databases/customer_data_read_replica_20260921.sql:17) | [activity_3578](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/system_activity.csv:3579) |
| `audit_record_3482` | [evidence_05:21](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/evidence/databases/customer_data_read_replica_20260921.sql:21) | No other match found in searched sources |
| `search_8911` | [evidence_05:41](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/evidence/databases/customer_data_read_replica_20260921.sql:41) | [activity_3581](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/system_activity.csv:3582) |

Cited manifest timing: `evidence_05` captured `2026-09-21T10:00:00Z`.

## case_23 — expected INCOMPLETE

- Request: [sample_deletion_requests.csv](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/sample_deletion_requests.csv:24). Expected answer: [sample_output.csv](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/sample_output.csv:24).
- Intent: Delete export and search; keep required security records; English. Identity: `user_23`; request email is current; 0 history rows.
- Cutoff: `2026-09-15T12:00:00Z`; reported claim: `NOT_STARTED`.
- Branch exercised: Two remaining copies. Policy: USER_EXPORT DELETE; SEARCH_INDEX_ENTRY DELETE; SECURITY_AUDIT_LOG retain.
- Observations: evidence_92 links export_7364 and search_898 to the request email.
- Limitations / decisions: account_410 is activity-only and audit_record_4128 appears only in later evidence_02. Future verification IDs are not all independently discoverable before cutoff.
- Expected phase counts: FINDING=2, REMEDIATION=2, VERIFICATION=4. Cited formats: .json.

| # | Phase | System / resource | Operation → state | Evidence ID |
|---|---|---|---|---|
| 1 | FINDING | `export_service` / `export_7364` | `REPORT_REMAINING_RECORD` → `PRESENT` | `evidence_92` |
| 2 | FINDING | `search_service` / `search_898` | `REPORT_REMAINING_RECORD` → `PRESENT` | `evidence_92` |
| 3 | REMEDIATION | `export_service` / `export_7364` | `DELETE_RECORD` → `ABSENT` | empty (future work) |
| 4 | REMEDIATION | `search_service` / `search_898` | `DELETE_RECORD` → `ABSENT` | empty (future work) |
| 5 | VERIFICATION | `account_service` / `account_410` | `VERIFY_RECORD_ABSENT` → `ABSENT` | empty (future work) |
| 6 | VERIFICATION | `export_service` / `export_7364` | `VERIFY_RECORD_ABSENT` → `ABSENT` | empty (future work) |
| 7 | VERIFICATION | `search_service` / `search_898` | `VERIFY_RECORD_ABSENT` → `ABSENT` | empty (future work) |
| 8 | VERIFICATION | `security_service` / `audit_record_4128` | `VERIFY_RECORD_PRESENT` → `PRESENT` | empty (future work) |

Evidence locations (a literal resource match establishes occurrence, not automatically ownership or policy applicability):

| Resource | Admissible evidence occurrence | Other references |
|---|---|---|
| `account_410` | No literal match; inspect absence/snapshot qualification above | [activity_3662](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/system_activity.csv:3663) |
| `audit_record_4128` | No literal match; inspect absence/snapshot qualification above | [evidence_02 AFTER CUTOFF](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/evidence/records/customer_data_snapshot_bundle_20260917.json:412) |
| `export_7364` | [evidence_92:150](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/evidence/records/service_resource_export_20260915_114455.json:150) | [activity_3667](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/system_activity.csv:3668) ; [evidence_02 AFTER CUTOFF](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/evidence/records/customer_data_snapshot_bundle_20260917.json:279) |
| `search_898` | [evidence_92:254](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/evidence/records/service_resource_export_20260915_114455.json:254) | [activity_3671](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/system_activity.csv:3672) ; [evidence_02 AFTER CUTOFF](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/evidence/records/customer_data_snapshot_bundle_20260917.json:355) |

Cited manifest timing: `evidence_92` captured `2026-09-15T11:44:55Z`.

## case_24 — expected INCOMPLETE

- Request: [sample_deletion_requests.csv](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/sample_deletion_requests.csv:25). Expected answer: [sample_output.csv](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/sample_output.csv:25).
- Intent: Finish deletion despite COMPLETE claim; English. Identity: `user_24`; request email is current; 0 history rows.
- Cutoff: `2026-09-15T12:00:00Z`; reported claim: `COMPLETE`.
- Branch exercised: Profile and search survive successful worker claims. Policy: USER_PROFILE DELETE; SEARCH_INDEX_ENTRY DELETE; SECURITY_AUDIT_LOG retain.
- Observations: evidence_92 links account_5334 status200 and search_5577 hit to the subject, despite worker SUCCESS for delete/sync.
- Limitations / decisions: audit_record_7095 is in later evidence_02 only. evidence_27 has a retained-order candidate. Canonical account-before-search order is not proof of a dependency edge.
- Expected phase counts: FINDING=2, REMEDIATION=2, VERIFICATION=3. Cited formats: .json.

| # | Phase | System / resource | Operation → state | Evidence ID |
|---|---|---|---|---|
| 1 | FINDING | `account_service` / `account_5334` | `REPORT_REMAINING_RECORD` → `PRESENT` | `evidence_92` |
| 2 | FINDING | `search_service` / `search_5577` | `REPORT_REMAINING_RECORD` → `PRESENT` | `evidence_92` |
| 3 | REMEDIATION | `account_service` / `account_5334` | `DELETE_RECORD` → `ABSENT` | empty (future work) |
| 4 | REMEDIATION | `search_service` / `search_5577` | `DELETE_RECORD` → `ABSENT` | empty (future work) |
| 5 | VERIFICATION | `account_service` / `account_5334` | `VERIFY_RECORD_ABSENT` → `ABSENT` | empty (future work) |
| 6 | VERIFICATION | `search_service` / `search_5577` | `VERIFY_RECORD_ABSENT` → `ABSENT` | empty (future work) |
| 7 | VERIFICATION | `security_service` / `audit_record_7095` | `VERIFY_RECORD_PRESENT` → `PRESENT` | empty (future work) |

Evidence locations (a literal resource match establishes occurrence, not automatically ownership or policy applicability):

| Resource | Admissible evidence occurrence | Other references |
|---|---|---|
| `account_5334` | [evidence_92:28](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/evidence/records/service_resource_export_20260915_114455.json:28) | [activity_3599](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/system_activity.csv:3600); [activity_3608](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/system_activity.csv:3609) ; [evidence_02 AFTER CUTOFF](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/evidence/records/customer_data_snapshot_bundle_20260917.json:43) |
| `audit_record_7095` | No literal match; inspect absence/snapshot qualification above | [evidence_02 AFTER CUTOFF](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/evidence/records/customer_data_snapshot_bundle_20260917.json:419) |
| `search_5577` | [evidence_92:236](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/evidence/records/service_resource_export_20260915_114455.json:236) | [activity_3610](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/system_activity.csv:3611) ; [evidence_02 AFTER CUTOFF](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/evidence/records/customer_data_snapshot_bundle_20260917.json:364) |

Cited manifest timing: `evidence_92` captured `2026-09-15T11:44:55Z`.

## case_25 — expected COMPLETE

- Request: [sample_deletion_requests.csv](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/sample_deletion_requests.csv:26). Expected answer: [sample_output.csv](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/sample_output.csv:26).
- Intent: Audit reported failed deletion; English. Identity: `user_25`; request email is current; 1 history rows (phone).
- Cutoff: `2026-09-15T12:00:00Z`; reported claim: `NOT_STARTED`.
- Branch exercised: NOT_STARTED claim versus compliant readbacks. Policy: USER_PROFILE absent; ANALYTICS_PROFILE anonymized; SECURITY_AUDIT_LOG retained.
- Observations: evidence_92 shows account_3136 404, analytics_1895 null identifiers, audit_record_451 linked to user_25 with retention through 2031.
- Limitations / decisions: Account/analytics attribution is ungrounded before cutoff; known states alone do not establish case membership. Phone history is present but not decisive.
- Expected phase counts: FINDING=0, REMEDIATION=0, VERIFICATION=3. Cited formats: .json.

| # | Phase | System / resource | Operation → state | Evidence ID |
|---|---|---|---|---|
| 1 | VERIFICATION | `account_service` / `account_3136` | `VERIFY_RECORD_ABSENT` → `ABSENT` | `evidence_92` |
| 2 | VERIFICATION | `security_service` / `audit_record_451` | `VERIFY_RECORD_PRESENT` → `PRESENT` | `evidence_92` |
| 3 | VERIFICATION | `analytics_platform` / `analytics_1895` | `VERIFY_RECORD_ANONYMIZED` → `ANONYMIZED` | `evidence_92` |

Evidence locations (a literal resource match establishes occurrence, not automatically ownership or policy applicability):

| Resource | Admissible evidence occurrence | Other references |
|---|---|---|
| `account_3136` | [evidence_92:10](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/evidence/records/service_resource_export_20260915_114455.json:10) | [activity_3597](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/system_activity.csv:3598) |
| `analytics_1895` | [evidence_92:60](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/evidence/records/service_resource_export_20260915_114455.json:60) | [activity_3602](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/system_activity.csv:3603) ; [evidence_02 AFTER CUTOFF](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/evidence/records/customer_data_snapshot_bundle_20260917.json:83) |
| `audit_record_451` | [evidence_92:302](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/evidence/records/service_resource_export_20260915_114455.json:302) | [evidence_02 AFTER CUTOFF](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/evidence/records/customer_data_snapshot_bundle_20260917.json:426) |

Cited manifest timing: `evidence_92` captured `2026-09-15T11:44:55Z`.

## case_26 — expected COMPLETE

- Request: [sample_deletion_requests.csv](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/sample_deletion_requests.csv:27). Expected answer: [sample_output.csv](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/sample_output.csv:27).
- Intent: Audit old report against latest state; English. Identity: `user_26`; request email is current; 0 history rows.
- Cutoff: `2026-09-15T12:00:00Z`; reported claim: `NOT_STARTED`.
- Branch exercised: Six compliant resource states and stale/future evidence separation. Policy: All six verification operations.
- Observations: evidence_92 proves linked security/support/flow/backup compliant states; account_5684 404 and analytics_4566 null identifiers lack admissible subject links. evidence_02 embeds a Sep9 account-present snapshot but was exported Sep17.
- Limitations / decisions: The older embedded observation must not override a later readback, and the late-export evidence must not supply missing links under the strict availability rule.
- Expected phase counts: FINDING=0, REMEDIATION=0, VERIFICATION=6. Cited formats: .json.

| # | Phase | System / resource | Operation → state | Evidence ID |
|---|---|---|---|---|
| 1 | VERIFICATION | `account_service` / `account_5684` | `VERIFY_RECORD_ABSENT` → `ABSENT` | `evidence_92` |
| 2 | VERIFICATION | `security_service` / `audit_record_5416` | `VERIFY_RECORD_PRESENT` → `PRESENT` | `evidence_92` |
| 3 | VERIFICATION | `support_platform` / `support_4715` | `VERIFY_RECORD_REDACTED` → `REDACTED` | `evidence_92` |
| 4 | VERIFICATION | `analytics_platform` / `analytics_4566` | `VERIFY_RECORD_ANONYMIZED` → `ANONYMIZED` | `evidence_92` |
| 5 | VERIFICATION | `integration_service` / `data_flow_6244` | `VERIFY_DATA_FLOW_DISABLED` → `DISABLED` | `evidence_92` |
| 6 | VERIFICATION | `backup_service` / `backup_3120` | `VERIFY_RESTORE_BLOCKED` → `BLOCKED` | `evidence_92` |

Evidence locations (a literal resource match establishes occurrence, not automatically ownership or policy applicability):

| Resource | Admissible evidence occurrence | Other references |
|---|---|---|
| `account_5684` | [evidence_92:40](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/evidence/records/service_resource_export_20260915_114455.json:40) | [activity_3600](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/system_activity.csv:3601) ; [evidence_02 AFTER CUTOFF](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/evidence/records/customer_data_snapshot_bundle_20260917.json:11) |
| `analytics_4566` | [evidence_92:78](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/evidence/records/service_resource_export_20260915_114455.json:78) | [activity_3603](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/system_activity.csv:3604) ; [evidence_02 AFTER CUTOFF](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/evidence/records/customer_data_snapshot_bundle_20260917.json:107) |
| `audit_record_5416` | [evidence_92:309](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/evidence/records/service_resource_export_20260915_114455.json:309) | [evidence_02 AFTER CUTOFF](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/evidence/records/customer_data_snapshot_bundle_20260917.json:433) |
| `backup_3120` | [evidence_92:121](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/evidence/records/service_resource_export_20260915_114455.json:121) | [activity_3607](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/system_activity.csv:3608) ; [evidence_02 AFTER CUTOFF](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/evidence/records/customer_data_snapshot_bundle_20260917.json:251) |
| `data_flow_6244` | [evidence_92:194](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/evidence/records/service_resource_export_20260915_114455.json:194) | [activity_3606](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/system_activity.csv:3607) ; [evidence_02 AFTER CUTOFF](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/evidence/records/customer_data_snapshot_bundle_20260917.json:299) |
| `support_4715` | [evidence_92:349](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/evidence/records/service_resource_export_20260915_114455.json:349) | [activity_3605](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/system_activity.csv:3606) ; [evidence_02 AFTER CUTOFF](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/evidence/records/customer_data_snapshot_bundle_20260917.json:482) |

Cited manifest timing: `evidence_92` captured `2026-09-15T11:44:55Z`.

## case_27 — expected COMPLETE

- Request: [sample_deletion_requests.csv](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/sample_deletion_requests.csv:28). Expected answer: [sample_output.csv](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/sample_output.csv:28).
- Intent: Audit deletion at review time; English. Identity: `user_27`; request email is current; 0 history rows.
- Cutoff: `2026-09-15T12:00:00Z`; reported claim: `COMPLETE`.
- Branch exercised: Future resurrection must not change historical verdict. Policy: All six verification operations.
- Observations: evidence_92 contains six compliant states; security/support/flow/backup are subject-linked, account_3866 and analytics_4574 are not. evidence_02 has a Sep17 account-present snapshot after the Sep15 cutoff.
- Limitations / decisions: Ignore future recreation when answering the earlier cutoff. Do not use the later profile as an identity bridge for earlier unlinked resources.
- Expected phase counts: FINDING=0, REMEDIATION=0, VERIFICATION=6. Cited formats: .json.

| # | Phase | System / resource | Operation → state | Evidence ID |
|---|---|---|---|---|
| 1 | VERIFICATION | `account_service` / `account_3866` | `VERIFY_RECORD_ABSENT` → `ABSENT` | `evidence_92` |
| 2 | VERIFICATION | `security_service` / `audit_record_3830` | `VERIFY_RECORD_PRESENT` → `PRESENT` | `evidence_92` |
| 3 | VERIFICATION | `support_platform` / `support_4707` | `VERIFY_RECORD_REDACTED` → `REDACTED` | `evidence_92` |
| 4 | VERIFICATION | `analytics_platform` / `analytics_4574` | `VERIFY_RECORD_ANONYMIZED` → `ANONYMIZED` | `evidence_92` |
| 5 | VERIFICATION | `integration_service` / `data_flow_2295` | `VERIFY_DATA_FLOW_DISABLED` → `DISABLED` | `evidence_92` |
| 6 | VERIFICATION | `backup_service` / `backup_5970` | `VERIFY_RESTORE_BLOCKED` → `BLOCKED` | `evidence_92` |

Evidence locations (a literal resource match establishes occurrence, not automatically ownership or policy applicability):

| Resource | Admissible evidence occurrence | Other references |
|---|---|---|
| `account_3866` | [evidence_92:16](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/evidence/records/service_resource_export_20260915_114455.json:16) | [activity_3530](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/system_activity.csv:3531) ; [evidence_02 AFTER CUTOFF](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/evidence/records/customer_data_snapshot_bundle_20260917.json:524) |
| `analytics_4574` | [evidence_92:87](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/evidence/records/service_resource_export_20260915_114455.json:87) | [activity_3533](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/system_activity.csv:3534) ; [evidence_02 AFTER CUTOFF](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/evidence/records/customer_data_snapshot_bundle_20260917.json:132) |
| `audit_record_3830` | [evidence_92:295](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/evidence/records/service_resource_export_20260915_114455.json:295) | [evidence_02 AFTER CUTOFF](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/evidence/records/customer_data_snapshot_bundle_20260917.json:440) |
| `backup_5970` | [evidence_92:129](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/evidence/records/service_resource_export_20260915_114455.json:129) | [activity_3540](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/system_activity.csv:3541) ; [evidence_02 AFTER CUTOFF](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/evidence/records/customer_data_snapshot_bundle_20260917.json:258) |
| `data_flow_2295` | [evidence_92:167](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/evidence/records/service_resource_export_20260915_114455.json:167) | [activity_3537](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/system_activity.csv:3538) ; [evidence_02 AFTER CUTOFF](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/evidence/records/customer_data_snapshot_bundle_20260917.json:307) |
| `support_4707` | [evidence_92:340](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/evidence/records/service_resource_export_20260915_114455.json:340) | [activity_3536](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/system_activity.csv:3537) ; [evidence_02 AFTER CUTOFF](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/evidence/records/customer_data_snapshot_bundle_20260917.json:489) |

Cited manifest timing: `evidence_92` captured `2026-09-15T11:44:55Z`.

## case_28 — expected COMPLETE

- Request: [sample_deletion_requests.csv](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/sample_deletion_requests.csv:29). Expected answer: [sample_output.csv](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/sample_output.csv:29).
- Intent: Audit deletion; similar-email record belongs to another person; English. Identity: `user_28`; request email is current; 0 history rows.
- Cutoff: `2026-09-15T12:00:00Z`; reported claim: `NOT_STARTED`.
- Branch exercised: Decoy discrimination and six compliant states. Policy: All six verification operations.
- Observations: evidence_92 contains six compliant states. security/support/flow/backup link to user_28; account_5482 and analytics_6077 lack admissible subject attribution. The similar-email search decoy is in later evidence_02, so strict manifest filtering already excludes it.
- Limitations / decisions: The intended decoy branch is present in request/data, but is not a strong admissible-same-time decoy test. Need a custom case with both identities observable before cutoff.
- Expected phase counts: FINDING=0, REMEDIATION=0, VERIFICATION=6. Cited formats: .json.

| # | Phase | System / resource | Operation → state | Evidence ID |
|---|---|---|---|---|
| 1 | VERIFICATION | `account_service` / `account_5482` | `VERIFY_RECORD_ABSENT` → `ABSENT` | `evidence_92` |
| 2 | VERIFICATION | `security_service` / `audit_record_9265` | `VERIFY_RECORD_PRESENT` → `PRESENT` | `evidence_92` |
| 3 | VERIFICATION | `support_platform` / `support_2351` | `VERIFY_RECORD_REDACTED` → `REDACTED` | `evidence_92` |
| 4 | VERIFICATION | `analytics_platform` / `analytics_6077` | `VERIFY_RECORD_ANONYMIZED` → `ANONYMIZED` | `evidence_92` |
| 5 | VERIFICATION | `integration_service` / `data_flow_2337` | `VERIFY_DATA_FLOW_DISABLED` → `DISABLED` | `evidence_92` |
| 6 | VERIFICATION | `backup_service` / `backup_838` | `VERIFY_RESTORE_BLOCKED` → `BLOCKED` | `evidence_92` |

Evidence locations (a literal resource match establishes occurrence, not automatically ownership or policy applicability):

| Resource | Admissible evidence occurrence | Other references |
|---|---|---|
| `account_5482` | [evidence_92:34](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/evidence/records/service_resource_export_20260915_114455.json:34) | [activity_3529](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/system_activity.csv:3530) |
| `analytics_6077` | [evidence_92:114](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/evidence/records/service_resource_export_20260915_114455.json:114) | [activity_3534](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/system_activity.csv:3535) ; [evidence_02 AFTER CUTOFF](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/evidence/records/customer_data_snapshot_bundle_20260917.json:161) |
| `audit_record_9265` | [evidence_92:316](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/evidence/records/service_resource_export_20260915_114455.json:316) | [evidence_02 AFTER CUTOFF](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/evidence/records/customer_data_snapshot_bundle_20260917.json:447) |
| `backup_838` | [evidence_92:137](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/evidence/records/service_resource_export_20260915_114455.json:137) | [activity_3539](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/system_activity.csv:3540) ; [evidence_02 AFTER CUTOFF](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/evidence/records/customer_data_snapshot_bundle_20260917.json:265) |
| `data_flow_2337` | [evidence_92:176](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/evidence/records/service_resource_export_20260915_114455.json:176) | [activity_3538](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/system_activity.csv:3539) ; [evidence_02 AFTER CUTOFF](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/evidence/records/customer_data_snapshot_bundle_20260917.json:315) |
| `support_2351` | [evidence_92:331](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/evidence/records/service_resource_export_20260915_114455.json:331) | [activity_3535](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/system_activity.csv:3536) ; [evidence_02 AFTER CUTOFF](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/evidence/records/customer_data_snapshot_bundle_20260917.json:496) |

Cited manifest timing: `evidence_92` captured `2026-09-15T11:44:55Z`.

## case_29 — expected INCOMPLETE

- Request: [sample_deletion_requests.csv](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/sample_deletion_requests.csv:30). Expected answer: [sample_output.csv](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/sample_output.csv:30).
- Intent: Delete old/current addresses and disable integrations; English. Identity: `user_29`; request email is historical; 2 history rows (email, email_hash).
- Cutoff: `2026-09-15T12:00:00Z`; reported claim: `NOT_STARTED`.
- Branch exercised: Historical request email and four violations. Policy: DELETE search; REDACT support; ANONYMIZE analytics; DISABLE flow.
- Observations: The request email is historical; history maps it to the current email used by evidence_92. search_1993, analytics_5208, support_5281 and data_flow_3827 are directly linked current violations.
- Limitations / decisions: account_7012 is activity-only; audit_record_3954 is in later evidence_02. evidence_27 retained-order candidate is outside expected steps.
- Expected phase counts: FINDING=4, REMEDIATION=4, VERIFICATION=6. Cited formats: .json.

| # | Phase | System / resource | Operation → state | Evidence ID |
|---|---|---|---|---|
| 1 | FINDING | `search_service` / `search_1993` | `REPORT_REMAINING_RECORD` → `PRESENT` | `evidence_92` |
| 2 | FINDING | `analytics_platform` / `analytics_5208` | `REPORT_EXPOSED_PII` → `PRESENT` | `evidence_92` |
| 3 | FINDING | `support_platform` / `support_5281` | `REPORT_EXPOSED_PII` → `PRESENT` | `evidence_92` |
| 4 | FINDING | `integration_service` / `data_flow_3827` | `REPORT_ACTIVE_DATA_FLOW` → `ACTIVE` | `evidence_92` |
| 5 | REMEDIATION | `integration_service` / `data_flow_3827` | `DISABLE_DATA_FLOW` → `DISABLED` | empty (future work) |
| 6 | REMEDIATION | `search_service` / `search_1993` | `DELETE_RECORD` → `ABSENT` | empty (future work) |
| 7 | REMEDIATION | `support_platform` / `support_5281` | `REDACT_RECORD` → `REDACTED` | empty (future work) |
| 8 | REMEDIATION | `analytics_platform` / `analytics_5208` | `ANONYMIZE_RECORD` → `ANONYMIZED` | empty (future work) |
| 9 | VERIFICATION | `account_service` / `account_7012` | `VERIFY_RECORD_ABSENT` → `ABSENT` | empty (future work) |
| 10 | VERIFICATION | `search_service` / `search_1993` | `VERIFY_RECORD_ABSENT` → `ABSENT` | empty (future work) |
| 11 | VERIFICATION | `security_service` / `audit_record_3954` | `VERIFY_RECORD_PRESENT` → `PRESENT` | empty (future work) |
| 12 | VERIFICATION | `support_platform` / `support_5281` | `VERIFY_RECORD_REDACTED` → `REDACTED` | empty (future work) |
| 13 | VERIFICATION | `analytics_platform` / `analytics_5208` | `VERIFY_RECORD_ANONYMIZED` → `ANONYMIZED` | empty (future work) |
| 14 | VERIFICATION | `integration_service` / `data_flow_3827` | `VERIFY_DATA_FLOW_DISABLED` → `DISABLED` | empty (future work) |

Evidence locations (a literal resource match establishes occurrence, not automatically ownership or policy applicability):

| Resource | Admissible evidence occurrence | Other references |
|---|---|---|
| `account_7012` | No literal match; inspect absence/snapshot qualification above | [activity_3532](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/system_activity.csv:3533) |
| `analytics_5208` | [evidence_92:96](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/evidence/records/service_resource_export_20260915_114455.json:96) | [activity_3544](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/system_activity.csv:3545) ; [evidence_02 AFTER CUTOFF](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/evidence/records/customer_data_snapshot_bundle_20260917.json:190) |
| `audit_record_3954` | No literal match; inspect absence/snapshot qualification above | [evidence_02 AFTER CUTOFF](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/evidence/records/customer_data_snapshot_bundle_20260917.json:454) |
| `data_flow_3827` | [evidence_92:185](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/evidence/records/service_resource_export_20260915_114455.json:185) | [activity_3541](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/system_activity.csv:3542) ; [evidence_02 AFTER CUTOFF](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/evidence/records/customer_data_snapshot_bundle_20260917.json:323) |
| `search_1993` | [evidence_92:218](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/evidence/records/service_resource_export_20260915_114455.json:218) | [activity_3542](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/system_activity.csv:3543) ; [evidence_02 AFTER CUTOFF](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/evidence/records/customer_data_snapshot_bundle_20260917.json:373) |
| `support_5281` | [evidence_92:358](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/evidence/records/service_resource_export_20260915_114455.json:358) | [activity_3543](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/system_activity.csv:3544) ; [evidence_02 AFTER CUTOFF](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/evidence/records/customer_data_snapshot_bundle_20260917.json:503) |

Cited manifest timing: `evidence_92` captured `2026-09-15T11:44:55Z`.

## case_30 — expected INCOMPLETE

- Request: [sample_deletion_requests.csv](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/sample_deletion_requests.csv:31). Expected answer: [sample_output.csv](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/sample_output.csv:31).
- Intent: Finish deletion across search/support/analytics; English. Identity: `user_30`; request email is historical; 2 history rows (email, email_hash).
- Cutoff: `2026-09-15T12:00:00Z`; reported claim: `COMPLETE`.
- Branch exercised: Historical request email and mixed remediation. Policy: DELETE search; REDACT support; ANONYMIZE analytics; DISABLE flow.
- Observations: Historical email/hash transition maps the request to current email. evidence_92 links search_9359, analytics_3697, support_6477 and data_flow_8524 to that current email.
- Limitations / decisions: account_4163 is activity-only; audit_record_1707 is in later evidence_02. Resource order and bounded citation semantics match case29.
- Expected phase counts: FINDING=4, REMEDIATION=4, VERIFICATION=6. Cited formats: .json.

| # | Phase | System / resource | Operation → state | Evidence ID |
|---|---|---|---|---|
| 1 | FINDING | `search_service` / `search_9359` | `REPORT_REMAINING_RECORD` → `PRESENT` | `evidence_92` |
| 2 | FINDING | `analytics_platform` / `analytics_3697` | `REPORT_EXPOSED_PII` → `PRESENT` | `evidence_92` |
| 3 | FINDING | `support_platform` / `support_6477` | `REPORT_EXPOSED_PII` → `PRESENT` | `evidence_92` |
| 4 | FINDING | `integration_service` / `data_flow_8524` | `REPORT_ACTIVE_DATA_FLOW` → `ACTIVE` | `evidence_92` |
| 5 | REMEDIATION | `integration_service` / `data_flow_8524` | `DISABLE_DATA_FLOW` → `DISABLED` | empty (future work) |
| 6 | REMEDIATION | `search_service` / `search_9359` | `DELETE_RECORD` → `ABSENT` | empty (future work) |
| 7 | REMEDIATION | `support_platform` / `support_6477` | `REDACT_RECORD` → `REDACTED` | empty (future work) |
| 8 | REMEDIATION | `analytics_platform` / `analytics_3697` | `ANONYMIZE_RECORD` → `ANONYMIZED` | empty (future work) |
| 9 | VERIFICATION | `account_service` / `account_4163` | `VERIFY_RECORD_ABSENT` → `ABSENT` | empty (future work) |
| 10 | VERIFICATION | `search_service` / `search_9359` | `VERIFY_RECORD_ABSENT` → `ABSENT` | empty (future work) |
| 11 | VERIFICATION | `security_service` / `audit_record_1707` | `VERIFY_RECORD_PRESENT` → `PRESENT` | empty (future work) |
| 12 | VERIFICATION | `support_platform` / `support_6477` | `VERIFY_RECORD_REDACTED` → `REDACTED` | empty (future work) |
| 13 | VERIFICATION | `analytics_platform` / `analytics_3697` | `VERIFY_RECORD_ANONYMIZED` → `ANONYMIZED` | empty (future work) |
| 14 | VERIFICATION | `integration_service` / `data_flow_8524` | `VERIFY_DATA_FLOW_DISABLED` → `DISABLED` | empty (future work) |

Evidence locations (a literal resource match establishes occurrence, not automatically ownership or policy applicability):

| Resource | Admissible evidence occurrence | Other references |
|---|---|---|
| `account_4163` | No literal match; inspect absence/snapshot qualification above | [activity_3465](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/system_activity.csv:3466) |
| `analytics_3697` | [evidence_92:69](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/evidence/records/service_resource_export_20260915_114455.json:69) | [activity_3470](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/system_activity.csv:3471) ; [evidence_02 AFTER CUTOFF](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/evidence/records/customer_data_snapshot_bundle_20260917.json:215) |
| `audit_record_1707` | No literal match; inspect absence/snapshot qualification above | [evidence_02 AFTER CUTOFF](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/evidence/records/customer_data_snapshot_bundle_20260917.json:461) |
| `data_flow_8524` | [evidence_92:203](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/evidence/records/service_resource_export_20260915_114455.json:203) | [activity_3467](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/system_activity.csv:3468) ; [evidence_02 AFTER CUTOFF](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/evidence/records/customer_data_snapshot_bundle_20260917.json:331) |
| `search_9359` | [evidence_92:272](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/evidence/records/service_resource_export_20260915_114455.json:272) | [activity_3468](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/system_activity.csv:3469) ; [evidence_02 AFTER CUTOFF](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/evidence/records/customer_data_snapshot_bundle_20260917.json:382) |
| `support_6477` | [evidence_92:367](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/evidence/records/service_resource_export_20260915_114455.json:367) | [activity_3469](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/system_activity.csv:3470) ; [evidence_02 AFTER CUTOFF](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/evidence/records/customer_data_snapshot_bundle_20260917.json:510) |

Cited manifest timing: `evidence_92` captured `2026-09-15T11:44:55Z`.

## case_31 — expected COMPLETE

- Request: [sample_deletion_requests.csv](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/sample_deletion_requests.csv:32). Expected answer: [sample_output.csv](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/sample_output.csv:32).
- Intent: Remove direct identifiers; preserve required internal reference; English. Identity: `user_541`; request email is current; 0 history rows.
- Cutoff: `2026-09-15T12:00:00Z`; reported claim: `COMPLETE`.
- Branch exercised: Compliant account tombstone. Policy: ACCOUNT_TOMBSTONE REDACT; SECURITY_AUDIT_LOG RETAIN; USER_PROFILE absent.
- Observations: evidence_51 at cutoff contains tombstone_440 linked to user_541 with name/email/phone/hash null, audit_record_6909 present, and an empty customer_profiles collection.
- Limitations / decisions: Correctly preserve stable reference. account_4857 is an unlinked worker-claim ID; snapshot scope/completeness and retention condition are not explicit.
- Expected phase counts: FINDING=0, REMEDIATION=0, VERIFICATION=3. Cited formats: .json.

| # | Phase | System / resource | Operation → state | Evidence ID |
|---|---|---|---|---|
| 1 | VERIFICATION | `account_service` / `account_4857` | `VERIFY_RECORD_ABSENT` → `ABSENT` | `evidence_51` |
| 2 | VERIFICATION | `security_service` / `audit_record_6909` | `VERIFY_RECORD_PRESENT` → `PRESENT` | `evidence_51` |
| 3 | VERIFICATION | `identity_service` / `tombstone_440` | `VERIFY_RECORD_REDACTED` → `REDACTED` | `evidence_51` |

Evidence locations (a literal resource match establishes occurrence, not automatically ownership or policy applicability):

| Resource | Admissible evidence occurrence | Other references |
|---|---|---|
| `account_4857` | No literal match; inspect absence/snapshot qualification above | [activity_3682](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/system_activity.csv:3683) |
| `audit_record_6909` | [evidence_51:42](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/evidence/records/customer_data_snapshot_bundle_20260915.json:42) | No other match found in searched sources |
| `tombstone_440` | [evidence_51:17](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/evidence/records/customer_data_snapshot_bundle_20260915.json:17) | [activity_3687](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/system_activity.csv:3688) |

Cited manifest timing: `evidence_51` captured `2026-09-15T12:00:00Z`.

## case_32 — expected INCOMPLETE

- Request: [sample_deletion_requests.csv](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/sample_deletion_requests.csv:33). Expected answer: [sample_output.csv](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/sample_output.csv:33).
- Intent: Clean exposed deleted-account reference; English. Identity: `user_542`; request email is current; 0 history rows.
- Cutoff: `2026-09-15T12:00:00Z`; reported claim: `PARTIALLY_COMPLETE`.
- Branch exercised: Noncompliant tombstone despite DELETED status. Policy: ACCOUNT_TOMBSTONE REDACT, not DELETE; SECURITY_AUDIT_LOG retain.
- Observations: evidence_51 tombstone_9178 links user_542 and exposes all four prohibited identifier fields; security record remains present; profiles collection is empty.
- Limitations / decisions: INCOMPLETE is grounded. account_8858 is an unlinked worker-claim ID; future absent check is expected but its mapping is not independently established.
- Expected phase counts: FINDING=1, REMEDIATION=1, VERIFICATION=3. Cited formats: .json.

| # | Phase | System / resource | Operation → state | Evidence ID |
|---|---|---|---|---|
| 1 | FINDING | `identity_service` / `tombstone_9178` | `REPORT_EXPOSED_PII` → `PRESENT` | `evidence_51` |
| 2 | REMEDIATION | `identity_service` / `tombstone_9178` | `REDACT_RECORD` → `REDACTED` | empty (future work) |
| 3 | VERIFICATION | `account_service` / `account_8858` | `VERIFY_RECORD_ABSENT` → `ABSENT` | empty (future work) |
| 4 | VERIFICATION | `security_service` / `audit_record_7068` | `VERIFY_RECORD_PRESENT` → `PRESENT` | empty (future work) |
| 5 | VERIFICATION | `identity_service` / `tombstone_9178` | `VERIFY_RECORD_REDACTED` → `REDACTED` | empty (future work) |

Evidence locations (a literal resource match establishes occurrence, not automatically ownership or policy applicability):

| Resource | Admissible evidence occurrence | Other references |
|---|---|---|
| `account_8858` | No literal match; inspect absence/snapshot qualification above | [activity_3685](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/system_activity.csv:3686) |
| `audit_record_7068` | [evidence_51:49](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/evidence/records/customer_data_snapshot_bundle_20260915.json:49) | No other match found in searched sources |
| `tombstone_9178` | [evidence_51:26](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/evidence/records/customer_data_snapshot_bundle_20260915.json:26) | [activity_3692](/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26/dataset/system_activity.csv:3693) |

Cited manifest timing: `evidence_51` captured `2026-09-15T12:00:00Z`.

