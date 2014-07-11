from closeio import CloseIO, utils

import json
import copy

from django.conf import settings
from django.core.urlresolvers import reverse
from django.test import TestCase

from .models import CloseIOLead

INIT_LEAD = {
    u'addresses': [],
    u'contacts': [],
    u'custom': {
        u'SHIELD Level': u'Avenger'
    },
    u'description': u'',
    u'name': u'Tony Stark',
    u'opportunities': [],
    u'tasks': [],
}


class CloseIOBaseTest(TestCase):

    def setUp(self):
        self.api = CloseIO(settings.CLOSEIO_API_KEY)
        self.lead = self.api.create_lead(INIT_LEAD)
        self.lead_id = self.lead['id']

    def tearDown(self):
        self.api.delete_lead(self.lead_id)


class TestCloseIOModel(CloseIOBaseTest):

    def test_manager_get(self):
        """ Tests the `CloseIOManager`'s get method. """
        lead = CloseIOLead.closeio.get(closeio_id=self.lead_id)
        self.assertFalse(lead.pk)

    def test_manager_all(self):
        """ Tests the `CloseIOManager`'s all method. """
        leads = CloseIOLead.closeio.all()
        self.assertGreaterEqual(len(list(leads)), 1)
        for lead in leads:
            self.assertIsInstance(lead, CloseIOLead)

    def test_model_saveing(self):
        """ Tests the models save method. """
        lead = CloseIOLead.closeio.get(closeio_id=self.lead_id)
        lead.save()
        self.assertEqual(lead.pk, 1)

    def test_model_reloading(self):
        """ Tests receiving objects through both managers. """
        lead = CloseIOLead.closeio.get(closeio_id=self.lead_id)
        lead.save()

        lead_reloaded_obj = CloseIOLead.objects.get(closeio_id=self.lead_id)
        self.assertEqual(lead_reloaded_obj.pk, 1)

        lead_reloaded_cio = CloseIOLead.closeio.get(closeio_id=self.lead_id)
        self.assertEqual(lead_reloaded_cio.pk, 1)

    def test_closeio_field(self):
        """ Tests the `closeio_field` field decorator. """
        lead = CloseIOLead.closeio.get(closeio_id=self.lead_id)

        self.assertEqual(lead.name, 'Tony Stark')

        lead.name = 'Iron Man'
        lead.save()

        lead_from_api = self.api.get_lead(self.lead_id)

        self.assertEqual(lead.name, lead_from_api['name'])

    def test_custom_field(self):
        """ Tests the `closeio_custom_field` field decorator. """
        lead = CloseIOLead.closeio.get(closeio_id=self.lead_id)
        lead.classified = True
        lead.save()

        lead_from_api = self.api.get_lead(self.lead_id)

        self.assertEqual(lead_from_api['custom']['classified'], 'ja')

    def test_do_not_update_closeio(self):
        """ Tests the `update_closeio` argument of the `CloseIOBaseModel`'s save method. """
        lead = CloseIOLead.closeio.get(closeio_id=self.lead_id)

        self.assertEqual(lead.name, 'Tony Stark')

        lead.name = 'Iron Man'
        lead.save(update_closeio=False)

        lead_from_api = self.api.get_lead(self.lead_id)

        self.assertEqual(lead_from_api['name'], 'Tony Stark')

    def test_lazy_loading(self):
        """ Tests lazy loading of closeio fields. """
        lead = CloseIOLead.closeio.get(closeio_id=self.lead_id)
        lead.save()

        lead_reloaded = CloseIOLead.objects.get(pk=lead.pk)
        self.assertIsNone(lead_reloaded._closeio_obj)
        self.assertEqual(lead_reloaded.custom['SHIELD Level'], u'Avenger')
        self.assertIsNotNone(lead_reloaded._closeio_obj)


class TestCloseIOHook(CloseIOBaseTest):

    def test_update_hook(self):
        lead = copy.copy(self.lead)
        lead['name'] = 'Iron Man'
        data = {
            'model': 'lead',
            'event': 'update',
            'data': utils.convert(lead),
        }
        response = self.client.post(reverse('closeio_webhook'), data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 200)

        lead_from_db = CloseIOLead.objects.get(closeio_id=self.lead_id)
        self.assertEqual(lead_from_db.name, 'Iron Man')

    def test_invalid_request(self):
        data = {
            'foo': 'bar',
        }
        response = self.client.post(reverse('closeio_webhook'), data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_invalid_json(self):
        data = 'foo, bar'
        response = self.client.post(reverse('closeio_webhook'), data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 400)