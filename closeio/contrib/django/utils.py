import hashlib
import hmac
import json
import logging

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

logger = logging.getLogger(__name__)


def webhook_signature_valid(request):
    """Verifies the integrity of signed webhooks from Closeio.

    When a webhook subscription is created via the Closeio API you get a secret
    signature key in the response of the request. This is the key that Closeio
    uses to sign their webhooks. You can use the key to verify that the request
    is indeed coming from Closeio (only Closeio should have the signature key)
    and that the payload was not altered inbetween.
    This is a simple security mechanism to protect you from false requests to your
    endpoints that receive the webhooks.

    The signature key for each webhook subscription needs to be stored inside the
    environment variable `CLOSEIO_WEBHOOK_SIGNATURE_KEYS` as json string containing
    the webhook subscription ID as key and the signature key as value, e.g.::
        CLOSEIO_WEBHOOK_SIGNATURE_KEYS = '{"whsub_1": "123", "whsub_2": "456"}'

    More information can be found in the `Closeio Docs`_ in the section "Webhook signatures".

    .. _Closeio Docs: https://developer.close.com/#webhook

    Args:
        request: an instance of Django's ``HttpRequest`` object
    """
    try:
        payload = json.loads(request.body)
    except json.JSONDecodeError:
        return False
    subscription_id = payload.get('subscription_id')
    if not subscription_id:
        return False

    try:
        signature_keys = json.loads(settings.CLOSEIO_WEBHOOK_SIGNATURE_KEYS)
    except AttributeError:
        raise ImproperlyConfigured('CLOSEIO_WEBHOOK_SIGNATURE_KEYS setting not set.')
    except TypeError:
        raise ImproperlyConfigured('Cannot load value of CLOSEIO_WEBHOOK_SIGNATURE_KEYS to json.')

    try:
        signature_key = signature_keys[subscription_id]
    except TypeError:
        raise ImproperlyConfigured('Parsed value of CLOSEIO_WEBHOOK_SIGNATURE_KEYS is expected '
                                   'to be a dictionary.')
    except KeyError:
        logger.error('No signature key set for Closeio webhook subscription with id %s.',
                     subscription_id)
        return False

    close_sig_hash = request.META.get('HTTP_CLOSE_SIG_HASH')
    close_sig_timestamp = request.META.get('HTTP_CLOSE_SIG_TIMESTAMP')

    if not close_sig_hash or not close_sig_timestamp:
        return False

    data = close_sig_timestamp + request.body.decode('utf-8')
    try:
        signature = hmac.new(
            bytearray.fromhex(signature_key),
            data.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
    except (TypeError, ValueError):
        raise ImproperlyConfigured('The signature key for a Closeio webhook subscription must '
                                   'be a valid string from a hexadecimal number.')
    valid = hmac.compare_digest(close_sig_hash, signature)

    return valid
