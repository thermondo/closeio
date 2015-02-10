# coding=utf-8
from __future__ import (
    absolute_import, division, print_function, unicode_literals
)

import contextlib
import json
from six import text_type, string_types
import types
from datetime import date, datetime, time
from functools import wraps

import dateutil.parser
from slumber.exceptions import SlumberBaseException

from closeio.exceptions import CloseIOError


@contextlib.contextmanager
def convert_errors():
    try:
        yield

    except CloseIOError:
        raise

    except SlumberBaseException as e:
        if hasattr(e, 'content'):
            try:
                error_info = json.loads(e.content)
                if 'error' in error_info:
                    error_message = error_info['error']
                else:
                    error_message = e.content
            except ValueError:
                error_message = text_type(e.content)
        else:
            error_message = text_type(e)

        if hasattr(e, 'response'):
            request = e.response.request
            request_data = 'url: {}\nbody: {}'.format(
                request.url,
                request.body,
            )
        else:
            request_data = ''

        raise CloseIOError(error_message, e, request_data)

    except Exception as e:
        raise CloseIOError(text_type(e), e, '')


def handle_errors(func):
    @wraps(func)
    def wrapped(*args, **kwargs):
        with convert_errors():
            return func(*args, **kwargs)

    return wrapped


class Item(dict):
    def __init__(self, *args, **kwargs):
        super(Item, self).__init__(*args, **kwargs)
        self.__dict__ = self


def parse(value):
    try:
        return Item({
            key: parse(value)
            for key, value in value.items()
        })
    except AttributeError:
        pass

    if isinstance(value, types.GeneratorType):
        return (
            parse(item)
            for item in value
        )

    if not isinstance(value, string_types):
        try:
            return [
                parse(item)
                for item in value
            ]
        except TypeError:
            pass

    try:
        parsed = dateutil.parser.parse(value)

        if parsed.isoformat() == value:
            return parsed

        if parsed.date().isoformat() == value:
            return parsed.date()
        if parsed.time().isoformat() == value:
            return parsed.time()

    except (TypeError, AttributeError, ValueError, OverflowError):
        pass

    return value


def convert(value):
    try:
        return {
            key: convert(value)
            for key, value in value.items()
        }
    except AttributeError:
        pass

    if not isinstance(value, string_types):
        try:
            return [
                convert(item)
                for item in value
            ]
        except TypeError:
            pass

    if isinstance(value, (datetime, date, time)):
        return value.isoformat()

    return value


def parse_response(func):
    @wraps(func)
    def wrapped(*args, **kwargs):
        return parse(func(*args, **kwargs))

    return wrapped


def paginate(func, *args, **kwargs):
    skip = 0
    limit = 100

    while True:
        kwargs['_skip'] = skip
        kwargs['_limit'] = limit

        with convert_errors():
            response = func(*args, **kwargs)

        for item in response['data']:
            yield item

        if not response['has_more']:
            break

        else:
            skip += limit


class DummyCookieJar(object):
    def __init__(self, policy=None):
        pass

    def set_policy(self, policy):
        pass

    def add_cookie_header(self, request):
        pass

    def make_cookies(self, response, request):
        pass

    def set_cookie_if_ok(self, cookie, request):
        pass

    def set_cookie(self, cookie):
        pass

    def extract_cookies(self, response, request):
        pass

    def clear(self, domain=None, path=None, name=None):
        pass

    def clear_session_cookies(self):
        pass

    def clear_expired_cookies(self):
        pass

    def __iter__(self):
        if False:
            yield None

    def __len__(self):
        return 0

    def __repr__(self):
        return "<%s[%s]>" % (self.__class__, "")

    def __str__(self):
        return "<%s[%s]>" % (self.__class__, "")
