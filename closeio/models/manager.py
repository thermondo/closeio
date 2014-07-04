#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging

from closeio import CloseIOError, CloseIO
from django.conf import settings
from django.db.models.manager import Manager


logger = logging.getLogger(__name__)


class CloseIOManager(Manager):
    """
    Object Manager for `CloseIOBaseModel`.
    """

    closeio = CloseIO(settings.CLOSEIO_API_KEY)

    def __init__(self, query=None):
        self.query = query
        super(CloseIOManager, self).__init__()

    def get(self, *args, **kwargs):
        """
        If Database lookup fails, it will search the object on CloseIO and prefetch all fields.
        Returned Models are not saved to the database.
        """
        try:
            return super(CloseIOManager, self).get(*args, **kwargs)
        except self.model.DoesNotExist:
            if "closeio_id" in kwargs:
                try:
                    fields = self.get_closeio(kwargs["closeio_id"])
                    kwargs['closeio_obj'] = fields
                    obj = self.model(**kwargs)
                    return obj
                except CloseIOError:
                    logger.warning("Matching CloseIO query does not exist.", exc_info=True)
            raise

    def get_or_create(self, *args, **kwargs):
        """
        As get but saves the object should it be received through CloseIO.
        """
        try:
            obj = super(CloseIOManager, self).get(*args, **kwargs)
            return obj, False
        except self.model.DoesNotExist:
            if "closeio_id" in kwargs:
                try:
                    fields = self.get_closeio(kwargs["closeio_id"])
                    kwargs['closeio_obj'] = fields
                    obj = self.model(**kwargs)
                    obj.save()
                    return obj, True
                except CloseIOError:
                    logger.warning("Matching CloseIO query does not exist.", exc_info=True)
            raise

    def all(self):
        """
        Returns a set of CloseIOBaseModels not a QuerySet.
        :return: set
        """
        return self.filter()

    def filter(self, query=None):
        """
        Returns a set of CloseIOBaseModels not a QuerySet.
        :param query: String
        :return: set
        """
        return (
            self.model(closeio_obj=f)
            for f in self.filter_closeio(query))

    def get_closeio(self, *args, **kwargs):
        return getattr(self.closeio, "get_%s" % self.model.closeio_type)(*args, **kwargs)

    def filter_closeio(self, *args, **kwargs):
        return getattr(self.closeio, "get_%ss" % self.model.closeio_type)(*args, **kwargs)

    def update_closeio(self, *args, **kwargs):
        return getattr(self.closeio, "update_%s" % self.model.closeio_type)(*args, **kwargs)
