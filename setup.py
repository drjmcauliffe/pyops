#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
from setuptools import setup
from setuptools.command.test import test as testcommand
import os
import shutil
import sys
# import epys
# from multiprocessing import util

root_dir = os.path.dirname(os.path.realpath(__file__))

with open('requirements.txt') as f:
    required = f.read().splitlines()

with open('epys/__init__.py') as f:
    for line in f.readlines():
        if line.startswith('__version__'):
            version = line.split('=')[-1].strip('\n \'')

readme = open('README.rst').read()
history = open('HISTORY.rst').read().replace('.. :changelog:', '')
authors = open('AUTHORS.rst').read()
contributing = open('CONTRIBUTING.rst').read()
LONG_DESCRIPTION = """
ePYs is a python library for the manipulation, processing and plotting of
the input and output files of ESA Experiment Planning Software (EPS).

  - Free software: BSD license
  - Documentation: http://epys.rtfd.org.

**Modules**

  - **draw** makes pretty orbit graphics
  - **events** provides a series of time/date utilities
  - **maps** does things with maps and images
  - **orbit** processes mission analysis orbit files
  - **read** reads EPS/MAPPS output into useable dataframes and/or arrays
  - **utils** more utilities ...
"""


class PyTest(testcommand):
    def finalize_options(self):
        testcommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import pytest
        errcode = pytest.main(self.test_args)
        sys.exit(errcode)


class Tox(testcommand):
    def finalize_options(self):
        testcommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        # import here, cause outside the eggs aren't loaded
        import tox
        errcode = tox.cmdline(self.test_args)
        sys.exit(errcode)


def cleanup():
    cleanuplist = ('build', 'dist', 'epys.egg-info')
    for file in cleanuplist:
        try:
            shutil.rmtree(os.path.join(root_dir, file))
        except OSError:
            pass

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()

try:
    setup(
        name='epys',
        version=version,
        description='A python library for handling EPS output.',
        long_description=LONG_DESCRIPTION,
        author='Jonathan McAuliffe',
        author_email='watch.n.learn@gmail.com',
        url='https://github.com/johnnycakes79/epys',
        packages=['epys', 'test'],
        package_data={'test': ['data/*.out']},
        include_package_data=True,
        # cmdclass={'test': Tox},
        cmdclass={'test': PyTest},
        test_suite='test',
        # tests_require=['tox'],
        tests_require=['pytest'],
        install_requires=required,
        license="BSD",
        zip_safe=False,
        keywords='epys',
        extras_require={
            'testing': ['pytest'],
        }
    )


finally:
    cleanup()
