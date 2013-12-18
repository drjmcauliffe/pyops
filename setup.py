#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys


try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()

readme = open('README.rst').read()
history = open('HISTORY.rst').read().replace('.. :changelog:', '')

setup(
    name='epys',
    version='0.1.0',
    description='A python library for handling EPS output.',
    long_description=readme + '\n\n' + history,
    author='Jonathan McAuliffe',
    author_email='watch.n.learn@gmail.com',
    url='https://github.com/johnnycakes79/epys',
    packages=[
        'epys',
    ],
    package_dir={'epys': 'epys'},
    include_package_data=True,
    install_requires=[
    ],
    license="BSD",
    zip_safe=False,
    keywords='epys',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
    ],
    data_files=[
        ('sampledata', ['sample_data/data_rate_avg.out']),
        ('sampledata', ['sample_data/power_avg.out'])
    ],
    test_suite='tests',
)