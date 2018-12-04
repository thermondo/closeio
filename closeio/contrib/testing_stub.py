import copy
import itertools
import threading
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone

from dateutil.parser import parse

from closeio.utils import CloseIOError, Item, parse_response

threadlocal = threading.local()


class CloseIOStub(object):
    record_event_logs = False

    def __init__(self, user_emails=None):
        users = self._data('users', [])
        if user_emails:
            users.extend(user_emails)

    def _clear(self):
        varname = '_closeio_store'
        if hasattr(threadlocal, varname):
            delattr(threadlocal, varname)

    def _data(self, attr, default=None):
        varname = '_closeio_store'
        storage = getattr(threadlocal, varname, None)

        if storage is None:
            storage = {}
            setattr(threadlocal, varname, storage)

        if default is None:
            default = []

        if attr not in storage:
            storage[attr] = default

        return storage[attr]

    def _create_task_log(self, task):
        return {
            'id': 'ev_{}'.format(uuid.uuid4().hex),
            'object_type': 'task.lead',
            'object_id': task['id'],
            'lead_id': task['lead_id'],
            'user_id': task['assigned_to'],
            'date_updated': datetime.utcnow().isoformat(),
        }

    def _create_task_log_created(self, task):
        logs = self._data('event_logs', [])
        log = self._create_task_log(task)
        log.update({
            'action': 'created',
            'data': task,
            'previous_data': {},
        })
        logs.insert(0, log)

    def _create_task_log_deleted(self, task):
        logs = self._data('event_logs', [])
        log = self._create_task_log(task)
        log.update({
            'action': 'deleted',
            'data': {},
            'previous_data': task,
        })
        logs.insert(0, log)

    @contextmanager
    def record_logs(self):
        """Create event log data for certain operations.

        This context manager can be used to automatically create
        event logs when calling certain methods on the stub.
        Currently only event log data for task creation and deletion
        is supported.

        Example usage::
            with stub.record_logs():
                task = stub.create_task(lead_id='x', assigned_to='y', text='z')
                stub.delete_task(task_id=task['id'])
        """
        self.record_event_logs = True
        yield
        self.record_event_logs = False

    @parse_response
    def find_opportunity_status(self, label):
        opportunity_status = self._data('opportunity_status', [])

        for idx, st in enumerate(opportunity_status):
            if st['label'] == label:
                return self._get_opportunity_status(idx)

        raise CloseIOError()

    @parse_response
    def get_opportunity_statuss(self):
        opportunity_status = self._data('opportunity_status', [])

        return [
            self.find_opportunity_status(os['label'])
            for os in opportunity_status
        ]

    @parse_response
    def create_opportunity_status(self, label, type_):
        opportunity_status = self._data('opportunity_status', [])

        try:
            self.find_opportunity_status(label)
        except CloseIOError:
            pass
        else:
            raise CloseIOError()

        opportunity_status.append({
            'label': label,
            'type': type_,
        })

        return self.find_opportunity_status(label)

    @parse_response
    def create_lead_status(self, label):
        lead_status = self._data('lead_status', [])

        if label in lead_status:
            raise CloseIOError()

        else:
            lead_status.append(label)

            return self.find_lead_status(label)

    @parse_response
    def find_lead_status(self, label):
        lead_status = self._data('lead_status', [])

        if label not in lead_status:
            raise CloseIOError()

        return Item(dict(
            id=str(lead_status.index(label)),
            label=label,
        ))

    @parse_response
    def get_lead_statuss(self):
        lead_status = self._data('lead_status', [])

        return [
            self.find_lead_status(label)
            for label in lead_status
        ]

    @parse_response
    def delete_lead_status(self, status_id):
        lead_status = self._data('lead_status', [])

        status_id = int(status_id)

        if status_id >= len(lead_status):
            raise CloseIOError()

        del lead_status[status_id]

    @parse_response
    def create_lead(self, data):
        leads = self._data('leads', {})

        data = copy.deepcopy(data)
        if not data.get('id', ''):
            data['id'] = str(len(leads) + 1)

        data['organization_id'] = 'xx'
        data['date_created'] = datetime.now(timezone.utc)

        for idx, contact in enumerate(data.get('contacts', [])):
            if not contact.get('id'):
                data['contacts'][idx]['id'] = '{}/{}'.format(
                    data['id'],
                    idx,
                )

        leads[data['id']] = data
        return self.get_lead(data['id'])

    def _get_opportunity_status(self, ops_id):
        opportunity_status = self._data('opportunity_status', [])

        try:
            ops_id = int(ops_id)
        except (TypeError, ValueError):
            raise CloseIOError()

        if ops_id >= len(opportunity_status):
            raise CloseIOError()

        os = opportunity_status[ops_id]
        os['id'] = str(ops_id)

        return Item(os)

    def _get_opportunity(self, op_id):
        opportunities = self._data('opportunities', {})

        if op_id not in opportunities:
            raise CloseIOError()

        op = opportunities[op_id]
        status = self._get_opportunity_status(op['status_id'])
        op['status_label'] = status['label']
        op['status_type'] = status['type']

        return Item(op)

    @parse_response
    def get_lead(self, lead_id):
        leads = self._data('leads', {})
        opportunities = self._data('opportunities', {})

        if lead_id not in leads:
            raise CloseIOError()

        lead = Item(leads[lead_id])

        lead['opportunities'] = [
            self._get_opportunity(op_id)
            for op_id, opportunity in opportunities.items()
            if opportunity.get('lead_id', None) == lead_id
        ]

        lead['tasks'] = self.get_tasks(lead_id=lead_id)

        return lead

    @parse_response
    def get_lead_display_name_by_id(self, lead_id):
        lead = self.get_lead(lead_id)
        if 'display_name' in lead:
            return lead['display_name']
        else:
            return None

    @parse_response
    def get_leads(self, query=None, fields=None):
        leads = self._data('leads', {})

        if not query:
            for lead in leads.values():
                yield lead

        else:
            query = str(query)
            for lead_id, data in leads.items():
                for k, v in data.items():
                    if query in str(v):
                        yield Item(data)
                        break

    @parse_response
    def update_task(self, task_id, fields):
        tasks = self._data('tasks', {})

        for t in itertools.chain.from_iterable(tasks.values()):
            if t['id'] == task_id:
                task = t
                break
        else:
            raise CloseIOError()

        task.update(fields)
        return self._get_task(task_id)

    @parse_response
    def delete_task(self, task_id):
        tasks = self._data('tasks', {})

        for lead_id, tasks_list in tasks.items():
            for t in tasks_list:
                if t['id'] == task_id:
                    tasks[lead_id].remove(t)
                    if self.record_event_logs:
                        self._create_task_log_deleted(t)
                    return True
        raise CloseIOError()

    @parse_response
    def update_lead(self, lead_id, fields):
        leads = self._data('leads', {})

        if lead_id not in leads:
            raise CloseIOError()

        leads[lead_id].update(fields)

        return self.get_lead(lead_id)

    @parse_response
    def delete_lead(self, lead_id):
        leads = self._data('leads', {})

        if lead_id not in leads:
            raise CloseIOError()

        del leads[lead_id]

    @parse_response
    def create_activity_email(self, **kwargs):
        kwargs.setdefault('status', 'draft')
        emails = self._data('activity_emails', {})
        lead_id = kwargs.get('lead_id')
        email = kwargs
        if lead_id not in emails:
            emails[lead_id] = []
        template_id = email.get('template_id', None)
        if template_id:
            template = self.get_email_template(template_id)
            email['subject'] = template['subject']
            email['body_text'] = template['body']

        email['id'] = 'acti_{}'.format(uuid.uuid4().hex)
        emails[lead_id].append(email)
        return email

    @parse_response
    def create_activity_call(self, **kwargs):
        calls = self._data('activity_calls', {})
        call = kwargs
        call['id'] = 'acti_{}'.format(uuid.uuid4().hex)
        lead_id = call['lead_id']

        if lead_id not in calls:
            calls[lead_id] = []

        calls[lead_id].append(call)

    @parse_response
    def create_activity_note(self, **kwargs):
        notes = self._data('activity_notes', {})
        note = kwargs
        note['id'] = 'acti_{}'.format(uuid.uuid4().hex)
        lead_id = note['lead_id']

        if lead_id not in notes:
            notes[lead_id] = []

        notes[lead_id].append(note)

    @parse_response
    def delete_activity_email(self, activity_id):
        emails = self._data('activity_emails', {})

        for lead_id, email_list in emails.items():
            for email in email_list:
                if email['id'] == activity_id:
                    emails[lead_id].remove(email)
                    return True
        raise CloseIOError()

    @parse_response
    def delete_activity_call(self, activity_id):
        calls = self._data('activity_calls', {})

        for lead_id, call_list in calls.items():
            for call in call_list:
                if call['id'] == activity_id:
                    calls[lead_id].remove(call)
                    return True
        raise CloseIOError()

    @parse_response
    def delete_activity_note(self, activity_id):
        notes = self._data('activity_notes', {})

        for lead_id, note_list in notes.items():
            for note in note_list:
                if note['id'] == activity_id:
                    notes[lead_id].remove(note)
                    return True
        raise CloseIOError()

    @parse_response
    def create_task(self, lead_id, assigned_to, text, due_date=None,
                    is_complete=False):
        tasks = self._data('tasks', {})

        if lead_id not in tasks:
            tasks[lead_id] = []

        task = {
            'id': 'task_{}'.format(uuid.uuid4().hex),
            'lead_id': lead_id,
            'assigned_to': str(assigned_to),
            'text': text,
            'due_date': due_date.isoformat() if due_date else None,
            'is_complete': is_complete,
            'date_created': datetime.now(timezone.utc).isoformat(),
            'date_updated': datetime.now(timezone.utc).isoformat(),
        }

        tasks[lead_id].append(task)

        if self.record_event_logs:
            self._create_task_log_created(task)

        return task

    def _get_task(self, task_id):
        tasks = self._data('tasks', {})
        leads = self._data('leads', {})

        for task in itertools.chain.from_iterable(tasks.values()):
            if task['id'] == task_id:
                if 'lead_id' in task:
                    lead_id = task.get('lead_id')
                    lead = leads.get(lead_id, {})
                    if lead:
                        task['lead_name'] = lead.get('name', '')

                # task['assigned_to'] = binary_type(task['assigned_to'])
                return task

        raise CloseIOError()

    @parse_response
    def get_tasks(self, lead_id=None, assigned_to=None, is_complete=None):
        tasks = self._data('tasks', {})

        if lead_id is not None:
            tasks = tasks.get(lead_id, [])
        else:
            tasks = itertools.chain.from_iterable(tasks.values())

        if assigned_to is not None:
            tasks = [
                self._get_task(t['id'])
                for t in tasks
                if t['assigned_to'] == assigned_to
            ]

        if is_complete is not None:
            tasks = [
                self._get_task(t['id'])
                for t in tasks
                if t['is_complete'] == is_complete
            ]

        return tasks

    get_tasks_cached = get_tasks

    @parse_response
    def get_activity_email(self, lead_id):
        emails = self._data('activity_emails', {})

        if lead_id not in emails:
            return []

        else:
            return emails[lead_id]

    @parse_response
    def get_activity_call(self, lead_id):
        calls = self._data('activity_calls', {})

        if lead_id not in calls:
            return []

        else:
            return calls[lead_id]

    @parse_response
    def get_activity_note(self, lead_id):
        notes = self._data('activity_notes', {})

        if lead_id not in notes:
            return []

        else:
            return notes[lead_id]

    @parse_response
    def get_email_templates(self):
        email_templates = self._data('email_templates', [])

        return [
            self.get_email_template(id_)
            for id_, data in enumerate(email_templates)
        ]

    @parse_response
    def get_email_template(self, template_id):
        email_templates = self._data('email_templates', [])

        template_id = int(template_id)

        if template_id >= len(email_templates):
            raise CloseIOError()

        data = copy.deepcopy(email_templates[template_id])
        data['id'] = str(template_id)

        return Item(data)

    @parse_response
    def create_email_template(self, fields):
        email_templates = self._data('email_templates', [])
        email_templates.append(fields)

        return self.get_email_template(len(email_templates) - 1)

    @parse_response
    def delete_email_template(self, template_id):
        email_templates = self._data('email_templates', [])

        template_id = int(template_id)

        if template_id >= len(email_templates):
            raise CloseIOError()

        del email_templates[template_id]

    @parse_response
    def get_organization_users(self, organization_id=None):
        users = self._data('users', [])

        return [
            self.get_user(user_id)
            for user_id, email in enumerate(users)
        ]

    @parse_response
    def me(self):
        return self.get_user(0)

    @parse_response
    def get_user(self, user_id):
        users = self._data('users', [])

        user_id = int(user_id)

        if user_id >= len(users):
            raise CloseIOError()

        email = users[user_id]

        return Item({
            'id': str(user_id),
            'email': email,
            'first_name': 'first {}'.format(user_id),
            'last_name': 'last {}'.format(user_id),
        })

    @parse_response
    def user_exists(self, email):
        users = self._data('users', [])

        return email in users

    @parse_response
    def find_user_id(self, email):
        users = self._data('users', [])

        if email in users:
            return str(users.index(email))
        else:
            raise CloseIOError()

    @parse_response
    def create_opportunity(self, data):
        opportunities = self._data('opportunities', {})
        opportunity_keys = self._data('opportunity_keys', {})

        data = copy.deepcopy(data)
        if not data.get('id', ''):
            data['id'] = str(len(opportunity_keys) + 1)

        data['organization_id'] = 'xx'
        data['date_created'] = datetime.now(timezone.utc)

        opportunities[data['id']] = data
        opportunity_keys[data['id']] = data

        return self._get_opportunity(data['id'])

    @parse_response
    def update_opportunity(self, opportunity_id, fields):
        opportunities = self._data('opportunities', {})

        if opportunity_id not in opportunities:
            raise CloseIOError()

        opportunities[opportunity_id].update(fields)

        return self._get_opportunity(opportunity_id)

    @parse_response
    def delete_opportunity(self, opportunity_id):
        opportunities = self._data('opportunities', {})

        if opportunity_id not in opportunities:
            raise CloseIOError()

        del opportunities[opportunity_id]

    @parse_response
    def get_event_logs(self, **kwargs):
        logs = self._data('event_logs', [])

        for param in ['action', 'object_type', 'object_id', 'lead_id', 'user_id']:
            if param in kwargs:
                logs = [log for log in logs if log[param] == kwargs[param]]

        if 'date_updated__gt' in kwargs:
            date_updated = parse(kwargs['date_updated__gt'])
            logs = [log for log in logs if parse(log['date_updated']) > date_updated]

        if 'date_updated__gte' in kwargs:
            date_updated = parse(kwargs['date_updated__gte'])
            logs = [log for log in logs if parse(log['date_updated']) >= date_updated]

        if 'date_updated__lt' in kwargs:
            date_updated = parse(kwargs['date_updated__lt'])
            logs = [log for log in logs if parse(log['date_updated']) < date_updated]

        if 'date_updated__lte' in kwargs:
            date_updated = parse(kwargs['date_updated__lte'])
            logs = [log for log in logs if parse(log['date_updated']) <= date_updated]

        if '_limit' in kwargs:
            logs = logs[:kwargs['_limit']]

        return logs

    @parse_response
    def get_export(self, id):
        exports = self._data('exports', [])
        export_id = int(id)

        export = next((item for item in exports if item["id"] == export_id))

        if not export:
            raise CloseIOError()
        return export

    @parse_response
    def create_lead_export(self, query='*', format='json', fields=(),
                           include_activities=False, include_smart_fields=False):
        exports = self._data('exports', [])
        export = dict(
            format=format,
            status='done',
            download_url='https://example.com',
            type='leads',
            query=query,
        )

        if include_activities:
            export['include_activities'] = include_activities

        if include_smart_fields:
            export['include_smart_fields'] = include_smart_fields

        if fields:
            export['fields'] = list(fields)

        export['id'] = len(exports) + 1
        exports.append(export)
        return self.get_export(export['id'])

    @parse_response
    def api_key(self):
        return Item({
            'has_more': False,
            'data': [{
                'date_updated': datetime.now(timezone.utc),
                'date_created': datetime.now(timezone.utc),
                'user_id': self.get_user(0)['id'],
                'organization_id': 'xx',
                'key': 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx',
            }],
        })
