# -*- coding: utf-8 -*-

from __future__ import unicode_literals, print_function
import datetime
import json
import time

from closeio.closeio import CloseIO
from closeio import utils
import os
import pytest


API_KEY = os.environ.get('API_KEY')
TEST_DIR = os.path.dirname(__file__)
FIXTURE_DIR = os.path.join(TEST_DIR, 'fixtures')


class TestEndToEnd(object):
    @pytest.fixture
    def client(self):
        return CloseIO(API_KEY)

    @pytest.yield_fixture
    def lead(self, client):

        def wait_for_index(name):
            query = 'name:{}'.format(name)
            i = 0
            while not list(client.get_leads(query)):
                i += 1
                if i == 10:
                    raise RuntimeWarning("Lead wasn't indexed within 10 seconds")
                time.sleep(1)

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

    def test_create_lead(self, client):
        with open(os.path.join(FIXTURE_DIR, 'lead.json')) as f:
            lead = utils.parse(json.load(f))
            response = client.create_lead(lead)
            assert all(False for k in lead if k not in response), dict(response)

            client.delete_lead(response['id'])  # Clean up

    def test_get_lead(self, client, lead):
        response = client.get_lead(lead['id'])
        assert all(False for k in lead if k not in response), dict(response)

    @pytest.mark.flaky(reruns=3)
    def test_get_leads(self, client, lead):
        query = 'name:{name}'.format(**lead)
        response = client.get_leads(query=query)
        assert lead in response, list(response)

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

    def test_update_task(self, client, task):
        fields = {
            "is_complete": True
        }
        response = client.update_task(task['id'], fields)
        assert response['is_complete'], dict(response)

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
