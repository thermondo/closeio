import json
from datetime import date
from functools import partial

import pytest
from django.test.client import Client
from django.urls import reverse

from closeio.contrib.django import signals, views


@pytest.fixture
def csrf_client(client):
    return Client(enforce_csrf_checks=True)


@pytest.fixture
def closeio_signals():
    data = []

    def log(signal_name, *args, **kwargs):
        data.append((
            signal_name,
            args,
            kwargs
        ))

    signals.closeio_event.connect(
        partial(log, "closeio_event"),
        weak=False)

    signals.closeio_create.connect(
        partial(log, "closeio_create"),
        weak=False)

    signals.closeio_update.connect(
        partial(log, "closeio_update"),
        weak=False)

    signals.closeio_delete.connect(
        partial(log, "closeio_delete"),
        weak=False)

    signals.closeio_merge.connect(
        partial(log, "closeio_merge"),
        weak=False)

    signals.lead_create.connect(
        partial(log, "lead_create"),
        weak=False)

    signals.lead_update.connect(
        partial(log, "lead_update"),
        weak=False)

    signals.lead_delete.connect(
        partial(log, "lead_delete"),
        weak=False)

    signals.lead_merge.connect(
        partial(log, "lead_merge"),
        weak=False)

    return data


@pytest.fixture
def closeio_hook_content():
    return {
        'id': 'foo',
        'data': 'bar',
        'destination_id': 'baz',
        'source_id': 'thud',
        'organization_id': 'test_org_id'
    }


def test_no_data(csrf_client):
    url = reverse('closeio_webhook')

    response = csrf_client.post(url)
    assert response.status_code == 400


def test_invalid_json(csrf_client):
    url = reverse('closeio_webhook')

    response = csrf_client.post(
        url,
        data="asdf",
        content_type="application/json")
    assert response.status_code == 400


def test_formencode(csrf_client):
    url = reverse('closeio_webhook')

    response = csrf_client.post(
        url,
        data=dict(
            event=1,
            model=2,
            data={}
        ))

    assert response.status_code == 400


def test_wrong_json(csrf_client):
    url = reverse('closeio_webhook')

    response = csrf_client.post(
        url,
        data=json.dumps(dict()),
        content_type="application/json")

    assert response.status_code == 400


@pytest.mark.parametrize('organization_id', ['wrong_id', None])
def test_wrong_organization_id(csrf_client, closeio_signals, organization_id):
    url = reverse('closeio_webhook')

    response = csrf_client.post(
        url,
        data=json.dumps(dict(
            event='testevent',
            model='testmodel',
            data=dict(id=1, organization_id=organization_id),
        )),
        content_type="application/json")

    # We should get 200 response (so Closeio would not need to handle this request),
    #  but without triggered signals, since this is an incorrect organization
    assert response.status_code == 200
    assert closeio_signals == []


def test_ok_unknown(csrf_client, closeio_signals, closeio_hook_content):
    url = reverse('closeio_webhook')

    response = csrf_client.post(
        url,
        data=json.dumps(dict(
            event='testevent',
            model='testmodel',
            data=closeio_hook_content,
        )),
        content_type="application/json")

    assert response.status_code == 200

    assert closeio_signals == [
        ('closeio_event', (), {
            'event': 'testevent',
            'instance': closeio_hook_content,
            'model': 'testmodel',
            'signal': signals.closeio_event,
            'sender': views.CloseIOWebHook,
        }),
    ]


def test_ok_create(csrf_client, closeio_signals, closeio_hook_content):
    url = reverse('closeio_webhook')

    response = csrf_client.post(
        url,
        data=json.dumps(dict(
            event='create',
            model='testmodel',
            data=closeio_hook_content,
        )),
        content_type="application/json")

    assert response.status_code == 200

    assert closeio_signals == [
        ('closeio_create', (), {
            'instance': closeio_hook_content,
            'model': 'testmodel',
            'signal': signals.closeio_create,
            'sender': views.CloseIOWebHook,
        }),
        ('closeio_event', (), {
            'event': 'create',
            'instance': closeio_hook_content,
            'model': 'testmodel',
            'signal': signals.closeio_event,
            'sender': views.CloseIOWebHook,
        }),
    ]


def test_ok_lead_create(csrf_client, closeio_signals, closeio_hook_content):
    url = reverse('closeio_webhook')

    # let's check that date is being parsed
    closeio_hook_content['date_'] = '2014-01-01'

    response = csrf_client.post(
        url,
        data=json.dumps(dict(
            event='create',
            model='lead',
            data=closeio_hook_content,
        )),
        content_type="application/json")

    assert response.status_code == 200

    result_content = closeio_hook_content.copy()
    result_content['date_'] = date(2014, 1, 1)

    assert closeio_signals == [
        ('closeio_create', (), {
            'instance': result_content,
            'model': 'lead',
            'signal': signals.closeio_create,
            'sender': views.CloseIOWebHook,
        }),
        ('lead_create', (), {
            'instance': result_content,
            'signal': signals.lead_create,
            'sender': views.CloseIOWebHook,
        }),
        ('closeio_event', (), {
            'event': 'create',
            'instance': result_content,
            'model': 'lead',
            'signal': signals.closeio_event,
            'sender': views.CloseIOWebHook,
        }),
    ]


