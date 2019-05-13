import json

import pytest

from closeio.contrib.django.utils import webhook_signature_valid


class TestCloseioWebhookPermission:
    @pytest.fixture
    def payload(self):
        return '{"event": {"id": "ev_4YUAT9G7PQNYEX0V7HpiZa", '\
            '"date_created": "2019-01-01T13:33:00.842000", "data": {"object_type": '\
            '"activity.note", "action": "created", "note": "test content"}}, '\
            '"subscription_id": "whsub_mBTylJxRXaBOXcuQmgUdmL"}'

    @pytest.fixture
    def headers(self):
        return {
            'HTTP_CLOSE_SIG_HASH':
                'e6cf27a55de463dc46d8b5c16d2afe74d766e8f0c9892422c93573521cd377ed',
            'HTTP_CLOSE_SIG_TIMESTAMP': '1557751596',
            'content_type': 'application/json',
        }

    @pytest.fixture
    def webhook_settings(self, settings):
        webhook_id = 'whsub_mBTylJxRXaBOXcuQmgUdmL'
        signature_key = 'b9260244ef33625f9b4b26a27db08758cdd39478b852c73f2d33ab042eb8abb4'
        settings.CLOSEIO_WEBHOOK_SIGNATURE_KEYS = json.dumps({webhook_id: signature_key})

    def test_valid(self, rf, webhook_settings, headers, payload):
        """Test the signture check with a valid example."""
        request = rf.post('/some/webhook/view', payload, **headers)
        assert webhook_signature_valid(request) is True

    def test_invalid_because_no_signature_key_was_set(self, rf, headers, payload):
        """Should fail if we don't find the signature key inside the settings."""
        request = rf.post('/some/webhook/view', payload, **headers)
        assert webhook_signature_valid(request) is False

    def test_invalid_because_signature_key_is_wrong(self, rf, settings, headers, payload):
        """Should fail if the signature key is wrong."""
        webhook_id = 'whsub_mBTylJxRXaBOXcuQmgUdmL'
        signature_key = '0000000000000000000000000000000000000000000000000000000000000000'
        settings.CLOSEIO_WEBHOOK_SIGNATURE_KEYS = json.dumps({webhook_id: signature_key})

        request = rf.post('/some/webhook/view', payload, **headers)
        assert webhook_signature_valid(request) is False

    def test_invalid_because_payload_was_altered(self, rf, webhook_settings, headers, payload):
        """Should fail if the payload was altered after signing."""
        payload = payload.replace('test content', 'content altered by Dr. Evil')
        request = rf.post('/some/webhook/view', payload, **headers)
        assert webhook_signature_valid(request) is False

    def test_invalid_because_hash_was_not_provided(self, rf, webhook_settings, headers, payload):
        """Should fail if the hash doesn't match."""
        headers.pop('HTTP_CLOSE_SIG_HASH')
        request = rf.post('/some/webhook/view', payload, **headers)
        assert webhook_signature_valid(request) is False

    def test_invalid_because_hash_does_not_match(self, rf, webhook_settings, headers, payload):
        """Should fail if the hash doesn't match."""
        headers['HTTP_CLOSE_SIG_HASH'] = 'xxxxxx'
        request = rf.post('/some/webhook/view', payload, **headers)
        assert webhook_signature_valid(request) is False
