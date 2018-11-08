# -*- coding:utf-8; tab-width:4; mode:python -*-

import time
from pprint import pprint

from .const import term

from hamcrest.core.matcher import Matcher
from hamcrest.core.string_description import StringDescription
from hamcrest.core.assert_that import _assert_bool


def assert_that(arg1, arg2=None, arg3=''):
    if isinstance(arg2, Matcher):
        _assert_match(actual=arg1, matcher=arg2, reason=arg3)
    else:
        _assert_bool(assertion=arg1, reason=arg2)


def _assert_match(actual, matcher, reason):
    if matcher.matches(actual):
        return

    description = StringDescription()
    description.append_text(reason.strip() + ' ')     \
               .append_description_of(matcher) \
               .append_text(', but ')
    matcher.describe_mismatch(actual, description)
    raise AssertionError(str(description))


def wait_that(actual, matcher, reason='', delta=1, timeout=5):
    init = time.time()
    timeout_reached = False
    while 1:
        try:
            if time.time() - init > timeout:
                timeout_reached = True
                break

            _assert_match(actual, matcher, reason)
            break

        except AssertionError:
            time.sleep(delta)

    if timeout_reached:
        raise AssertionError('{0} was not true after {1} seconds'.format(
            matcher, timeout))