def test_ok_update(csrf_client, closeio_signals, closeio_hook_content):
    url = reverse('closeio_webhook')

    response = csrf_client.post(
        url,
        data=json.dumps(dict(
            event='update',
            model='testmodel',
            data=closeio_hook_content,
        )),
        content_type="application/json")

    assert response.status_code == 200

    assert closeio_signals == [
        ('closeio_update', (), {
            'instance': closeio_hook_content,
            'model': 'testmodel',
            'signal': signals.closeio_update,
            'sender': views.CloseIOWebHook,
        }),
        ('closeio_event', (), {
            'event': 'update',
            'instance': closeio_hook_content,
            'model': 'testmodel',
            'signal': signals.closeio_event,
            'sender': views.CloseIOWebHook,
        }),
    ]


def test_ok_lead_update(client, closeio_signals, closeio_hook_content):
    url = reverse('closeio_webhook')

    response = client.post(
        url,
        data=json.dumps(dict(
            event='update',
            model='lead',
            data=closeio_hook_content,
        )),
        content_type="application/json")

    assert response.status_code == 200

    assert closeio_signals == [
        ('closeio_update', (), {
            'instance': closeio_hook_content,
            'model': 'lead',
            'signal': signals.closeio_update,
            'sender': views.CloseIOWebHook,
        }),
        ('lead_update', (), {
            'instance': closeio_hook_content,
            'signal': signals.lead_update,
            'sender': views.CloseIOWebHook,
        }),
        ('closeio_event', (), {
            'event': 'update',
            'instance': closeio_hook_content,
            'model': 'lead',
            'signal': signals.closeio_event,
            'sender': views.CloseIOWebHook,
        }),
    ]


def test_ok_delete(csrf_client, closeio_signals, closeio_hook_content):
    url = reverse('closeio_webhook')

    response = csrf_client.post(
        url,
        data=json.dumps(dict(
            event='delete',
            model='testmodel',
            data=closeio_hook_content,
        )),
        content_type="application/json")

    assert response.status_code == 200

    assert closeio_signals == [
        ('closeio_delete', (), {
            'instance_id': closeio_hook_content['id'],
            'model': 'testmodel',
            'signal': signals.closeio_delete,
            'sender': views.CloseIOWebHook,
        }),
        ('closeio_event', (), {
            'event': 'delete',
            'instance': closeio_hook_content,
            'model': 'testmodel',
            'signal': signals.closeio_event,
            'sender': views.CloseIOWebHook,
        }),
    ]


def test_ok_lead_delete(client, closeio_signals, closeio_hook_content):
    url = reverse('closeio_webhook')

    response = client.post(
        url,
        data=json.dumps(dict(
            event='delete',
            model='lead',
            data=closeio_hook_content,
        )),
        content_type="application/json")

    assert response.status_code == 200

    assert closeio_signals == [
        ('closeio_delete', (), {
            'instance_id': closeio_hook_content['id'],
            'model': 'lead',
            'signal': signals.closeio_delete,
            'sender': views.CloseIOWebHook,
        }),
        ('lead_delete', (), {
            'instance_id': closeio_hook_content['id'],
            'signal': signals.lead_delete,
            'sender': views.CloseIOWebHook,
        }),
        ('closeio_event', (), {
            'event': 'delete',
            'instance': closeio_hook_content,
            'model': 'lead',
            'signal': signals.closeio_event,
            'sender': views.CloseIOWebHook,
        }),
    ]


def test_ok_merge(csrf_client, closeio_signals, closeio_hook_content):
    url = reverse('closeio_webhook')

    response = csrf_client.post(
        url,
        data=json.dumps(dict(
            event='merge',
            model='testmodel',
            data=closeio_hook_content,
        )),
        content_type="application/json")

    assert response.status_code == 200

    assert closeio_signals == [
        ('closeio_merge', (), {
            'source_id': closeio_hook_content['source_id'],
            'destination_id': closeio_hook_content['destination_id'],
            'model': 'testmodel',
            'signal': signals.closeio_merge,
            'sender': views.CloseIOWebHook,
        }),
        ('closeio_event', (), {
            'event': 'merge',
            'instance': closeio_hook_content,
            'model': 'testmodel',
            'signal': signals.closeio_event,
            'sender': views.CloseIOWebHook,
        }),
    ]


def test_ok_lead_merge(client, closeio_signals, closeio_hook_content):
    url = reverse('closeio_webhook')

    response = client.post(
        url,
        data=json.dumps(dict(
            event='merge',
            model='lead',
            data=closeio_hook_content,
        )),
        content_type="application/json")

    assert response.status_code == 200

    assert closeio_signals == [
        ('closeio_merge', (), {
            'source_id': closeio_hook_content['source_id'],
            'destination_id': closeio_hook_content['destination_id'],
            'model': 'lead',
            'signal': signals.closeio_merge,
            'sender': views.CloseIOWebHook,
        }),
        ('lead_merge', (), {
            'source_id': closeio_hook_content['source_id'],
            'destination_id': closeio_hook_content['destination_id'],
            'signal': signals.lead_merge,
            'sender': views.CloseIOWebHook,
        }),
        ('closeio_event', (), {
            'event': 'merge',
            'instance': closeio_hook_content,
            'model': 'lead',
            'signal': signals.closeio_event,
            'sender': views.CloseIOWebHook,
        }),
    ]
