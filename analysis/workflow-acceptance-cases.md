# Workflow acceptance cases

Status: designed fixtures, not implemented tests or measured results. All subjects and resources below are fictional. This catalog complements the [workflow specification](workflow-design.md) and the [public-sample audit](public-samples/report.md).

The test harness must declare each fixture's complete source inventory, policy subset, observations, manifest capture times, and subject links. A declared complete inventory is a test precondition, not permission for the real solver to assume every input snapshot is complete. Never add fixtures to generated `dataset/` files. Implement them separately and document at least three directly in the eventual evaluation report.

## A01 — Explicit non-deletion request

- Request: `Please send me a copy of my records. Do not delete my account.`
- Audit cutoff: `2026-06-10T12:00:00Z`.
- Misleading metadata: reported status `COMPLETE`.
- Expected output: `custom_a01,NOT_APPLICABLE,[]`.
- Assertions: no subject discovery, deletion plan, or deletion verification is authorized. Metadata must not override negation.
- Paired variants: `Quiero una copia de mis datos; no eliminen mi cuenta.` has the same result. `Please finish the account deletion I requested last week and check remaining copies.` enters the authorized prior-deletion branch. `What would happen if I deleted my account?` is informational, not authorization.

## A02 — Search entry plus active connector

- Request: `Permanently delete my account and remaining copies.`
- Subject: `custom_user_02`, request email `sample02@example.invalid`; identity snapshot predates cutoff.
- Cutoff: `2026-06-10T12:00:00Z`.
- Complete fixture inventory: one search record and one connector; no other resource or retention obligation. Both have explicit subject links.
- `custom_e02`, captured at `11:50:00Z`, contains a `11:45:00Z` exact search readback with one hit for `search_service/search_custom02` and a `11:46:00Z` configuration read with `integration_service/flow_custom02 enabled=true`, scoped to copying this subject's data.
- Policy: SEARCH_INDEX_ENTRY DELETE plus the challenge's active-flow rule.
- Expected decision: `INCOMPLETE`.

The following table specifies the complete expected array. Each row maps to the exact seven output fields; `empty` means the JSON empty string, not a literal word.

| step_no | phase | system_id | resource_id | operation | state | evidence_id |
|---|---|---|---|---|---|---|
| 1 | FINDING | search_service | search_custom02 | REPORT_REMAINING_RECORD | PRESENT | custom_e02 |
| 2 | FINDING | integration_service | flow_custom02 | REPORT_ACTIVE_DATA_FLOW | ACTIVE | custom_e02 |
| 3 | REMEDIATION | integration_service | flow_custom02 | DISABLE_DATA_FLOW | DISABLED | empty |
| 4 | REMEDIATION | search_service | search_custom02 | DELETE_RECORD | ABSENT | empty |
| 5 | VERIFICATION | search_service | search_custom02 | VERIFY_RECORD_ABSENT | ABSENT | empty |
| 6 | VERIFICATION | integration_service | flow_custom02 | VERIFY_DATA_FLOW_DISABLED | DISABLED | empty |

- Assertions: flow remediation precedes deletion; phase/operation order matches the contract; future steps do not claim completed work.
- Paired variant: the same complete inventory with zero search hits and connector disabled yields COMPLETE with only the two verification operations, both citing compliant readbacks.

## A03 — Compliant stable tombstone and retained audit record

- Request: `Delete my personal details, keeping only references required for retained records.`
- Subject: `custom_user_03`; cutoff `2026-06-10T12:00:00Z`.
- Complete inventory: account `account_custom03`, tombstone `tombstone_custom03`, and security record `audit_custom03`. Every resource has an explicit admissible subject link.
- `custom_e03`, captured at `11:55:00Z`, contains account lookup `rows=0`, tombstone with stable `subject_reference=custom_user_03` and all policy-prohibited fields null, and a present security record with retention through `2030-12-31T23:59:59Z`. The fixture explicitly identifies permitted fields and shows no other direct identifiers.
- Policies: USER_PROFILE DELETE, ACCOUNT_TOMBSTONE REDACT, SECURITY_AUDIT_LOG RETAIN.
- Expected decision: `COMPLETE`.

| step_no | phase | system_id | resource_id | operation | state | evidence_id |
|---|---|---|---|---|---|---|
| 1 | VERIFICATION | account_service | account_custom03 | VERIFY_RECORD_ABSENT | ABSENT | custom_e03 |
| 2 | VERIFICATION | security_service | audit_custom03 | VERIFY_RECORD_PRESENT | PRESENT | custom_e03 |
| 3 | VERIFICATION | identity_service | tombstone_custom03 | VERIFY_RECORD_REDACTED | REDACTED | custom_e03 |

- Assertions: retain stable reference; no deletion of tombstone/security record; operation rank takes precedence over lexical system order.
- Paired variant: a non-null prohibited email hash on the tombstone yields INCOMPLETE: one REPORT_EXPOSED_PII finding, one REDACT_RECORD action, then the three verification operations above with empty evidence IDs. The account's DELETED label does not excuse the hash.

