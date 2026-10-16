"""Explicit opt-in hosted Sentry gate. Skips are blockers, never provider passes."""
import os
import secrets
import unittest
from unittest.mock import patch
from nexus_lifecycle import sentry_create,sentry_rollback,IntegrationError
@unittest.skipUnless(os.getenv('NEXUS_SENTRY_LIVE_TESTS')=='1','hosted Sentry test account not configured')
class HostedSentryTests(unittest.TestCase):
    def test_create_duplicate_auth_permission_and_rollback(self):
        if not os.getenv('NEXUS_SENTRY_READONLY_TOKEN'):
            self.fail('isolated read-only Sentry credential required for permission gate')
        project='nexus-cert-'+secrets.token_hex(8)
        receipt=sentry_create(project)
        try:
            self.assertTrue(receipt['created'])
            self.assertTrue(sentry_create(project)['duplicate'])
            with patch.dict(os.environ,{'NEXUS_SENTRY_TOKEN':'invalid-certification-token'}):
                with self.assertRaises(IntegrationError):sentry_create(project)
            with patch.dict(os.environ,{'NEXUS_SENTRY_TOKEN':os.environ['NEXUS_SENTRY_READONLY_TOKEN']}):
                with self.assertRaisesRegex(IntegrationError,'permission_denied'):
                    sentry_create(project+'-denied')
        finally:
            # Async provider deletion stays pending/failing until disappearance
            # is independently confirmed; no successful rollback is invented.
            with patch.dict(os.environ,{'NEXUS_ALLOW_CERTIFICATION_DELETE':'1'}):
                self.assertTrue(sentry_rollback(receipt)['verified'])
