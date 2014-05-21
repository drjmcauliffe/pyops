#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import epys

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()

version = epys.__version__
readme = open('README.rst').read()
history = open('HISTORY.rst').read().replace('.. :changelog:', '')
authors = open('AUTHORS.rst').read()
contributing = open('CONTRIBUTING.rst').read()

setup(
    name='epys',
    version=version,
    description='A python library for handling EPS output.',
    long_description='ePYs is a python library for the manipulation, '
    + 'processing and plotting of the input and output '
    + 'files of ESA Experiment Planning Software (EPS).',
    # long_description=readme + '\n\n' + history + '\n\n'
    #                         + authors + '\n\n' + contributing,
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
        ('sample_data', ['sample_data/data_rate_avg.out']),
        ('sample_data', ['sample_data/power_avg.out'])
    ],
    test_suite='tests',
)
