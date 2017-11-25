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


def test_ok_unknown(csrf_client, closeio_signals):
    url = reverse('closeio_webhook')

    response = csrf_client.post(
        url,
        data=json.dumps(dict(
            event='testevent',
            model='testmodel',
            data=dict(data=1),
        )),
        content_type="application/json")

    assert response.status_code == 200

    assert closeio_signals == [
        ('closeio_event', (), {
            'event': 'testevent',
            'instance': dict(data=1),
            'model': 'testmodel',
            'signal': signals.closeio_event,
            'sender': views.CloseIOWebHook,
        }),
    ]


def test_ok_create(csrf_client, closeio_signals):
    url = reverse('closeio_webhook')

    response = csrf_client.post(
        url,
        data=json.dumps(dict(
            event='create',
            model='testmodel',
            data=dict(data=1),
        )),
        content_type="application/json")

    assert response.status_code == 200

    assert closeio_signals == [
        ('closeio_create', (), {
            'instance': dict(data=1),
            'model': 'testmodel',
            'signal': signals.closeio_create,
            'sender': views.CloseIOWebHook,
        }),
        ('closeio_event', (), {
            'event': 'create',
            'instance': dict(data=1),
            'model': 'testmodel',
            'signal': signals.closeio_event,
            'sender': views.CloseIOWebHook,
        }),
    ]


def test_ok_lead_create(csrf_client, closeio_signals):
    url = reverse('closeio_webhook')

    response = csrf_client.post(
        url,
        data=json.dumps(dict(
            event='create',
            model='lead',
            data=dict(
                data=1,
                date_='2014-01-01',
            ),
        )),
        content_type="application/json")

    assert response.status_code == 200

    assert closeio_signals == [
        ('closeio_create', (), {
            'instance': dict(
                data=1,
                date_=date(2014, 1, 1),
            ),
            'model': 'lead',
            'signal': signals.closeio_create,
            'sender': views.CloseIOWebHook,
        }),
        ('lead_create', (), {
            'instance': dict(
                data=1,
                date_=date(2014, 1, 1),
            ),
            'signal': signals.lead_create,
            'sender': views.CloseIOWebHook,
        }),
        ('closeio_event', (), {
            'event': 'create',
            'instance': dict(
                data=1,
                date_=date(2014, 1, 1),
            ),
            'model': 'lead',
            'signal': signals.closeio_event,
            'sender': views.CloseIOWebHook,
        }),
    ]


def test_ok_update(csrf_client, closeio_signals):
    url = reverse('closeio_webhook')

    response = csrf_client.post(
        url,
        data=json.dumps(dict(
            event='update',
            model='testmodel',
            data=dict(data=1),
        )),
        content_type="application/json")

    assert response.status_code == 200

    assert closeio_signals == [
        ('closeio_update', (), {
            'instance': dict(data=1),
            'model': 'testmodel',
            'signal': signals.closeio_update,
            'sender': views.CloseIOWebHook,
        }),
        ('closeio_event', (), {
            'event': 'update',
            'instance': dict(data=1),
            'model': 'testmodel',
            'signal': signals.closeio_event,
            'sender': views.CloseIOWebHook,
        }),
    ]


def test_ok_lead_update(client, closeio_signals):
    url = reverse('closeio_webhook')

    response = client.post(url,
                           data=json.dumps(dict(
                               event='update',
                               model='lead',
                               data=dict(data=1),
                           )),
                           content_type="application/json")

    assert response.status_code == 200

    assert closeio_signals == [
        ('closeio_update', (), {
            'instance': dict(data=1),
            'model': 'lead',
            'signal': signals.closeio_update,
            'sender': views.CloseIOWebHook,
        }),
        ('lead_update', (), {
            'instance': dict(data=1),
            'signal': signals.lead_update,
            'sender': views.CloseIOWebHook,
        }),
        ('closeio_event', (), {
            'event': 'update',
            'instance': dict(data=1),
            'model': 'lead',
            'signal': signals.closeio_event,
            'sender': views.CloseIOWebHook,
        }),
    ]


def test_ok_delete(csrf_client, closeio_signals):
    url = reverse('closeio_webhook')

    response = csrf_client.post(
        url,
        data=json.dumps(dict(
            event='delete',
            model='testmodel',
            data=dict(id=321),
        )),
        content_type="application/json")

    assert response.status_code == 200

    assert closeio_signals == [
        ('closeio_delete', (), {
            'instance_id': 321,
            'model': 'testmodel',
            'signal': signals.closeio_delete,
            'sender': views.CloseIOWebHook,
        }),
        ('closeio_event', (), {
            'event': 'delete',
            'instance': dict(id=321),
            'model': 'testmodel',
            'signal': signals.closeio_event,
            'sender': views.CloseIOWebHook,
        }),
    ]


def test_ok_lead_delete(client, closeio_signals):
    url = reverse('closeio_webhook')

    response = client.post(url,
                           data=json.dumps(dict(
                               event='delete',
                               model='lead',
                               data=dict(id=321),
                           )),
                           content_type="application/json")

    assert response.status_code == 200

    assert closeio_signals == [
        ('closeio_delete', (), {
            'instance_id': 321,
            'model': 'lead',
            'signal': signals.closeio_delete,
            'sender': views.CloseIOWebHook,
        }),
        ('lead_delete', (), {
            'instance_id': 321,
            'signal': signals.lead_delete,
            'sender': views.CloseIOWebHook,
        }),
        ('closeio_event', (), {
            'event': 'delete',
            'instance': dict(id=321),
            'model': 'lead',
            'signal': signals.closeio_event,
            'sender': views.CloseIOWebHook,
        }),
    ]


def test_ok_merge(csrf_client, closeio_signals):
    url = reverse('closeio_webhook')

    response = csrf_client.post(
        url,
        data=json.dumps(dict(
            event='merge',
            model='testmodel',
            data=dict(source_id=321, destination_id=123),
        )),
        content_type="application/json")

    assert response.status_code == 200

    assert closeio_signals == [
        ('closeio_merge', (), {
            'source_id': 321,
            'destination_id': 123,
            'model': 'testmodel',
            'signal': signals.closeio_merge,
            'sender': views.CloseIOWebHook,
        }),
        ('closeio_event', (), {
            'event': 'merge',
            'instance': dict(source_id=321, destination_id=123),
            'model': 'testmodel',
            'signal': signals.closeio_event,
            'sender': views.CloseIOWebHook,
        }),
    ]


def test_ok_lead_merge(client, closeio_signals):
    url = reverse('closeio_webhook')

    response = client.post(url,
                           data=json.dumps(dict(
                               event='merge',
                               model='lead',
                               data=dict(source_id=321, destination_id=123),
                           )),
                           content_type="application/json")

    assert response.status_code == 200

    assert closeio_signals == [
        ('closeio_merge', (), {
            'source_id': 321,
            'destination_id': 123,
            'model': 'lead',
            'signal': signals.closeio_merge,
            'sender': views.CloseIOWebHook,
        }),
        ('lead_merge', (), {
            'source_id': 321,
            'destination_id': 123,
            'signal': signals.lead_merge,
            'sender': views.CloseIOWebHook,
        }),
        ('closeio_event', (), {
            'event': 'merge',
            'instance': dict(source_id=321, destination_id=123),
            'model': 'lead',
            'signal': signals.closeio_event,
            'sender': views.CloseIOWebHook,
        }),
    ]
