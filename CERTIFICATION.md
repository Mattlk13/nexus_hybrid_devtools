# Current certification status — 2026-10-17 UTC

Production HOLD. DCO passes on all five NEXUS draft PRs. Devtools signed head 936db0b passed Actions runs 38992499274 and 38992502685, including real Jenkins acceptance. A later documentation commit must receive its own current-head checks.

Actual Nexus2 staging deployment and rollback passed run 38993772022. Actual four-width browser journeys pass. New platform text contrast and keyboard focus defects are fixed in Nexus2 PR49 and covered by deployed browser evidence in the accessibility PR. Full manual accessibility review remains open.

The Node semantic-release dependency blocker was removed by replacing that preview integration with pinned Python Semantic Release. Candidate dependency audits pass without suppressions. Existing default-branch alerts await approved merge and rescan; none were dismissed.

Hosted Sentry credentials and provider-specific cloud test resources remain absent. Full live permission/timeout/rollback-failure coverage, release publication and irreversible notification mark-read acceptance remain open. Documentation below retains historical results; historical queued/blocked statements do not supersede this dated status.

# NEXUS resumed certification — 2026-10-16

Decision: **HOLD**. No production deployment, merge, release publication or service purchase.

## Resumed certification results

- PASS: 18 local Python tests, including real HTTP socket 401, 403, 409 and timeout/redaction tests. One hosted Sentry gate skips because credentials are absent.
- PASS: final real Jenkins matrix includes concurrent create convergence and injected lost-create-ack reconciliation without claiming ownership: 3 acceptance tests pass in 40.827s.
- PASS: real Jenkins 2.580.1 with matrix-auth 3.3, in an ephemeral loopback-only Podman container on MattWorkspace. Authenticated disabled-job creation, duplicate reuse, invalid authentication, read-only permission denial, deletion rollback and repeated rollback disappearance checks pass (1 acceptance test, 72.634s).
- Implemented: certification-scoped Sentry create/readback, ambiguous-outcome reconciliation without claiming ownership, duplicate reads, identity-bound rollback; exposed through the engine for nexus-cert-* resources. Hosted Sentry acceptance is still BLOCKED. Required configuration: NEXUS_SENTRY_TOKEN, NEXUS_SENTRY_ORG, NEXUS_SENTRY_TEAM, NEXUS_SENTRY_READONLY_TOKEN and NEXUS_SENTRY_LIVE_TESTS=1. Store credentials in an isolated environment, never chat or source.
- Jenkins loopback HTTP is permitted only with explicit fixture opt-in and literal 127.0.0.1. Remote Jenkins still requires HTTPS. Fixture credentials are generated inside the temporary server and are not printed.
- Current-head CI must pass. New hosted Linux jobs are queued; earlier passing commits do not certify these changes.

Reproduce: `python -m unittest discover -v -p 'test_*.py'`; `PYTHONPATH=. python ci/test_real_jenkins.py` (Docker); set NEXUS_TEST_RUNTIME=podman for Podman.

## Earlier evidence (historical)

# NEXUS certification evidence — 2026-10-16

Decision: **HOLD**. Draft PR #1; no merge, production deployment, service purchase, or publication authorized by this evidence.

11 Python tests pass locally. GitHub Actions run 38960023548 passed on commit 798b31e.
Sentry and Jenkins create operations require readback before success. Redirects are rejected; JSON sizes/schema checked; transport auth/permission/conflict/timeout errors are redacted. Jenkins API token authentication no longer depends on a crumb endpoint.
Live Sentry/Jenkins acceptance is BLOCKED: required environment configuration absent locally and on MattWorkspace. No isolated project/job was created. Duplicate reconciliation, concurrent provisioning, permission failures on real services, timeout reconciliation and rollback of service resources remain unverified. Existing mock readbacks are not live evidence.

## Reproduce

`python -m unittest discover -v -p 'test_*.py'`

GitHub Actions runs on the PR branch with contents:read and a bounded job timeout. Review current-head Actions results; prior passing commits are not substitutes for current-head evidence. No tests against live Sentry/Jenkins or a production environment were executed.

## Expanded real Jenkins failure acceptance — 2026-10-17 UTC

All five isolated Jenkins tests pass in 17.885 seconds on Podman. Added actual read-only rollback denial plus provider readback confirming the job remains, followed by successful admin cleanup. Added injected lost-delete-ack after real deletion: the adapter fails closed, and a subsequent readback verifies absence. This is transport fault injection around a real provider operation, not a naturally occurring provider outage. Existing create/concurrency/authentication tests also pass. Ephemeral server cleanup completed.

Pages documentation preview deployment 8b34ce12-d9b4-481a-9343-cf29096cf6a5 passed on documentation commit 2bc1509. Current-head regression runs must pass after this test update.

## Executable hosted acceptance gate — 2026-10-17 UTC

Added a separate hosted Sentry certification workflow bound to nexus-certification. Missing credentials, a mismatched isolated organization or skipped acceptance now produce a non-success gate result. Four guard tests pass: missing configuration never reaches provider tests, wrong organization confirmation blocks, skipped acceptance fails, and exception details do not leak into evidence. Local preflight produced BLOCKED with zero provider tests because all five required configuration entries were absent. This intentionally prevents green regression tests from being interpreted as complete hosted certification. Production HOLD persists.
