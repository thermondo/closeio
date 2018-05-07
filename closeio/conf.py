"""
Additional settings for Django.
``CLOSEIO_ORGANIZATION_ID`` (required):
    Each Closeio webhook contains organization id, pointing the origin of the request.
    This can be used as an extra protection and distinguish between staging and production orgs.
    .. note:: See https://developer.close.io/#organizations
"""
from appconf import AppConf
from django.conf import settings  # NoQA

__all__ = ('settings',)


class CloseioConf(AppConf):
    class Meta:
        prefix = 'CLOSEIO'
        required = ['ORGANIZATION_ID']
