# Usage report

## Final full-dataset run

No fully evidence-validated final run is complete. A 518-row candidate exists. The development measurements below are not a substitute for final-run usage/cost.

## Measured development pilots

Provider: OpenAI. Model: gpt-6.1-sol. Reasoning: triage low; audit and visual interpretation medium. Standard Responses API; remote tracing disabled. SDK and HTTP automatic retries disabled. Any audit-repair calls are explicit and included below. Offline fake-model tests are excluded.

| Model | Stage | Requests | Known input tokens | Known output tokens | Unknown-usage requests |
|---|---|---:|---:|---:|---:|
| gpt-6.1-sol | audit | 309 | 2729875 | 134201 | 4 |
| gpt-6.1-sol | audit_repair | 79 | 922824 | 46872 | 0 |
| gpt-6.1-sol | triage | 101 | 23995 | 4921 | 0 |
| gpt-6.1-sol | triage_batch | 18 | 34476 | 18915 | 0 |
| gpt-6.1-sol | triage_cache | 0 | 0 | 0 | 0 |
| gpt-6.1-sol | vision | 36 | 100522 | 39047 | 0 |
| Overall | All development | 543 | 3811692 | 243956 | 4 |

Known total tokens: 4055648.

Known-token Standard uncached baseline estimate: USD 10.062944. This estimate excludes cache discounts/write premiums, regional premiums and unreported tokens; it is not an invoice or complete cost.

Conservative settled cost allowance: USD 23.647822.
Outstanding/unknown request reservations: USD 1.549427.
Total budget committed (including reservations): USD 25.197249 of USD 50.00.

Budget prices allow short-context input/cache writes up to $5/M and output $10/M; long-context input/cache writes up to $10/M and output $15/M, plus a conservative 10% regional premium. Official Standard base rates are $2/M input and $10/M output. Prices verified 2026-10-25 at [OpenAI pricing](https://developers.openai.com/api/docs/pricing). Requests reserve before sending; failures/crashes keep their full reservation. The single persistent budget is shared by all pilot, vision, audit and final calls.

Visual extraction is cached by source image/model/prompt hash. Cache hits make no model call. Development shared-extraction calls appear under vision; the final report must state reuse and any allocated shared preparation costs. Local evidence tools are not model requests. SDK aggregate usage is not added again. Unknown usage stays unknown, not zero.

Final averages per evaluation request, per-model totals and total/per-request final cost remain unavailable until the successful 518-case run. Credentials and sensitive configuration are never included in this report.

## Measured full candidate pass

Output kind: candidate
Run output SHA-256: 014900dd0b17b5d397a7c0e35204b093c61e7df86e1f815a01c8d775078a79df

Run: `runs/full-candidate-v2`; requests: 518.
Provider: OpenAI; model: gpt-6.1-sol. Request-only triage effort: low. Reused audit/vision preparation used medium effort.

| Model | Stage | Model calls | Known input | Known output | Unknown calls |
|---|---|---:|---:|---:|---:|
| gpt-6.1-sol | triage_batch | 17 | 32613 | 17447 | 0 |
| gpt-6.1-sol | triage_cache | 0 | 0 | 0 | 0 |
| Overall | All stages | 17 | 32613 | 17447 | 0 |

Known total tokens: 50060; average per request: 96.641.
Known-token uncached baseline estimate for new calls in this pass: USD 0.239696; per request: USD 0.00046273.

This estimate excludes cache rate changes and unreported usage; it is not an invoice. Cache hits have zero new calls/tokens, not zero historical cost. The development totals above include the historical visual extraction, cached individual authorizations and saved audit proposals reused by this pass, plus failed and superseded work. No fraction of that shared preparation is silently relabeled as a new call or assigned a fabricated exact per-case cost. Thus the new-call estimate is incremental, not total end-to-end cost. The all-development committed ceiling is the conservative cost bound covering all preparation and this run. Local readback processing makes no model call.

A final fully evidence-validated run is still unavailable. These candidate measurements replace neither the semantic limitations nor the unknown hidden accuracy. Credentials are excluded.

### Conservative inclusive preparation allocation

For an inclusive bound, allocate all recorded development preparation, superseded attempts and evaluation overhead to this candidate. This deliberately overallocates shared preparation; it is not exact marginal cache attribution or an invoice. The preceding stage table reports the measured candidate pass separately, without double counting.

Allocated overall OpenAI/gpt-6.1-sol calls: 543; unknown-usage calls: 4.
Allocated known input/output/total tokens: 3811692/243956/4055648; mean total per candidate request: 7829.436.
Allocated known-token uncached baseline estimate: USD 10.062944; per candidate request: USD 0.01942653.
Inclusive committed budget allowance (including unknown reservations): USD 25.197249; per candidate request: USD 0.04864334.
