#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from copy import copy
from abc import abstractproperty
from django.db.models import Model, CharField, Manager, ForeignKey

from .manager import CloseIOManager
from .decorators import *


class CloseIOBaseModel(Model):
    objects = Manager()
    closeio = CloseIOManager()

    _closeio_obj = None

    closeio_id = closeio_field(CharField(max_length=100, unique=True, editable=False), ('id',))

    def __getattr__(self, item):
        """Tries to return a field. If that that fails, it looks for a CloseIO field.

        :param item: str
        :return: object
        """
        if hasattr(self.closeio_obj, item):
            return self.closeio_obj[item]

    @property
    def closeio_obj(self):
        """Lazy loads the CloseIO object.

        :return: dict
        """
        if not self._closeio_obj:
            self._closeio_obj = self.get_closeio_fields()
        return self._closeio_obj

    @closeio_obj.setter
    def closeio_obj(self, value):
        if not isinstance(value, (type(None), dict)):
            raise ValueError("%s must be a dictionary." % value)
        self._closeio_obj = value

    def get_closeio_fields(self):
        if self.closeio_id:
            return self.__class__.closeio.get_closeio(self.closeio_id)

    @abstractproperty
    def closeio_type(self):
        """Should be in ["lead", "opportunity", "task"]

        :return: str
        """
        pass

    def __init__(self, *args, **kwargs):
        super(CloseIOBaseModel, self).__init__(*args, **kwargs)
        self._closeio_obj = kwargs.pop('closeio_obj', None)
        if self._closeio_obj:
            self.load_fields_from_closeio()

    def load_fields_from_closeio(self, force=False):
        for field in self._meta.fields:
            field_name = field.name
            if not getattr(self, field_name) or force:
                self.load_field_from_closeio(field)

    def load_field_from_closeio(self, field):
        obj = self.closeio_obj
        if hasattr(field, 'closeio_field_name'):
            try:
                if field.closeio_converter:
                    setattr(self, field.name,
                            field.closeio_converter[0](reduce(dict.__getitem__, field.closeio_field_name, obj)))
                else:
                    setattr(self, field.name,
                            reduce(dict.__getitem__, field.closeio_field_name, obj))
            except KeyError:
                pass

    def save(self, update_closeio=True, force_insert=False, force_update=False, using=None, update_fields=None):
        if update_closeio:
            self.save_closeio()
        super(CloseIOBaseModel, self).save(force_insert, force_update, using, update_fields)

    def save_closeio(self, obj=None):
        if not self._closeio_obj:
            return False
        obj = obj or copy(self.closeio_obj)

        for field_name in self._meta.get_all_field_names():
            field = self._meta.get_field_by_name(field_name)[0]
            if hasattr(field, 'closeio_field_name'):
                if field.closeio_converter:
                    reduce(dict.__getitem__, field.closeio_field_name[:-1], obj)[field.closeio_field_name[-1]] = \
                        field.closeio_converter[1](getattr(self, field_name))
                else:
                    reduce(dict.__getitem__, field.closeio_field_name[:-1], obj)[field.closeio_field_name[-1]] = \
                        getattr(self, field_name)

        def del_empty_fields(json):
            if isinstance(json, dict):
                for k, v in json.items():
                    if not v:
                        del json[k]
                    elif isinstance(v, (dict, list)):
                        del_empty_fields(v)
            elif isinstance(json, list):
                for v in json:
                    del_empty_fields(v)
        del_empty_fields(obj)
        self.__class__.closeio.update_closeio(self.closeio_id, obj)

    class Meta:
        abstract = True
