# -*- coding:utf-8; tab-width:4; mode:python -*-

import os
import logging

from . import gvars
from .const import Status, PREGO_TMP, INDENTST
from .exc import TestFailed, TestError, UserBreak
from . import config
from .tools import set_testpath

log = logging.getLogger('prego')


class Runner(object):
    shutdown = False

    def __init__(self, tasks):
        self.tasks = tasks

    def run(self):
        if not self.tasks:
            return

        self.run_tasks()
        self.wait_detached()
        self.remove_gen()
        self.report_tasks()

    def run_tasks(self):
        for t in self.tasks:
            try:
                t.run()
                if self._stop_condition(t):
                    break
            except UserBreak:
                Runner.shutdown = True

    def _stop_condition(self, t):
        if config.keep_going:
            return False

        return t.status.is_bad()

    def wait_detached(self):
        log.debug('%s All not detached tasks finished... killing detached',
                  Status.indent('-'))
        while 1:
            unfinished = self.get_unfinished_tasks()
            if not unfinished:
                return

            for t in reversed(unfinished):
                t.terminate()
                t.wait_detached(0.5)

    def remove_gen(self):
        log.debug("%s Temporary directory is '%s'", Status.indent(), PREGO_TMP)

        for t in self.tasks:
            t.remove_gen()

        try:
            os.removedirs(PREGO_TMP)
        except OSError:
            pass

    def report_tasks(self):
        for t in self.tasks:
            if t.status != Status.OK:
                raise TestFailed(t)

    def get_unfinished_tasks(self):
        return [t for t in self.tasks if t.thread
                and t.thread.isAlive()]


def commit(logger=None):
    result = Status.UNKNOWN
    try:
        Runner(gvars.tasks).run()
        result = Status.OK
    except TestFailed as test_failed:
        result = Status.FAIL
        # srink trackeback
        raise test_failed
    except:
        result = Status.ERROR
        raise
    finally:
        if logger:
            logger.info('%s END', result.pretty())
        init()


def run():
    try:
        commit()
    except TestFailed:
        return Status.FAIL

    return Status.OK


def init():
    del gvars.tasks[:]
    gvars.context.clear()
    set_testpath()
