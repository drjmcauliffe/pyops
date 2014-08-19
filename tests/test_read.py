#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'johnnycakes79'
"""
test_epys
----------------------------------

Tests for `epys` module.
"""

# import pytest
import os

import epys as ep


this_dir, this_filename = os.path.split(__file__)
parent_dir = os.path.abspath(os.path.join(this_dir, os.pardir))
_dataRateFile = os.path.join(parent_dir, "tests/data/data_rate_avg.out")
_powerFile = os.path.join(parent_dir, "tests/data/power_avg.out")


# --- epys.read for data_rate_avg.out ---
def test_epys_read_datarate():
    data, header = ep.read(_dataRateFile, meta=True)
    assert data.shape == (366, 52)
    assert len(header) == 20
    assert header['experiments'] == ['ANTENNA',
                                     'SSMM',
                                     'BELA',
                                     'ISA',
                                     'MERMAG',
                                     'MERTIS',
                                     'MGNS',
                                     'MORE',
                                     'PHEBUS',
                                     'SERENA',
                                     'SIMBIOSYS-STC',
                                     'SIMBIOSYS-HRIC',
                                     'SIMBIOSYS-VIHI',
                                     'MIXS-SIXS']


# --- epys.read for power_avg.out ---
def test_epys_read_power():
    data, header = ep.read(_powerFile, meta=True)
    assert data.shape == (354, 15)
    assert len(header) == 20
    assert header['experiments'] == ['ANTENNA',
                                     'SSMM',
                                     'BELA',
                                     'ISA',
                                     'MERMAG',
                                     'MERTIS',
                                     'MGNS',
                                     'MORE',
                                     'PHEBUS',
                                     'SERENA',
                                     'SIMBIOSYS-STC',
                                     'SIMBIOSYS-HRIC',
                                     'SIMBIOSYS-VIHI',
                                     'MIXS-SIXS']
