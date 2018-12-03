import datetime
import json
import os
import random
import string
import time

import pytest

from closeio import utils
from closeio.closeio import CloseIO

API_KEY = os.environ.get('API_KEY')
TEST_DIR = os.path.dirname(__file__)
FIXTURE_DIR = os.path.join(TEST_DIR, 'fixtures')


class TestEndToEnd(object):
    @pytest.fixture
    def client(self):
        return CloseIO(API_KEY)

    @pytest.fixture
    def random_string(self):
        return ''.join([
            random.choice(string.ascii_uppercase)
            for _ in range(10)
        ])

    @pytest.yield_fixture
    def lead(self, client):

        def wait_for_index(name):
            query = 'name:{}'.format(name)
            i = 0
            while not list(client.get_leads(query)):
                i += 1
                if i == 3:
                    raise RuntimeWarning("Lead wasn't indexed within 15 seconds")
                time.sleep(5)

        with open(os.path.join(FIXTURE_DIR, 'lead.json')) as f:
            lead = utils.parse(json.load(f))
            response = client.create_lead(lead)
            wait_for_index(response['name'])
            yield response
            client.delete_lead(response['id'])

    @pytest.yield_fixture
    def opportunity(self, client, lead):
        with open(os.path.join(FIXTURE_DIR, 'opportunity.json')) as f:
            opportunity = utils.parse(json.load(f))
            opportunity.update({
                'lead_id': lead['id'],
            })
            response = client.create_opportunity(opportunity)
            yield response
            client.delete_opportunity(response['id'])

    @pytest.yield_fixture
    def task(self, client, lead):
        with open(os.path.join(FIXTURE_DIR, 'task.json')) as f:
            def wait_for_index(lead_id):
                query = {'lead_id': lead_id}
                i = 0
                while not list(client.get_tasks(**query)):
                    i += 1
                    if i == 10:
                        raise RuntimeWarning("Lead wasn't indexed within 10 seconds")
                    time.sleep(1)

            task = utils.parse(json.load(f))
            task.update({
                'lead_id': lead['id'],
                'assigned_to': client.me()['id'],
            })
            response = client.create_task(**task)
            wait_for_index(response['lead_id'])
            yield response

    @pytest.fixture
    def export(self, client, random_string):
        return client.create_lead_export(random_string)

    def test_create_lead(self, client):
        with open(os.path.join(FIXTURE_DIR, 'lead.json')) as f:
            lead = utils.parse(json.load(f))
            response = client.create_lead(lead)
            assert all(False for k in lead if k not in response), dict(response)

            client.delete_lead(response['id'])  # Clean up

    def test_get_lead(self, client, lead):
        response = client.get_lead(lead['id'])
        assert all(False for k in lead if k not in response), dict(response)

    @pytest.mark.flaky(reruns=5)
    def test_get_leads(self, client, lead):
        query = 'name:{name}'.format(**lead)
        response = client.get_leads(query=query)
        lead_ids = [l['id'] for l in response]
        assert lead['id'] in lead_ids, list(response)

    def test_update_lead(self, client, lead):
        fields = {
            "description": "Best show ever canceled.  Sad."
        }
        response = client.update_lead(lead['id'], fields)
        assert fields['description'] == response['description']

    @pytest.mark.parametrize('_date', [
        datetime.datetime.now(), datetime.date.today(), None
    ])
    def test_create_task(self, client, lead, _date):
        with open(os.path.join(FIXTURE_DIR, 'task.json')) as f:
            task = utils.parse(json.load(f))
            task.update({
                'lead_id': lead['id'],
                'assigned_to': client.me()['id'],
                'due_date': _date
            })
            response = client.create_task(**task)
            assert all(False for k in task if k not in response), dict(response)

    @pytest.mark.flaky(reruns=3)
    def test_update_task(self, client, task):
        fields = {
            "is_complete": True
        }
        response = client.update_task(task['id'], fields)
        assert response['is_complete'], dict(response)

    @pytest.mark.flaky(reruns=3)
    def test_delete_task(self, client, task):
        response = client.delete_task(task['id'])
        assert response is True

    @pytest.mark.flaky(reruns=3)
    def test_get_tasks(self, client, task):
        response = client.get_tasks(assigned_to=client.me()['id'])
        assert task in response, list(response)

    def test_create_opportunity(self, client, lead):
        with open(os.path.join(FIXTURE_DIR, 'opportunity.json')) as f:
            opportunity = utils.parse(json.load(f))
            opportunity.update({
                'lead_id': lead['id'],
            })
            response = client.create_opportunity(opportunity)
            assert all(False for k in opportunity if k not in response), dict(response)

            client.delete_opportunity(response['id'])  # Clean up

    def test_update_opportunity(self, client, opportunity):
        fields = {
            "confidence": 75
        }
        response = client.update_opportunity(opportunity['id'], fields)
        assert response['confidence'] == 75, dict(response)

    def test_create_activity_call(self, client, lead):
        with open(os.path.join(FIXTURE_DIR, 'call.json')) as f:
            call = utils.parse(json.load(f))
            call.update({
                'lead_id': lead['id'],
            })
            response = client.create_activity_call(**call)
            assert all(False for k in call if k not in response), dict(response)

    def test_create_activity_email(self, client, lead):
        with open(os.path.join(FIXTURE_DIR, 'email.json')) as f:
            call = utils.parse(json.load(f))
            call.update({
                'lead_id': lead['id'],
            })
            response = client.create_activity_email(**call)
            assert all(False for k in call if k not in response), dict(response)

    def test_delete_activity_email(self, client, lead):
        with open(os.path.join(FIXTURE_DIR, 'email.json')) as f:
            email = utils.parse(json.load(f))
            email.update({
                'lead_id': lead['id'],
            })
            response = client.create_activity_email(**email)
            activity_id = response['id']

            response = client.delete_activity_email(activity_id)
            assert response is True

            assert list(client.get_activity_email(lead['id'])) == []

    def test_delete_activity_call(self, client, lead):
        with open(os.path.join(FIXTURE_DIR, 'call.json')) as f:
            call = utils.parse(json.load(f))
            call.update({
                'lead_id': lead['id'],
            })
            response = client.create_activity_call(**call)
            activity_id = response['id']

            response = client.delete_activity_call(activity_id)
            assert response is True

            assert list(client.get_activity_call(lead['id'])) == []

    def test_delete_activity_note(self, client, lead):
        note = {
            'note': 'this is a test note.',
            'lead_id': lead['id'],
        }
        response = client.create_activity_note(**note)
        activity_id = response['id']

        response = client.delete_activity_note(activity_id)
        assert response is True

        assert list(client.get_activity_note(lead['id'])) == []

    def test_get_event_logs(self, client, task):
        task_id = task['id']

        logs = client.get_event_logs(object_type='task.lead', action='created')
        logs = list(logs)
        assert len(logs) >= 1
        assert logs[0]['object_id'] == task_id
        assert all(log['action'] == 'created' for log in logs)

        iso_now = datetime.datetime.utcnow().isoformat()
        client.delete_task(task['id'])
        time.sleep(1)  # give closeio some time to create the event log on their system

        logs = client.get_event_logs(date_updated__gte=iso_now, object_type='task.lead',
                                     action='deleted')
        logs = list(logs)
        assert len(logs) == 1
        assert logs[0]['object_id'] == task_id
        assert logs[0]['action'] == 'deleted'

    def test_create_lead_export(self, client, random_string):
        export = client.create_lead_export(random_string)
        assert export

    def test_get_export(self, client, export):
        assert client.get_export(export['id'])

    def test_api_key(self, client):
        assert client.api_key()
