# -*- coding:utf-8; tab-width:4; mode:python -*-

from hamcrest import is_, contains_string, all_of
from hamcrest.library.text.stringcontainsinorder import *

from prego import TestCase, Task, File, exists
from prego.shell import Variable

nose = 'nosetests -c /dev/null '
prego_cmd = 'bin/prego -p -c /dev/null %s'


class LogTests(TestCase):
    def test_show_log_on_wrong_command(self):
        task = Task(desc='wrong')
        cmd = task.command(nose + 'examples/examples.py:Test.test_cmd_wrong_true_and_ls',
                           expected=1)
        strings = [
            "TestFailed: assert that command A.0 expected returncode 0, but was 127",
            ">> begin captured logging <<",
            "[FAIL]   A   Task end - elapsed:"]

        for s in strings:
            task.assert_that(cmd.stderr.content, contains_string(s))

    def test_show_log_on_fail_command(self):
        task = Task(desc='fail')
        cmd = task.command(nose + 'examples/examples.py:Test.test_cmd_false_true',
                           expected=1)
        strings = [
            "TestFailed: assert that command A.0 expected returncode 0, but was 1",
            ">> begin captured logging <<",
            "[FAIL]   A   Task end - elapsed:"]

        for s in strings:
            task.assert_that(cmd.stderr.content, contains_string(s))


class KeepGoingTests(TestCase):
    def test_keep_going_off(self):
        task = Task()
        cmd = task.command(
            prego_cmd % 'examples/examples.py:Test.test_cmd_wrong_true_and_ls',
            expected=1)

        strings = [
            "[ ok ]   A.0 Command 'wrong' code (0:127)",
            "assert that command A.0 expected returncode 0, but was 127",
            "[ -- ]   A.3 Command 'true'",
            "[ -- ]   A.5 assert that command A.3 returncode 0",
            ]

        for s in strings:
            task.assert_that(cmd.stderr.content, contains_string(s))

    def test_keep_going_on(self):
        task = Task()
        cmd = task.command(
            prego_cmd % '--keep-going examples/examples.py:Test.test_cmd_wrong_true_and_ls',
            expected=1)

        strings = [
            "[ ok ]   A.0 Command 'wrong' code (0:127)",
            "assert that command A.0 expected returncode 0, but was 127",
            "[ ok ]   A.3 Command 'true'",
            "[ ok ]   A.5 assert that command A.3 returncode 0",
            "[ ok ]   B.0 Command 'ls'",
            "[ ok ]   B.2 assert that command B.0 returncode 0",
            ]

        for s in strings:
            task.assert_that(cmd.stderr.content, contains_string(s))


class GeneratingCommands(TestCase):
    # atheist/examples/bucle.test
    def test_for(self):
        task = Task()
        for i, retcode in [(0, 2), (1, 0), (2, 2)]:
            task.command('ls -%s' % i, cwd='/tmp', expected=retcode, timeout=None)


class Assertions(TestCase):
    # atheist/examples/conditions.test
    def test_pre_post(self):
        task = Task()
        task.assert_that(Variable('SHELL'), exists())
        task.assert_that(File('/etc/motd'), exists())
        task.command('cp /etc/motd /tmp/')
        task.generate_files('/tmp/motd')

        task.command('ls / > /tmp/kk')  # shell=True)
        task.generate_files('/tmp/kk')

        task.assert_that(File('/tmp/kk').content, all_of(
                contains_string('sbin'),
                contains_string('home'),
                contains_string('boot')))


class OutLoggingTests(TestCase):
    def test_auto_log_stdout(self):
        task = Task()
        cmd = task.command(prego_cmd % '-vo examples/command-outs.py:OK.test_ls_stdout_auto')
        task.assert_that(cmd.stderr.content,
                         contains_string('A.0.out| /initrd.img'))

    def test_noauto_log_stdout_when_stdout_flag(self):
        task = Task()
        cmd = task.command(prego_cmd % '-vo examples/command-outs.py:OK.test_ls_stdout')
        task.assert_that(cmd.stderr.content,
                         contains_string('A.0.out| /initrd.img'))

    def test_auto_log_stderr(self):
        task = Task()
        cmd = task.command(prego_cmd % '-ve examples/command-outs.py:OK.test_ls_stderr_auto')
        task.assert_that(cmd.stderr.content,
                         contains_string('A.0.err| /initrd.img'))

    def test_noauto_log_stderr_when_stderr_flag(self):
        task = Task()
        cmd = task.command(prego_cmd % '-ve examples/command-outs.py:OK.test_ls_stderr')
        task.assert_that(cmd.stderr.content,
                         contains_string('A.0.err| /initrd.img'))

    def test_vv_implies_nocapture(self):
        task = Task()
        cmd = task.command(prego_cmd % '-vv test/fixtures/output.py:OutputFixture.test_print_text')
        task.assert_that(cmd.stdout.content,
                         contains_string('OutputFixture printed this'))


class AdviceTests(TestCase):
    def test_no_detach_no_timeout(self):
        task = Task(detach=True)
        cmd = task.command(prego_cmd % '-v test/integration/advices.py:Timeout.test_no_detach_no_timeout', expected=None)
        task.assert_that(cmd.stderr.content,
                         contains_string("A.0 No timeout command in a non detached task could block forever!"))
        Task().delay()


class multiline_commands(TestCase):
    def test_escape_linebreaks_on_log(self):
        task = Task()
        task.command(prego_cmd % '-v test/integration/cases.py:multiline_commands.test_writing_out')
        task.assert_that(task.lastcmd.stderr.content,
                         contains_string("hi\\nbye\\nagain"))
