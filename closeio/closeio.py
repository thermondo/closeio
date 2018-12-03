import logging

import requests
import slumber
from requests.adapters import HTTPAdapter

from closeio.exceptions import CloseIOError
from closeio.utils import (
    DummyCookieJar, convert, handle_errors, paginate, paginate_via_cursor,
    parse_response
)

logger = logging.getLogger(__name__)


class CloseIO(object):
    def __init__(self, api_key, max_retries=5):
        self._api_key = api_key
        self._api_cache = None
        self._max_retries = max_retries

    @property
    def _api(self):
        if self._api_cache:
            return self._api_cache

        _session = requests.Session()
        _session.cookies = DummyCookieJar()
        _session.auth = (self._api_key, "")
        _session.verify = True
        _session.mount('http://', HTTPAdapter(max_retries=self._max_retries))
        _session.mount('https://', HTTPAdapter(max_retries=self._max_retries))

        self._api_cache = slumber.API(
            'https://app.close.io/api/v1/',
            session=_session
        )

        return self._api_cache

    # undocumented, hidden API - use with care
    @parse_response
    @handle_errors
    def api_key(self):
        return self._api.api_key.get()

    @parse_response
    @handle_errors
    def me(self):
        return self._api.me.get()

    @parse_response
    @handle_errors
    def get_lead(self, lead_id):
        return self._api.lead(lead_id).get()

    @parse_response
    @handle_errors
    def get_contact(self, contact_id):
        return self._api.contact(contact_id).get()

    @parse_response
    @handle_errors
    def delete_lead(self, lead_id):
        return self._api.lead(lead_id).delete()

    @parse_response
    @handle_errors
    def delete_email_template(self, template_id):
        return self._api.email_template(template_id).delete()

    @parse_response
    @handle_errors
    def create_email_template(self, fields):
        fields = convert(fields)
        return self._api.email_template.post(fields)

    @parse_response
    @handle_errors
    def get_email_templates(self):
        return paginate(
            self._api.email_template.get
        )

    @parse_response
    @handle_errors
    def get_email_template(self, template_id):
        return self._api.email_template(template_id).get()

    @parse_response
    @handle_errors
    def find_email_template(self, name):
        for template in self.get_email_templates():
            if template.name == name:
                return template

        raise CloseIOError(
            "EMail template with nane \"{}\" could not be found!".format(name))

    @parse_response
    @handle_errors
    def get_opportunity_statuss(self):
        return paginate(self._api.status.opportunity.get)

    @parse_response
    @handle_errors
    def find_opportunity_status(self, label):
        for status in self.get_opportunity_statuss():
            if status.label == label:
                return status

        raise CloseIOError(
            "Opportunity-Status with label \"{}\" "
            "could not be found!".format(label))

    @parse_response
    @handle_errors
    def find_opportunity_status_in_organization(self, organization_id, label):
        org = self.get_organization(organization_id)

        for status in org['opportunity_statuses']:
            if status['label'] == label:
                return status

        raise CloseIOError(
            "Opportunity-Status with label \"{}\" "
            "could not be found!".format(label))

    @parse_response
    @handle_errors
    def get_lead_statuss(self):
        return paginate(self._api.status.lead.get)

    @parse_response
    @handle_errors
    def find_lead_status(self, label):
        for status in self.get_lead_statuss():
            if status.label == label:
                return status

        raise CloseIOError(
            "Lead-Status with label \"" + label + "\" could not be found!")

    @parse_response
    @handle_errors
    def find_user(self, full_name):
        me = self._api.me.get()
        for membership in me['memberships']:
            org_id = membership['organization_id']

            org = self._api.organization(org_id).get()

            for user in org['memberships']:
                if user['user_full_name'] == full_name:
                    return self.get_organization_user(org_id, user['user_id'])

        raise CloseIOError(
            "User with full-name \"" + full_name + "\" could not be found!")

    @parse_response
    @handle_errors
    def find_user_id(self, email):
        ids = set()
        email = email.strip().lower()

        me = self._api.me.get()
        for my_membership in me['memberships']:
            organization_id = my_membership['organization_id']
            org = self._api.organization(organization_id).get()
            for membership in org['memberships']:
                membership_mail = membership['user_email']
                membership_mail = membership_mail.strip().lower()

                if membership_mail == email:
                    ids.add(membership['user_id'])

        if not ids:
            raise CloseIOError("user with email {} not found".format(email))

        elif len(ids) > 1:
            raise CloseIOError(
                "multiple users with email {} found".format(email))

        else:
            return ids.pop()

    @parse_response
    @handle_errors
    def update_lead(self, lead_id, fields):
        fields = convert(fields)
        return self._api.lead(lead_id).put(fields)

    @parse_response
    @handle_errors
    def create_lead(self, fields):
        fields = convert(fields)
        return self._api.lead.post(fields)

    @parse_response
    @handle_errors
    def create_opportunity(self, fields):
        fields = convert(fields)
        return self._api.opportunity.post(fields)

    @parse_response
    @handle_errors
    def update_opportunity(self, opportunity_id, fields):
        fields = convert(fields)
        return self._api.opportunity(opportunity_id).put(fields)

    @parse_response
    @handle_errors
    def create_task(self, lead_id, assigned_to, text, due_date=None,
                    is_complete=False):

        return self._api.task.post({
            "lead_id": lead_id,
            "assigned_to": assigned_to,
            "text": text,
            "due_date": due_date.isoformat() if due_date else None,
            "is_complete": is_complete
        })

    @parse_response
    @handle_errors
    def update_task(self, task_id, fields):
        fields = convert(fields)
        return self._api.task(task_id).put(fields)

    @parse_response
    @handle_errors
    def delete_task(self, task_id):
        return self._api.task(task_id).delete()

    @parse_response
    @handle_errors
    def get_tasks(self, **kwargs):
        kwargs = convert(kwargs)
        kwargs.update({
            k: 'true' if v else 'false'
            for k, v in kwargs.items()
            if isinstance(v, bool)
        })

        kwargs.setdefault('_order_by', '-date_created')

        return paginate(
            self._api.task.get,
            **kwargs
        )

    @parse_response
    @handle_errors
    def create_opportunity_status(self, label, type_):
        if type_ not in ('active', 'won', 'lost'):
            raise CloseIOError("invalid opportunity status type {}".format(type_))

        return self._api.status.opportunity.post({
            'label': label,
            'type': type_,
        })

    @parse_response
    @handle_errors
    def delete_opportunity_status(self, status_id):
        return self._api.status.opportunity(status_id).delete()

    @parse_response
    @handle_errors
    def create_lead_status(self, label):
        return self._api.status.lead.post({
            'label': label,
        })

    @parse_response
    @handle_errors
    def delete_lead_status(self, status_id):
        return self._api.status.lead(status_id).delete()

    @parse_response
    @handle_errors
    def create_activity_note(self, lead_id, note):
        return self._api.activity.note.post({
            'lead_id': lead_id,
            'note': note,
        })

    @parse_response
    @handle_errors
    def create_activity_email(self, **kwargs):
        kwargs.setdefault('status', 'draft')
        return self._api.activity.email.post(kwargs)

    @parse_response
    @handle_errors
    def create_activity_call(self, **kwargs):
        return self._api.activity.call.post(kwargs)

    @parse_response
    @handle_errors
    def get_activity_email(self, lead_id):
        return paginate(
            self._api.activity.email.get,
            lead_id=lead_id,
        )

    @parse_response
    @handle_errors
    def get_activity_call(self, lead_id):
        return paginate(
            self._api.activity.call.get,
            lead_id=lead_id,
        )

    @parse_response
    @handle_errors
    def get_activity_note(self, lead_id):
        return paginate(
            self._api.activity.note.get,
            lead_id=lead_id,
        )

    @parse_response
    @handle_errors
    def get_activities(self, **kwargs):
        fields = kwargs.pop('fields', None)
        if fields:
            kwargs['_fields'] = ','.join(fields)

        return paginate(
            self._api.activity.get,
            **kwargs)

    @parse_response
    @handle_errors
    def delete_activity_email(self, activity_id):
        return self._api.activity.email(activity_id).delete()

    @parse_response
    @handle_errors
    def delete_activity_call(self, activity_id):
        return self._api.activity.call(activity_id).delete()

    @parse_response
    @handle_errors
    def delete_activity_note(self, activity_id):
        return self._api.activity.note(activity_id).delete()

    @parse_response
    @handle_errors
    def get_opportunities(self):
        return paginate(
            self._api.opportunity.get,
        )

    @parse_response
    @handle_errors
    def delete_opportunity(self, opportunity_id):
        return self._api.opportunity(opportunity_id).delete()

    @parse_response
    @handle_errors
    def get_leads(self, query=None, fields=None):
        args = {}
        if query:
            args['query'] = query

        if fields:
            args['_fields'] = ','.join(fields)

        return paginate(
            self._api.lead.get,
            **args)

    @parse_response
    @handle_errors
    def get_user(self, user_id):
        return self._api.user(user_id).get()

    @parse_response
    @handle_errors
    def get_organization(self, organization_id):
        return self._api.organization(organization_id).get()

    @parse_response
    @handle_errors
    def get_organization_users(self, organization_id=None):
        if not organization_id:
            me = self._api.me.get()
            for mem in me['memberships']:
                organization_id = mem['organization_id']
                break

        users = []

        org = self._api.organization(organization_id).get()
        for membership in org['memberships']:
            uid = membership['user_id']
            user = self._api.user(uid).get()

            user.update({
                key[5:]: value
                for key, value in membership.items()
                if key.startswith('user_')
            })

            users.append(user)

        return users

    @parse_response
    @handle_errors
    def get_organization_user(self, organization_id, user_id):
        user = self._api.user(user_id).get()

        org = self._api.organization(organization_id).get()
        for membership in org['memberships']:
            if membership['user_id'] == user_id:
                user.update({
                    key[5:]: value
                    for key, value in membership.items()
                    if key.startswith('user_')
                })
                break

        else:
            raise CloseIOError(
                "User {} not found in "
                "organization {}".format(user_id, organization_id))

        return user

    @parse_response
    @handle_errors
    def get_lead_display_name_by_id(self, lead_id):
        lead = self.get_lead(lead_id)
        if 'display_name' in lead:
            return lead['display_name']
        else:
            return None

    @parse_response
    @handle_errors
    def get_lead_display_name(self, query):
        possible_leads = list(self.get_leads(
            query=query
        ))

        if len(possible_leads) > 0:
            if len(possible_leads) > 1:
                logger.warning(
                    "got {len} possible leads for query {query}. "
                    "Using the first one. ".format(
                        len=len(possible_leads),
                        query=query,
                    ))

            display_name = possible_leads[0].display_name
            return display_name

        return ""

    @parse_response
    @handle_errors
    def custom_field_values(self, fieldname):
        leads = self.get_leads(
            query='custom.{}:*'.format(fieldname),
            fields=['custom']
        )

        return {
            lead['custom'][fieldname]
            for lead in leads
        }

    @parse_response
    @handle_errors
    def user_exists(self, email):
        try:
            self.find_user_id(email)
            return True
        except Exception:
            return False

    @parse_response
    @handle_errors
    def create_lead_export(self, query='*', format='json', fields=(),
                           include_activities=False, include_smart_fields=False):

        args = dict(
            format=format,
            type='leads',
            query=query,
        )

        if include_activities:
            args['include_activities'] = include_activities

        if include_smart_fields:
            args['include_smart_fields'] = include_smart_fields

        if fields:
            args['fields'] = list(fields)

        return self._api.export.lead.post(args)

    @parse_response
    @handle_errors
    def get_export(self, id):
        return self._api.export(id).get()

    @parse_response
    @handle_errors
    def get_event_logs(self, **kwargs):
        return paginate_via_cursor(
            self._api.event.get,
            **kwargs
        )
