from closeio.signals import lead_update, lead_create
from django.db import models

from closeio.models import CloseIOBaseModel, closeio_field, closeio_custom_field
from django.dispatch import receiver


class CloseIOLead(CloseIOBaseModel):
    """
    `django.db.models.Model` representation of http://developer.close.io/#Leads
    """
    closeio_type = 'lead'

    name = closeio_field(
        models.CharField(max_length=100),
        'name')

    classified = closeio_custom_field(
        models.BooleanField(default=False),
        'classified')

    date_created = closeio_field(
        models.DateTimeField(auto_now_add=True),
        'date_created')

    def __unicode__(self):
        return self.name


@receiver([lead_update, lead_create])
def update_lead(sender, instance, **kwargs):
    lead = CloseIOLead.closeio.get(closeio_id=instance['id'])
    lead.closeio_obj = instance
    lead.load_fields_from_closeio(force=True)
    lead.save(update_closeio=False)