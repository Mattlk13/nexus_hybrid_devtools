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
