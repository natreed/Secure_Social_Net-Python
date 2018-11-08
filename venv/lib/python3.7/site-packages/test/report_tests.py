# -*- mode:python; coding:utf-8; tab-width:4 -*-

from hamcrest import contains_string, is_not
from prego import TestCase, Task

prego_cmd = 'bin/prego %s -c /dev/null'


class TestOutOptions(TestCase):
    def test_print_outs_on_fail(self):
        task = Task()
        task.command(prego_cmd % '-peo examples/examples.py:Test.test_cmd_fail_with_outs', expected=1)
        task.assert_that(task.lastcmd.stderr.content,
                         contains_string("A.0.out| STDOUT"))

        task.assert_that(task.lastcmd.stderr.content,
                         contains_string("A.3.err| STDERR"))

    def test_do_not_print_outs_on_fail(self):
        task = Task()
        task.command(prego_cmd % '-p examples/examples.py:Test.test_cmd_fail_with_outs', expected=1)
        task.assert_that(task.lastcmd.stderr.content,
                         is_not(contains_string("A.0.out| STDOUT")))

        task.assert_that(task.lastcmd.stderr.content,
                         is_not(contains_string("A.3.err| STDERR")))
