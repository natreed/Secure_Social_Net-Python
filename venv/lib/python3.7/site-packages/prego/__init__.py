# -*- coding:utf-8; tab-width:4; mode:python -*-

import logging

from .runner import *
from .task import *
from .item import *
from .assertion import *
from .testcase import TestCase
from .const import AUTO
from .gvars import context
from .command import *
from .console import run

# wait_that should be in hamcrest
# from .assert_that import wait_that

from .tools import set_logger_default_formatter, load_default_config
set_logger_default_formatter(logging.getLogger())

from . import config
load_default_config(config)
