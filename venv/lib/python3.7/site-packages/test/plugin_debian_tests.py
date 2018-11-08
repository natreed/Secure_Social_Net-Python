#!/usr/bin/python
# -*- coding:utf-8; tab-width:4; mode:python -*-

from hamcrest import is_not

from prego import Task, TestCase
from prego.debian import Package, installed


class Debian(TestCase):
    def test_installed(self):
        depends = Task()
        depends.assert_that(Package('bash'), installed())
        depends.assert_that(Package('never-installed'),
                            is_not(installed()))

    def test_installed_version(self):
        depends = Task()
        depends.assert_that(Package('python-prego'),
                            installed(min_version='0.20130206'))
