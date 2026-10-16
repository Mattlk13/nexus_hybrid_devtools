# NEXUS acceptance matrix — 2026-10-16

Production: HOLD. A skipped or queued check is never a pass.

| Boundary | Success / readback | Authentication / permission | Duplicate / concurrent | Timeout / unknown outcome | Rollback |
|---|---|---|---|---|---|
| Hosted Sentry | Blocked: isolated credentials absent | Unit coverage; hosted gate blocked | Unit reconciliation; hosted gate blocked | Unit reconciliation; actual socket transport timeout tested locally | Identity-bound implementation/unit tests; hosted deletion blocked |
| Ephemeral Jenkins | Real provider create/config readback | Real invalid credential and read-only user denial | Sequential real duplicate passes; concurrency covered by real acceptance harness | Lost acknowledgement injection uses real create and readback; ownership remains unclaimed | Real job deletion + absence readback; duplicate rollback verified |
| GitHub notifications | Live identity and paginated API read | Failure-path unit coverage | Duplicate mark-read unit coverage | Ambiguous subscription write attempts restore + readback in unit tests | Live subscription write and exact previous-state restoration pass; mark-read has no inverse and was not executed live |
| Container runtime | Real Docker earlier CI and current Podman lifecycle | Redacted command failures unit-tested | Sequential real duplicate passes; full concurrent container lifecycle not certified | Timeout is unconfirmed, not success | Real fixture start-failure injection + remove + runtime absence query pass |
| Terraform | Real built-in terraform_data apply/state/refresh | No cloud provider credentials exercised | Real duplicate + operation-lock policy tests | Pending receipt blocks blind retries | Real destroy and empty-state readback pass; cloud provider gate remains blocked |
| Browser | Actual staging journeys and four viewport sizes | App authentication is disclosed as unavailable; no fabricated signed-in acceptance | Private draft refresh passes in isolated browser contexts | Console/network assertions retained | Browser-local test context discarded; no external publication |

The actual application logo defect is fixed in Nexus2 draft PR #49. Candidate-overlay browser evidence is distinct from deployed-state evidence. Current hosted CI and staging deployment are queued. Manual axe incomplete/screen-reader review and the existing dependency security findings remain open.
