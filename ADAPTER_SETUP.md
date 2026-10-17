# Isolated adapter setup

Use a dedicated test organization, team and disabled Jenkins fixture jobs. Never put tokens in this repository, generated documentation, logs or chat.

## Hosted Sentry

Configure NEXUS_SENTRY_TOKEN, NEXUS_SENTRY_ORG, NEXUS_SENTRY_TEAM and NEXUS_SENTRY_READONLY_TOKEN securely in the isolated runner environment. Enable NEXUS_SENTRY_LIVE_TESTS=1 only after confirming the target is a disposable test organization. Resource names must start nexus-cert-. Deletion additionally requires NEXUS_ALLOW_CERTIFICATION_DELETE=1.

Run python -m unittest test_sentry_live -v. Missing configuration is a blocked/skipped live gate, not acceptance. Do not reuse a production organization or token.

## Jenkins fixture

Run PYTHONPATH=. python ci/test_real_jenkins.py on a Docker test host. Set NEXUS_TEST_RUNTIME=podman for Podman. The fixture generates ephemeral credentials internally and binds to loopback. Never enable public access to this fixture. The live acceptance suite verifies disabled-job creation, readback, duplicate convergence, invalid authentication, read-only denial and rollback absence.

## Transport and operation rules

External adapters require HTTPS, bounded timeouts and response sizes, and reject redirects. A lost acknowledgement is an unknown outcome until provider state confirms it. Existing or reconciled resources are not claimed as newly owned. Rollback checks resource identity before deletion and verifies absence afterward.

## Documentation preview

The existing Pages project expects the public directory with no build command. Run python ci/build_docs.py after changing these documents; commit the generated public files. CI runs python ci/build_docs.py --check. Only fixed, reviewed documentation sources are rendered; environment variables and credentials are never read. PR pushes create preview deployments; production remains on HOLD.
