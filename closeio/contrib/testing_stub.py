import threading
import copy
import itertools
from datetime import datetime

from closeio.utils import Item, CloseIOError

threadlocal = threading.local()


class CloseIOStub(object):
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

    def find_opportunity_status(self, label):
        opportunity_status = self._data('opportunity_status', [])

        for st in opportunity_status:
            if st['label'] == label:
                return Item(st)

        raise CloseIOError()

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

    def create_lead_status(self, label):
        lead_status = self._data('lead_status', [])

        if label in lead_status:
            raise CloseIOError()

        else:
            lead_status.append(label)

            return self.find_lead_status(label)

    def find_lead_status(self, label):
        lead_status = self._data('lead_status', [])

        if label not in lead_status:
            raise CloseIOError()

        return Item(dict(
            id=unicode(lead_status.index(label)),
            label=label,
        ))

    def delete_lead_status(self, status_id):
        lead_status = self._data('lead_status', [])

        status_id = int(status_id)

        if status_id >= len(lead_status):
            raise CloseIOError()

        del lead_status[status_id]

    def create_lead(self, data):
        leads = self._data('leads', {})

        data = copy.deepcopy(data)
        if not data.get('id', ''):
            data['id'] = str(len(leads) + 1)

        data['organization_id'] = 'xx'
        data['date_created'] = datetime.utcnow()

        for idx, contact in enumerate(data.get('contacts', [])):
            if not contact.get('id'):
                data['contacts'][idx]['id'] = '{}/{}'.format(
                    data['id'],
                    idx,
                )

        leads[data['id']] = data
        return self.get_lead(data['id'])

    def get_lead(self, lead_id):
        leads = self._data('leads', {})
        opportunities = self._data('opportunities', {})

        if lead_id not in leads:
            raise CloseIOError()

        lead = Item(leads[lead_id])

        lead['opportunities'] = [
            opportunity
            for op_id, opportunity in opportunities.items()
            if opportunity.get('lead_id', None) == lead_id
        ]

        return lead

    def get_lead_display_name_by_id(self, lead_id):
        lead = self.get_lead(lead_id)
        if 'display_name' in lead:
            return lead['display_name']
        else:
            return None

    def get_leads(self, query=None, fields=None):
        leads = self._data('leads', {})

        if not query:
            for lead in leads.values():
                yield lead

        else:
            query = unicode(query)
            for lead_id, data in leads.items():
                for k, v in data.items():
                    if query in unicode(v):
                        yield Item(data)
                        break

    def update_lead(self, lead_id, fields):
        leads = self._data('leads', {})

        if lead_id not in leads:
            raise CloseIOError()

        leads[lead_id].update(fields)

        return self.get_lead(lead_id)

    def delete_lead(self, lead_id):
        leads = self._data('leads', {})

        if lead_id not in leads:
            raise CloseIOError()

        del leads[lead_id]

    def create_activity_email(self, lead_id, **kwargs):
        kwargs.setdefault('status', 'draft')

        emails = self._data('activity_emails', {})

        if lead_id not in emails:
            emails[lead_id] = []

        emails[lead_id].append(kwargs)

    def create_activity_note(self, lead_id, note):
        notes = self._data('activity_notes', {})

        if lead_id not in notes:
            notes[lead_id] = []

        notes[lead_id].append(note)

    def create_task(self, lead_id, assigned_to, text, due_date=None,
                    is_complete=False):
        tasks = self._data('tasks', {})

        if lead_id not in tasks:
            tasks[lead_id] = []

        tasks[lead_id].append({
            "lead_id": lead_id,
            "assigned_to": str(assigned_to),
            "text": text,
            "due_date": due_date.date().isoformat() if due_date else None,
            "is_complete": is_complete
        })

    def get_tasks(self, lead_id=None, assigned_to=None, is_complete=None):
        tasks = self._data('tasks', {})

        if lead_id is not None:
            tasks = tasks[lead_id]
        else:
            tasks = itertools.chain.from_iterable(tasks.values())

        if assigned_to is not None:
            tasks = [
                t
                for t in tasks
                if t['assigned_to'] == assigned_to
            ]

        if is_complete is not None:
            tasks = [
                t
                for t in tasks
                if t['is_complete'] == is_complete
            ]

        return tasks

    get_tasks_cached = get_tasks

    def get_activity_email(self, lead_id):
        emails = self._data('activity_emails', {})

        if lead_id not in emails:
            return []

        else:
            return emails[lead_id]

    def get_activity_note(self, lead_id):
        notes = self._data('activity_notes', {})

        if lead_id not in notes:
            return []

        else:
            return notes[lead_id]

    def get_email_templates(self):
        email_templates = self._data('email_templates', [])

        return [
            self.get_email_template(id_)
            for id_, data in enumerate(email_templates)
        ]

    def get_email_template(self, template_id):
        email_templates = self._data('email_templates', [])

        template_id = int(template_id)

        if template_id >= len(email_templates):
            raise CloseIOError()

        data = copy.deepcopy(email_templates[template_id])
        data['id'] = str(template_id)

        return Item(data)

    def create_email_template(self, fields):
        email_templates = self._data('email_templates', [])
        email_templates.append(fields)

        return self.get_email_template(len(email_templates) - 1)

    def delete_email_template(self, template_id):
        email_templates = self._data('email_templates', [])

        template_id = int(template_id)

        if template_id >= len(email_templates):
            raise CloseIOError()

        del email_templates[template_id]

    def get_organization_users(self, organization_id):
        users = self._data('users', [])

        return [
            self.get_user(user_id)
            for user_id, email in enumerate(users)
        ]

    def get_user(self, user_id):
        users = self._data('users', [])

        user_id = int(user_id)

        if user_id >= len(users):
            raise CloseIOError()

        return Item({
            'id': user_id,
            'email': users[user_id]
        })

    def user_exists(self, email):
        users = self._data('users', [])

        return email in users

    def find_user_id(self, email):
        users = self._data('users', [])

        if email in users:
            return users.index(email)
        else:
            raise CloseIOError()

    def create_opportunity(self, data):
        opportunities = self._data('opportunities', {})

        data = copy.deepcopy(data)
        if not data.get('id', ''):
            data['id'] = str(len(opportunities) + 1)

        data['organization_id'] = 'xx'
        data['date_created'] = datetime.utcnow()

        opportunities[data['id']] = data

        return Item(data)

    def update_opportunity(self, opportunity_id, fields):
        opportunities = self._data('opportunities', {})

        if opportunity_id not in opportunities:
            raise CloseIOError()

        opportunities[opportunity_id].update(fields)

        return Item(opportunities[opportunity_id])

    def delete_opportunity(self, opportunity_id):
        opportunities = self._data('opportunities', {})

        if opportunity_id not in opportunities:
            raise CloseIOError()

        del opportunities[opportunity_id]
