#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
from setuptools import setup
from setuptools.command.test import test as TestCommand
import os
import sys
# from epys import __version__

here = os.path.abspath(os.path.dirname(__file__))
version = '0.3.1'  # __version__
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


class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import pytest
        errcode = pytest.main(self.test_args)
        sys.exit(errcode)


def cleanup():
    cleanuplist = ('build', 'dist', 'epys.egg-info')
    for file in cleanuplist:
        try:
            os.remove(os.path.join(here, file))
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
        packages=['epys', 'tests'],
        package_data={'tests': ['data/*.out']},
        include_package_data=True,
        cmdclass={'test': PyTest},
        test_suite='tests.test_read.py',
        tests_require=['pytest'],
        install_requires=['Jinja2==2.7.3',
                        'ipython==2.3.0',
                        'matplotlib==1.4.1',
                        'numpy==1.9.0',
                        'pandas==0.14.1',
                        'plotly==1.2.6',
                        'pytest==2.6.3',
                        'pyzmq==14.4.0',
                        'quantities==0.10.1',
                        'scipy==0.14.0',
                        'tornado==4.0.2'],
        license="BSD",
        zip_safe=False,
        keywords='epys',
        extras_require={
            'testing': ['pytest'],
        }
    )


finally:
    cleanup()
