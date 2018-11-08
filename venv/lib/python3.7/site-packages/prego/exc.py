# -*- coding:utf-8; tab-width:4; mode:python -*-

import logging
import traceback

#from .tools import Printable


class TestResultException(AssertionError):
    def __init__(self, task):
        super(Exception, self).__init__(
            "%s\n%s" % (task.reason, task.reason.caller))


class TestFailed(TestResultException):
    pass


class TestError(TestResultException):
    pass


class UserBreak(Exception):
    pass


class ConfigError(Exception):
    pass


class PregoAssertionException(Exception):
    def __init__(self, assertion):
        self.assertion = assertion
        super(Exception, self).__init__(assertion)


class PregoAssertionFailed(PregoAssertionException):
    pass


class PregoAssertionError(PregoAssertionException):
    pass


class CommandAlreadyDefined(Exception):
    pass


def log_exc(exc, logger=logging):
    for line in str(exc).splitlines():
        if line.strip():
            logger.error('| ' + line)


def log_traceback(logger=logging, prefix='| '):
    for line in traceback.format_exc().splitlines():
        if line.strip():
            logger.error(prefix + line)
