#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
import logging

from django.http import HttpResponse, HttpResponseBadRequest
from django.views.generic import View

from closeio import utils

from . import signals


logger = logging.getLogger(__name__)


class CloseIOWebHook(View):
    def post(self, request, *args, **kwargs):
        try:
            query = json.loads(request.body)
        except (ValueError, TypeError):
            logger.exception("CloseIO webhook request could not be parsed.")
            return HttpResponseBadRequest()

        try:
            event = query['event']
            model = query['model']
            data = utils.parse(query['data'])
        except KeyError:
            logger.exception("CloseIO webhook request could not be dispatched.")
            return HttpResponseBadRequest()

        expl_signal_name = '%s_%s' % (model, event)

        if hasattr(signals, expl_signal_name):
            signal = getattr(signals, expl_signal_name)
            signal.send(
                sender=self.__class__,
                instance=data,
            )

        if event == 'create':
            signals.closeio_create.send(
                sender=self.__class__,
                instance=data,
                model=model,
            )

        elif event == 'update':
            signals.closeio_update.send(
                sender=self.__class__,
                instance=data,
                model=model,
            )

        signals.closeio_event.send(
            sender=self.__class__,
            instance=data,
            model=model,
            event=event,
        )

        return HttpResponse()
