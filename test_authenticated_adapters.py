"""Adapter tests use fake HTTP responses only; no live account mutations."""
import os
import unittest
from unittest.mock import patch
from nexus_integrations import IntegrationError, provision_sentry, provision_jenkins


class AuthenticatedAdapterTests(unittest.TestCase):
    def test_sentry_requires_credentials(self):
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaisesRegex(IntegrationError, "credentials_not_configured"):
                provision_sentry("example")

    def test_sentry_verifies_readback(self):
        with patch.dict(os.environ, {"NEXUS_SENTRY_TOKEN": "fake", "NEXUS_SENTRY_ORG": "org"}):
            with patch("nexus_integrations._json_request", side_effect=[
                (201, {"slug": "example"}), (200, {"slug": "example"})]) as client:
                result = provision_sentry("example")
            self.assertTrue(result["success"])
            self.assertEqual(client.call_count, 2)

    def test_sentry_rejects_mismatched_readback(self):
        with patch.dict(os.environ, {"NEXUS_SENTRY_TOKEN": "fake", "NEXUS_SENTRY_ORG": "org"}):
            with patch("nexus_integrations._json_request", side_effect=[
                (201, {"slug": "example"}), (200, {"slug": "different"})]):
                with self.assertRaisesRegex(IntegrationError, "verification_failed"):
                    provision_sentry("example")

    def test_jenkins_requires_https_credentials(self):
        with patch.dict(os.environ, {"NEXUS_JENKINS_URL": "http://localhost"}, clear=True):
            with self.assertRaisesRegex(IntegrationError, "not_configured"):
                provision_jenkins({"name": "test", "config_xml": "<project/>"})

if __name__ == "__main__":
    unittest.main()

class JenkinsReadbackTests(unittest.TestCase):
    def test_create_requires_matching_remote_state(self):
        from unittest.mock import MagicMock
        env={'NEXUS_JENKINS_URL':'https://jenkins.example','NEXUS_JENKINS_USER':'tester','NEXUS_JENKINS_TOKEN':'fake'}
        response=MagicMock();response.__enter__.return_value=response;response.status=201
        for name,passes in [('fixture',True),('wrong',False)]:
            with self.subTest(name=name),patch.dict(os.environ,env),patch('nexus_integrations._open',return_value=response),patch('nexus_integrations._json_request',return_value=(200,{'name':name})):
                if passes: self.assertTrue(provision_jenkins({'name':'fixture','config_xml':'<project/>'})['verified'])
                else:
                    with self.assertRaisesRegex(IntegrationError,'verification_failed'):
                        provision_jenkins({'name':'fixture','config_xml':'<project/>'})
