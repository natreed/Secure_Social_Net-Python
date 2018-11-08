# -*- mode:python; coding:utf-8; tab-width:4 -*-

from prego import TestCase, Task
from prego.debian import Package, installed


class pip_tests(TestCase):
    def test_install(self):
        task = Task()
        task.assert_that(Package('python-virtualenv'), installed())
        task.command('rm dist/*', expected=None)
        task.command('python setup.py sdist', timeout=20)
        task.command('virtualenv --clear venv')
        task.command('. venv/bin/activate; pip install dist/prego*; echo y | pip uninstall prego; deactivate', timeout=50)
