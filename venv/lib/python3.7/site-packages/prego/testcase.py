#!/usr/bin/python
# -*- coding:utf-8; tab-width:4; mode:python -*-

import sys
import logging
import warnings
import unittest
from unittest.case import _ExpectedFailure, _UnexpectedSuccess, SkipTest

from .runner import init, Runner
from .exc import TestFailed
from .tools import StatusFilter
from .const import Status, term
from . import gvars


class PregoTestCase(object):
    def __init__(self, testcase, methodname):
        self.testcase = testcase
        self.methodname = methodname
        self.status = Status.NOEXEC

        self.name = "%s.%s" % (testcase.__class__.__name__, methodname)
        self.log = logging.getLogger(self.name)
        self.log.setLevel(logging.INFO)
        self.log.addFilter(StatusFilter(self))
        init()

    def commit(self):
        self.status = Status.UNKNOWN
        self.log.info(Status.indent('=') + term().reverse(' $name BEGIN '))
        try:
            Runner(gvars.tasks).run()
            self.status = Status.OK
        except TestFailed as test_failed:
            self.status = Status.FAIL
            # shrink trackeback
            raise test_failed
        except:
            self.status = Status.ERROR
            raise
        finally:
            self.log.info('$status ' + term().reverse(' $name END '))
            init()


class TestCase(unittest.TestCase):
    def run(self, result=None):
        raised_exc = None
        orig_result = result
        if result is None:
            result = self.defaultTestResult()
            startTestRun = getattr(result, 'startTestRun', None)
            if startTestRun is not None:
                startTestRun()

        self._resultForDoCleanups = result
        result.startTest(self)

        testMethod = getattr(self, self._testMethodName)
        if (getattr(self.__class__, "__unittest_skip__", False) or
            getattr(testMethod, "__unittest_skip__", False)):
            # If the class or method was skipped.
            try:
                skip_why = (getattr(self.__class__, '__unittest_skip_why__', '')
                            or getattr(testMethod, '__unittest_skip_why__', ''))
                self._addSkip(result, skip_why)
            finally:
                result.stopTest(self)
            return

        if Runner.shutdown:
            self._addSkip(result, 'user break')
            result.stopTest(self)
            return

        try:
            success = False
            try:
                gvars.testpath = testMethod.__code__.co_filename
                prego_case = PregoTestCase(self, self._testMethodName)
                self.setUp()
            except SkipTest as e:
                self._addSkip(result, str(e))
            except KeyboardInterrupt:
                raise
            except:
                result.addError(self, sys.exc_info())
            else:
                try:
                    testMethod()
                    prego_case.commit()
                except KeyboardInterrupt:
                    raise
                except self.failureException:
                    exc_info = list(sys.exc_info())
                    if exc_info[0] == TestFailed:
                        exc_info[2] = None  # remove traceback
                    result.addFailure(self, exc_info)
                except _ExpectedFailure as e:
                    addExpectedFailure = getattr(result, 'addExpectedFailure', None)
                    if addExpectedFailure is not None:
                        addExpectedFailure(self, e.exc_info)
                    else:
                        warnings.warn("TestResult has no addExpectedFailure method, reporting as passes",
                                      RuntimeWarning)
                        result.addSuccess(self)
                except _UnexpectedSuccess:
                    addUnexpectedSuccess = getattr(result, 'addUnexpectedSuccess', None)
                    if addUnexpectedSuccess is not None:
                        addUnexpectedSuccess(self)
                    else:
                        warnings.warn("TestResult has no addUnexpectedSuccess method, reporting as failures",
                                      RuntimeWarning)
                        result.addFailure(self, sys.exc_info())
                except SkipTest as e:
                    self._addSkip(result, str(e))
                except Exception as e:
                    raised_exc = e
                    result.addError(self, sys.exc_info())

                else:
                    success = True
                try:
                    self.tearDown()
#                    if not raised_exc:
#                        prego_case.commit()
                except KeyboardInterrupt:
                    raise
                except:
                    result.addError(self, sys.exc_info())
                    success = False

            cleanUpSuccess = self.doCleanups()
            success = success and cleanUpSuccess
            if success:
                result.addSuccess(self)
        finally:
            result.stopTest(self)
            if orig_result is None:
                stopTestRun = getattr(result, 'stopTestRun', None)
                if stopTestRun is not None:
                    stopTestRun()
