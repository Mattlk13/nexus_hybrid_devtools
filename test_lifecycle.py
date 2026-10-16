import os
import unittest
from unittest.mock import patch
from nexus_lifecycle import sentry_create,sentry_rollback,jenkins_create,jenkins_rollback,IntegrationError

class SentryLifecycleTests(unittest.TestCase):
    def setUp(self):
        self.env=patch.dict(os.environ,{'NEXUS_SENTRY_TOKEN':'fixture','NEXUS_SENTRY_ORG':'fixture-org','NEXUS_ALLOW_CERTIFICATION_DELETE':'1'})
        self.env.start();self.addCleanup(self.env.stop)
    def test_create_duplicate_and_owned_rollback(self):
        remote={'id':'123','slug':'nexus-cert-test'}
        with patch('nexus_lifecycle._read',side_effect=[None,remote]),patch('nexus_lifecycle._json_request',return_value=(201,remote)):
            receipt=sentry_create('nexus-cert-test');self.assertTrue(receipt['created'])
        with patch('nexus_lifecycle._read',return_value=remote),patch('nexus_lifecycle._json_request') as mutate:
            duplicate=sentry_create('nexus-cert-test');self.assertTrue(duplicate['duplicate']);mutate.assert_not_called()
        with patch('nexus_lifecycle._read',side_effect=[remote,None]),patch('nexus_lifecycle._json_request'):
            self.assertTrue(sentry_rollback(receipt)['verified'])
        with self.assertRaisesRegex(IntegrationError,'rollback_not_authorized'): sentry_rollback(duplicate)
    def test_timeout_reconciles_without_claiming_ownership(self):
        with patch('nexus_lifecycle._read',side_effect=[None,{'id':'1','slug':'nexus-cert-test'}]),patch('nexus_lifecycle._json_request',side_effect=IntegrationError('remote_request_failed')):
            result=sentry_create('nexus-cert-test');self.assertFalse(result['created']);self.assertTrue(result['verified'])
    def test_auth_and_permission_failures_do_not_mutate(self):
        for code in ('authentication_failed','permission_denied'):
            with self.subTest(code=code),patch('nexus_lifecycle._read',side_effect=IntegrationError(code)),patch('nexus_lifecycle._json_request') as mutate:
                with self.assertRaisesRegex(IntegrationError,code): sentry_create('nexus-cert-test')
                mutate.assert_not_called()
    def test_rollback_rejects_changed_remote_identity(self):
        receipt={'created':True,'org':'fixture-org','slug':'nexus-cert-test','id':'1'}
        with patch('nexus_lifecycle._read',return_value={'id':'2'}),patch('nexus_lifecycle._json_request') as mutate:
            with self.assertRaisesRegex(IntegrationError,'rollback_identity_conflict'): sentry_rollback(receipt)
            mutate.assert_not_called()

class JenkinsPolicyTests(unittest.TestCase):
    def test_no_remote_http_optin(self):
        with patch.dict(os.environ,{'NEXUS_JENKINS_URL':'http://example.com','NEXUS_JENKINS_USER':'fixture','NEXUS_JENKINS_TOKEN':'fixture','NEXUS_JENKINS_LOOPBACK_FIXTURE':'1'}):
            with self.assertRaisesRegex(IntegrationError,'https_not_configured'): jenkins_create({})
    def test_rollback_refuses_unowned_receipt(self):
        with patch.dict(os.environ,{'NEXUS_JENKINS_URL':'https://example.com','NEXUS_JENKINS_USER':'fixture','NEXUS_JENKINS_TOKEN':'fixture'}):
            with self.assertRaisesRegex(IntegrationError,'rollback_not_authorized'): jenkins_rollback({'created':False})
