import datetime
import hashlib
import hmac
import json
import random
import secrets
import string

import pytest


@pytest.fixture
def random_string():
    return '%030x' % random.randrange(16 ** 30)


@pytest.yield_fixture
def lead_status(closeio, random_string):
    ls = closeio.create_lead_status(random_string)

    yield ls

    # closeio.delete_lead_status(ls['id'])


@pytest.yield_fixture
def opportunity_status(closeio, random_string):
    os = closeio.create_opportunity_status(random_string, 'active')

    yield os

    # closeio.delete_lead_status(ls['id'])


@pytest.fixture
def sign_closeio_webhook_request(settings):
    """Sign requests for endpoints that expect webhooks from Closeio.

    Sets correct settings, alters the payload and computes headers so that fake
    requests to webhook endpoints pass signature validation.

    Usage::
        data = {'some key': 'some value'}
        data, headers = _sign_request(data)
        client.post('/my/url/', data, **headers)
    """
    def _sign_request(payload):
        webhook_id = 'whsub_' + ''.join(random.choice(string.ascii_letters) for i in range(22))
        signature_key = secrets.token_hex(32)
        settings.CLOSEIO_WEBHOOK_SIGNATURE_KEYS = json.dumps({webhook_id: signature_key})

        payload.update({'subscription_id': webhook_id})

        timestamp = str(int(datetime.datetime.now().timestamp()))
        payload = json.dumps(payload)
        data = timestamp + payload

        sig_hash = hmac.new(
            bytearray.fromhex(signature_key),
            data.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()

        headers = {
            'HTTP_CLOSE_SIG_HASH': sig_hash,
            'HTTP_CLOSE_SIG_TIMESTAMP': timestamp,
            'content_type': 'application/json',
        }

        return payload, headers

    return _sign_request
