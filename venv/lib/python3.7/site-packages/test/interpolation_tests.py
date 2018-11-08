# -*- coding:utf-8; tab-width:4; mode:python -*-

import os
import prego
import hamcrest
import pwd

TESTDIR = os.path.abspath(os.path.split(__file__)[0])
BASEDIR = os.path.dirname(TESTDIR)
PID = os.getpid()
LOGIN = pwd.getpwuid(os.getuid())[0]


class CommandInterpolation(prego.TestCase):
    def echo(self, var):
        task = prego.Task(var)
        cmd = task.command('echo ' + var, stdout=prego.AUTO)
        return task, cmd

    def test_basedir(self):
        task, cmd = self.echo('$basedir')
        task.assert_that(cmd.stdout.content,
                         hamcrest.equal_to_ignoring_whitespace('.'))

    def test_fullbasedir(self):
        task, cmd = self.echo('$fullbasedir')
        task.assert_that(cmd.stdout.content,
                         hamcrest.equal_to_ignoring_whitespace(BASEDIR))

    def test_testdir(self):
        task, cmd = self.echo('$testdir')
        task.assert_that(cmd.stdout.content,
                         hamcrest.equal_to_ignoring_whitespace('test'))

    def test_fulltestdir(self):
        task, cmd = self.echo('$fulltestdir')
        task.assert_that(cmd.stdout.content,
                         hamcrest.equal_to_ignoring_whitespace(TESTDIR))

    def test_testfilename(self):
        task, cmd = self.echo('$testfilename')
        expected = os.path.split(__file__)[1].rstrip('c')
        task.assert_that(cmd.stdout.content,
                         hamcrest.equal_to_ignoring_whitespace(expected))

    def test_pid(self):
        task, cmd = self.echo('$pid')
        task.assert_that(cmd.stdout.content, hamcrest.contains_string(str(PID)))

    def test_tmp_base(self):
        expected = '/tmp/prego-' + LOGIN
        task, cmd = self.echo('$tmpbase')
        task.assert_that(cmd.stdout.content,
                         hamcrest.equal_to_ignoring_whitespace(expected))

    def test_tmp(self):
        expected = '/tmp/prego-{0}/{1}'.format(LOGIN, PID)
        task, cmd = self.echo('$tmp')
        task.assert_that(cmd.stdout.content,
                         hamcrest.equal_to_ignoring_whitespace(expected))


class KeywordsInterpolation(prego.TestCase):
    def test_cwd(self):
        task = prego.Task()
        cmd = task.command('pwd', cwd='$testdir')
        task.assert_that(cmd.stdout.content,
                         hamcrest.equal_to_ignoring_whitespace(TESTDIR))

    def test_stdout(self):
        task = prego.Task()
        task.command('echo hi', stdout='$basedir/task.out')
        task.assert_that(prego.File('$basedir/task.out'),
                         prego.exists())
