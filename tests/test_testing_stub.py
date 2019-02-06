import datetime

from closeio.contrib.testing_stub import CloseIOStub


class TestEventLogs:
    def test_record_and_retrieve_event_logs(self):
        client = CloseIOStub()

        task1 = client.create_task(lead_id='x1', assigned_to='y1', text='z1')
        client.delete_task(task_id=task1['id'])

        assert list(client.get_event_logs()) == []

        with client.record_logs():
            task2 = client.create_task(lead_id='x2', assigned_to='y2', text='z2')
            client.delete_task(task_id=task2['id'])
            pause = datetime.datetime.utcnow().isoformat()
            task3 = client.create_task(lead_id='x3', assigned_to='y3', text='z3')
            client.delete_task(task_id=task3['id'])

        logs = list(client.get_event_logs())
        assert len(logs) == 4
        assert logs[0]['action'] == 'deleted'
        assert logs[0]['object_id'] == task3['id']
        assert logs[1]['action'] == 'created'
        assert logs[1]['object_id'] == task3['id']
        assert logs[2]['action'] == 'deleted'
        assert logs[2]['object_id'] == task2['id']
        assert logs[3]['action'] == 'created'
        assert logs[3]['object_id'] == task2['id']

        logs = list(client.get_event_logs(action='created'))
        assert len(logs) == 2

        logs = list(client.get_event_logs(action='deleted'))
        assert len(logs) == 2

        logs = list(client.get_event_logs(object_type='task.lead'))
        assert len(logs) == 4
        assert logs[0]['object_id'] == task3['id']
        assert logs[1]['object_id'] == task3['id']
        assert logs[2]['object_id'] == task2['id']
        assert logs[3]['object_id'] == task2['id']

        logs = list(client.get_event_logs(object_type='task.lead', date_updated__gt=pause))
        assert len(logs) == 2
        assert logs[0]['object_id'] == task3['id']
        assert logs[1]['object_id'] == task3['id']


class TestCreateActivities:
    def test_create_activity_note(self):
        client = CloseIOStub()

        kwargs = {
            'note': 'this is a test note.',
            'lead_id': 'lead_s6vHFTK1TSRoH6otXOexWDO9jM4xyb1kELHDoU7Fdsp',
        }
        response = client.create_activity_note(**kwargs)
        assert response['id'].startswith('acti_')

    def test_create_activity_call(self):
        client = CloseIOStub()

        kwargs = {
            'direction': 'outbound',
            'status': 'completed',
            'note': 'call notes go here',
            'duration': 153,
            'lead_id': 'lead_s6vHFTK1TSRoH6otXOexWDO9jM4xyb1kELHDoU7Fdsp',
        }
        response = client.create_activity_call(**kwargs)
        assert response['id'].startswith('acti_')

    def test_create_activity_email(self):
        client = CloseIOStub()

        kwargs = {
            'subject': 'test subject',
            'sender': 'sender@example.com',
            'to': ['recipient+1@example.com'],
            'bcc': [],
            'cc': [],
            'status': 'draft',
            'body_text': 'test',
            'body_html': 'test',
            'attachments': [],
            'template_id': None,
            'lead_id': 'lead_s6vHFTK1TSRoH6otXOexWDO9jM4xyb1kELHDoU7Fdsp',
        }
        response = client.create_activity_email(**kwargs)
        assert response['id'].startswith('acti_')
