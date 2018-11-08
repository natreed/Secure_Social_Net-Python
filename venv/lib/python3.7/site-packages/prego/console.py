# -*- coding:utf-8; tab-width:4; mode:python -*-

import sys
import os
import logging
import threading

from logging import StreamHandler
from logging import Handler
log = logging.getLogger('nose.plugins.prego')
log.addHandler(logging.StreamHandler())

import argparse

import nose
from nose.plugins import logcapture
from nose.plugins.logcapture import FilterSet

from commodity.type_ import module_to_dict
from commodity.log import CapitalLoggingFormatter, NullHandler
from commodity.pattern import MetaBunch
from commodity.args import parser, add_argument, args

from . import config
from .tools import set_logger_default_formatter, StatusFilter, update_obj
from . import const

logging.getLogger('nose.plugins.manager').addHandler(NullHandler())
plugins_logger = logging.getLogger('nose')
plugins_logger.propagate = False

rdflog = logging.getLogger('rdflib')
# rdflog.propagate = False
rdflog.addFilter(StatusFilter())
rdflog.addHandler(NullHandler())

logging.getLogger().addFilter(StatusFilter())


class MyMemoryHandler(Handler):
    def __init__(self, logformat, logdatefmt, filters):
        Handler.__init__(self)
        fmt = CapitalLoggingFormatter(logformat, logdatefmt)
        self.setFormatter(fmt)
        self.filterset = FilterSet(filters)
        self.buffer = []
    def emit(self, record):
        self.buffer.append(self.format(record))
    def flush(self):
        pass # do nothing
    def truncate(self):
        self.buffer = []
    def filter(self, record):
        return self.filterset.allow(record.name)
    def __getstate__(self):
        state = self.__dict__.copy()
        del state['lock']
        return state
    def __setstate__(self, state):
        self.__dict__.update(state)
        self.lock = threading.RLock()



# if isinstance(logcapture.MyMemoryHandler, BufferingHandler):
logcapture.MyMemoryHandler = MyMemoryHandler
logcapture.LogCapture.logformat = '[%(levelcapital)s] %(message)s'
logcapture.clear = True


def run():
    parser.prog = 'prego'

    # behaviour
    parser.add_argument('-c', '--config', metavar='FILE',
                        help='explicit config file')
    parser.add_argument('-k', '--keep-going', action='store_true',
                        help="continue even with failed assertion or tests")
    parser.add_argument('-d', '--dirty', action='store_true',
                        help="do not remove generated files")

    # output
    parser.add_argument('-o', '--stdout', action='store_true',
                        help='print tests stdout')
    parser.add_argument('-e', '--stderr', action='store_true',
                        help='print tests stderr')
    parser.add_argument('-t', '--time-tag', dest='timetag', action='store_true',
                        help='Include time info in logs')

    parser.add_argument('-v', '--verbose', dest='verbosity', action='count',
                        help='increase log verbosity')

    # styling
    parser.add_argument('-p', '--plain', action='store_false', dest='color',
                        help='avoid colors and styling in output')

    # pass throw nose options
    parser.add_argument('nose', metavar='nose-args', nargs=argparse.REMAINDER)

    parser.load_config_file(const.PREGO_CMD_DEFAULTS)
    parser.parse_args()

    for x in range(args.nose.count('--')):
        args.nose.remove('--')

    if args.config:
        parser.load_config_file(os.path.abspath(args.config))
    else:
        parser.load_config_file(const.USER_CONFIG)
        parser.load_config_file(const.CWD_CONFIG)

    update_obj(config, args)

    if config.timetag:
        logcapture.LogCapture.logformat = '%(asctime)s [%(levelcapital)s] %(message)s'

    if config.verbosity:
        args.nose += ['--nologcapture', '--quiet']

        if config.verbosity == 1:
            loglevel = logging.INFO
        elif config.verbosity >= 2:
            loglevel = logging.DEBUG
            args.nose += ['--nocapture']

        if config.verbosity > 2:
            config.stderr = config.stdout = True

        root = logging.getLogger()
        root.setLevel(loglevel)

        handler = StreamHandler()
        root.addHandler(handler)
        set_logger_default_formatter(root)

    nose.main(argv=['dummy'] + args.nose)
