#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
import logging

from django.http import HttpResponse, HttpResponseBadRequest
from django.views.generic import View

from . import signals, utils


logger = logging.getLogger(__name__)


class CloseIOWebHook(View):
    def post(self, request, *args, **kwargs):
        query = json.loads(request.body)

        try:
            data = utils.parse(query['data'])
            
            expl_signal_name = '%s_%s' % (query['model'], query['event'])

            if hasattr(signals, expl_signal_name):
                getattr(signals, expl_signal_name).send(sender=self.__class__, instance=data)

            if query['event'] == 'create':
                signals.closeio_create.send(sender=self.__class__, instance=data, model=query['model'])

            elif query['event'] == 'update':
                signals.closeio_update.send(sender=self.__class__, instance=data, model=query['model'])

            signals.closeio_event.send(sender=self.__class__, instance=data, model=query['model'], event=query['event'])

            return HttpResponse()

        except KeyError:  # request json has wrong structure
            logger.exception("CloseIO webhook request could not be dispatched.")
            return HttpResponseBadRequest()

        except (ValueError, TypeError):  # `json.loads` fails
            logger.exception("CloseIO webhook request could not be parsed.")
            return HttpResponseBadRequest()