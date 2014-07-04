#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime

from django.db.models import Field, BooleanField, NullBooleanField


def closeio_field(instance, field_name, converter=None):
    """
    CloseIO pseudo decorator for instances of `django.db.models.Field`.
    The decorator attaches the corresponding CloseIO field name
    as well as back/forth converter.
    :param instance: django.db.models.Field
    :param field_name: tuple
    :param converter: tuple
    :return: django.db.models.Field
    """
    if not isinstance(instance, Field):
        raise ValueError("%s must ob of type %s" % (instance.__class, Field))
    instance.closeio_field_name = (field_name, ) if not isinstance(field_name, tuple) else field_name
    if not converter:
        if isinstance(instance, BooleanField):
            converter = BOOLEAN_CONVERTER
        elif isinstance(instance, NullBooleanField):
            converter = NULL_BOOLEAN_CONVERTER
    instance.closeio_converter = converter
    return instance


def closeio_custom_field(instance, field_name, converter=None):
    field_name = ("custom", field_name)
    return closeio_field(instance, field_name, converter)


BOOLEAN_CONVERTER = ((lambda v: True if v in ['ja', 'Ja'] else False),
                     (lambda v: u"ja" if v else u"nein"))

NULL_BOOLEAN_CONVERTER = ((lambda v: True if v in ['ja', 'Ja'] else None if v in ['', '-'] else False),
                          (lambda v: u"ja" if v else u"" if v is None else u"nein"))

MONTH_CONVERTER = ((lambda v: datetime.date(int(v[:4]), int(v[5:7]), 1) if len(v) == 10 else None),
                   (lambda v: v.isoformat()[:7] if isinstance(v, datetime.date) else u""))