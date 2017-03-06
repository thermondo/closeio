#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import

__author__ = 'Denis Cornehl'
__email__ = 'denis.cornehl@gmail.com'
__version__ = '0.4.0'


try:
    from .closeio import CloseIO, CloseIOError  # noqa
except ImportError:
    pass
