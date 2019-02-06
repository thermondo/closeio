import json
import logging

from django.http import HttpResponse, HttpResponseBadRequest
from django.utils.decorators import method_decorator
from django.utils.encoding import force_text
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View

from closeio import utils

from . import signals

logger = logging.getLogger(__name__)


class CloseIOWebHook(View):
    # first elements are from webhook legacy API
    created = ['create', 'created']
    updated = ['update', 'updated']
    deleted = ['delete', 'deleted']
    merged = ['merge', 'merged']

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(CloseIOWebHook, self).dispatch(*args, **kwargs)

    @staticmethod
    def _from_legacy(query):
        return isinstance(query.get('event'), str)

    def _get_event(self, query):
        if self._from_legacy(query):
            return query['event']
        return query['event']['action']

    def _get_model(self, query):
        if self._from_legacy(query):
            return query['model']
        return query['event']['object_type']

    def _get_data(self, query):
        if self._from_legacy(query):
            return query['data']
        return query['event']['data']

    def post(self, request, *args, **kwargs):
        try:
            query = json.loads(force_text(request.body))
        except (ValueError, TypeError):
            logger.exception("CloseIO webhook request could not be parsed.")
            return HttpResponseBadRequest()

        try:
            event = self._get_event(query)
            model = self._get_model(query)
            data = utils.parse(self._get_data(query))
        except KeyError:
            logger.exception("CloseIO webhook request could not be dispatched.")
            return HttpResponseBadRequest()

        data_to_send = dict(
            instance=data
        )

        if event in self.created:
            signals.closeio_create.send(
                sender=self.__class__,
                model=model,
                **data_to_send
            )

        elif event in self.updated:
            signals.closeio_update.send(
                sender=self.__class__,
                model=model,
                **data_to_send
            )

        elif event in self.deleted:
            data_to_send = dict(
                instance_id=data.get('id', '')
            )
            signals.closeio_delete.send(
                sender=self.__class__,
                model=model,
                **data_to_send
            )

        elif event in self.merged:
            data_to_send = dict(
                source_id=data.get('source_id', ''),
                destination_id=data.get('destination_id', ''),
            )
            signals.closeio_merge.send(
                sender=self.__class__,
                model=model,
                **data_to_send
            )

        expl_signal_name = '%s_%s' % (model, event)

        if hasattr(signals, expl_signal_name):
            signal = getattr(signals, expl_signal_name)
            signal.send(
                sender=self.__class__,
                **data_to_send
            )

        signals.closeio_event.send(
            sender=self.__class__,
            model=model,
            event=event,
            instance=data,
        )

        return HttpResponse()
