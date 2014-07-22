import threading
import copy

from closeio.utils import Item, CloseIOError

threadlocal = threading.local()


class CloseIOStub(object):
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

        leads[data['id']] = data

        return Item(data)

    def get_lead(self, lead_id):
        leads = self._data('leads', {})

        if lead_id not in leads:
            raise CloseIOError()

        return Item(leads[lead_id])

    def update_lead(self, lead_id, fields):
        leads = self._data('leads', {})

        if lead_id not in leads:
            raise CloseIOError()

        leads[lead_id].update(fields)

        return Item(leads[lead_id])

    def create_activity_note(self, lead_id, note):
        notes = self._data('activity_notes', {})

        if lead_id not in notes:
            notes[lead_id] = []

        notes[lead_id].append(note)
