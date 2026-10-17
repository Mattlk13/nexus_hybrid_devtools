import io
import unittest
from urllib import request, error
from unittest.mock import patch, MagicMock
from nexus_integrations import _json_request, _NoRedirect, IntegrationError

class TransportSecurityTests(unittest.TestCase):
    def test_redirect_never_forwards_credentials(self):
        with self.assertRaisesRegex(IntegrationError, 'redirect_rejected'):
            _NoRedirect().redirect_request(request.Request('https://example.com'), None, 302, '', {}, 'https://other.example')

    def test_auth_permission_duplicate_errors_are_redacted(self):
        for status, expected in [(401,'authentication_failed'),(403,'permission_denied'),(409,'duplicate_conflict')]:
            with self.subTest(status=status), patch('nexus_integrations._open', side_effect=error.HTTPError('https://example.com', status, 'secret', {}, None)):
                with self.assertRaisesRegex(IntegrationError, '^'+expected+'$'):
                    _json_request('https://example.com')

    def test_timeout_is_redacted(self):
        with patch('nexus_integrations._open', side_effect=TimeoutError('secret')):
            with self.assertRaisesRegex(IntegrationError, '^remote_request_failed$'):
                _json_request('https://example.com')

    def test_invalid_schema(self):
        response = MagicMock()
        response.__enter__.return_value = response
        response.read.return_value = b'[]'
        with patch('nexus_integrations._open', return_value=response):
            with self.assertRaisesRegex(IntegrationError, 'invalid_response_schema'):
                _json_request('https://example.com')