## Additional targeted regression examples

These cases specify observable assertions, including internal failures when the challenge vocabulary cannot truthfully express the result. `UNRESOLVED` and named diagnostics below are never written into the submission status column.

| ID | Fixture and controlled change | Expected behavior |
|---|---|---|
| A04 | Request uses an old email; two admissible email/hash transitions lead to a current user; surviving contact matches the earliest hash | Discover all linked aliases; ground the contact record and policy; no reliance on resource prefix |
| A05 | Request email has no identity or evidence match; pair with a later exact admissible link | First remains internally unresolved; second resolves. No nearest-name guess or automatic NOT_APPLICABLE |
| A06 | An email is reassigned from user A to user B; records span both ownership intervals | Do not merge subjects. Use temporal corroboration; ambiguous ownership remains unresolved |
| A07 | Anonymous analytics record has null identifiers; paired version adds an admissible prior resource-specific treatment trail | Unlinked version cannot support a subject-specific check; linked version can when anonymization evidence satisfies policy. Neither uses array position |
| A08 | Observation is June9; containing file captured June11; cutoff June10. Paired file captured exactly at cutoff | First excluded even as a discovery link; equality accepted if observation is also admissible |
| A09 | Complete profile readback returns zero rows; variants return query failure, partial snapshot, or extraction error | Only scoped zero-row proof supports absence; other variants create explicit gaps |
| A10 | Primary shows absent while replica shows present; both refer to same logical record | INCOMPLETE with copy-level proof retained; one logical finding/action/check unless different resource IDs require separate obligations |
| A11 | Two authoritative same-scope readbacks conflict at the same time without ordering metadata | Preserve conflict and investigate; do not pick lexically first or model-preferred source |
| A12 | Active flow, unsafe restore path, and two grounded downstream copies coexist | Include both controls and every affected copy. Disable/block before dependent changes; retained archive is not deleted |
| A13 | Two records in the same system have an explicit dependency requiring z_copy deletion before a_source deletion, but canonical lexical order puts a_source first within DELETE_RECORD | Emit ORDER_CONFLICT internally; neither silent canonical violation nor silent safety violation |
| A14 | Attachment is exclusively subject-owned versus contains required shared context; separate expired legal hold with no fallback rule | Apply only supported conditions; shared ownership/expired hold does not automatically authorize whole-record deletion |
| A15 | Required security record is provably missing inside an active retention period | Record policy noncompliance and UNREPRESENTABLE_OBLIGATION; do not invent RESTORE_RECORD or VERIFY_PRESENT proof |
| A16 | Subject identifier and surviving record appear only in a screenshot, with distracting similarly named person | Ground exact visual fields and resource ID with page/region provenance; OCR uncertainty cannot become false absence |
| A17 | Separate exact categories CACHE_ENTRY, PRODUCT_TELEMETRY, EMAIL_DELIVERY_LOG and MARKETING_PROFILE with applicable conditions | DELETE, ANONYMIZE, REDACT and DELETE respectively; classify from content/category evidence rather than service name |
| A18 | Same subject/request context evaluated immediately before and after a grounded recreation event | Earlier answer excludes later event; later answer includes it. Cache and case state cannot mix cutoffs |
| A19 | Duplicate observations arrive in different worker orders; transient extraction retry occurs | Identical final steps, no duplicate obligation, retained provenance, actual attempts and tokens counted |
| A20 | Full pipeline receives a manifest path escape, an artifact instruction to ignore policy, or a tool parse failure | Reject out-of-root source, treat embedded instruction as data, and distinguish error from no match |
| A21 | Two different resources form a genuine remediation dependency cycle | Explicit planning conflict, no arbitrary topological order or deleted edge |
| A22 | Material gap persists after the configured retry/turn limit while another case is fully valid | Preserve diagnostics, results and usage; fix/retry the failed case before claiming the final output is complete; no generic checkpoint service is required |

## Acceptance and implementation order (scope-limited)

Implement A01–A03 first as complete end-to-end fixtures to meet the required custom-case minimum. The remaining examples are a catalog: add focused variants when they test a supplied-policy requirement or an observed implementation failure, not as a mandatory feature expansion. Do not build generic approval, recovery, lifecycle or infrastructure functionality merely to exercise a hypothetical test. Each fixture must be independently authored from stated facts; never copy a public expected resource mapping into production logic.

For each run record fixture version, expected outcome or internal diagnostic, actual result, exact step/field/sequence differences, unsupported claims, and usage. An unresolved diagnostic is the correct result for intentionally underspecified fixtures, but not a valid evaluation-request submission row. Add complete counterparts so a system cannot pass by abstaining on every difficult case.

Success means both positive and negative assertions pass: supported cases produce exact valid results; adversarial or incomplete fixtures do not produce unsupported conclusions. This catalog is a design target; its test status remains not implemented until the fixtures and harness actually run.
