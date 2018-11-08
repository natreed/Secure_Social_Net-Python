# -*- coding:utf-8; tab-width:4; mode:python -*-

import os
import pwd
import string

import blessings
#import commodity.term as term
from commodity.pattern import memoized
from commodity.os_ import resolve_path

from . import config

AUTO = '__AUTO__'
PREGO_TMP_BASE = os.path.join('/tmp', 'prego-{0}'.format(pwd.getpwuid(os.getuid())[0]))
PREGO_TMP = os.path.join(PREGO_TMP_BASE, str(os.getpid()))
INDENTST = 9 * ' '
IDENTIFIERS = string.ascii_uppercase + string.ascii_lowercase

config_path = [
    '.',                           # pwd
    '/usr/share/lib/prego',        # debian
    '/share/lib/prego',            # virtualenv
    '/usr/local/share/lib/prego']  # pip

PREGO_SPECS = os.path.abspath(resolve_path('config.spec', config_path)[0])
PREGO_CMD_DEFAULTS = os.path.abspath(resolve_path('defaults.config', config_path)[0])
USER_CONFIG = os.path.abspath(os.path.join(os.environ['HOME'], '.prego'))
CWD_CONFIG = os.path.join(os.getcwd(), '.prego')


@memoized
def term():
    return blessings.Terminal(force_styling=config.color or None)


class Status:
    _FAIL     = 0
    _OK       = 1
    _ERROR    = 2
    _NOEXEC   = 3
    _UNKNOWN  = 4
    _SOFTFAIL = 5
    _SOFTOK   = 6

    stringfied_values = {
        _FAIL:     ('FAIL',    'FAIL'),
        _OK:       ('OK',      'OK'),
        _ERROR:    ('ERROR',   '!!'),
        _NOEXEC:   ('NOEXEC',  '--'),
        _UNKNOWN:  ('UNKNOWN', '??'),
        _SOFTFAIL: ('fail',    'fail'),
        _SOFTOK:   ('ok',      'ok'),
        }

    color_map = {
        _FAIL:     lambda: term().bold_red,
        _OK:       lambda: term().bold_green,
        _NOEXEC:   lambda: term().normal,
        _ERROR:    lambda: term().bold_red,
        _UNKNOWN:  lambda: term().normal,
        _SOFTFAIL: lambda: term().red,
        _SOFTOK:   lambda: term().green,
        }

    def __init__(self, value=None):
        if value is None:
            value = self._NOEXEC
        self.value = value

    def __eq__(self, other):
        if all(x.value in [self.FAIL.value, self.SOFTFAIL.value] for x in [self, other]):
            return True

        if all(x.value in [self.OK.value, self.SOFTOK.value] for x in [self, other]):
            return True

        return self.value == other.value

    def __repr__(self):
        return str(self)

    def __str__(self):
        return self.stringfied_values[self.value][0]

    def is_bad(self):
        return self.value in [self._FAIL, self._ERROR]

    def pretty(self):
        retval = "{0:^4}".format(self.stringfied_values[self.value][1])
        retval = str.join('', [self.color_map[self.value]()] + [retval, term().normal])
        return "[{0}]".format(retval)

    @classmethod
    def define_statuses(cls):
        Status.FAIL     = Status(Status._FAIL)
        Status.OK       = Status(Status._OK)
        Status.ERROR    = Status(Status._ERROR)
        Status.NOEXEC   = Status(Status._NOEXEC)
        Status.UNKNOWN  = Status(Status._UNKNOWN)
        Status.SOFTFAIL = Status(Status._SOFTFAIL)
        Status.SOFTOK   = Status(Status._SOFTOK)

    def log(self, logger, msg):
        if self in [Status.NOEXEC, Status.UNKNOWN]:
            func = logger.debug
        elif self.is_bad():
            func = logger.error
        else:
            func = logger.info

        func(msg)

    @classmethod
    def indent(cls, char=' '):
        return (6 * char) + ' '


Status.define_statuses()
