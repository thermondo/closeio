#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.dispatch import Signal

closeio_event = Signal(providing_args=["instance", "model", "event"], use_caching=True)

closeio_create = Signal(providing_args=["instance", "model"], use_caching=True)

closeio_update = Signal(providing_args=["instance", "model"], use_caching=True)

closeio_delete = Signal(providing_args=["instance_id", "model"], use_caching=True)

closeio_merge = Signal(providing_args=["source_id", "destination_id", "model"], use_caching=True)

lead_create = Signal(providing_args=["instance"], use_caching=True)

lead_update = Signal(providing_args=["instance"], use_caching=True)

lead_delete = Signal(providing_args=["instance_id"], use_caching=True)

lead_merge = Signal(providing_args=["source_id", "destination_id"], use_caching=True)
