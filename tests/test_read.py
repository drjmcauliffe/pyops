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
_datarateFile = os.path.join(parent_dir, "tests/data/data_rate_avg.out")


# --- epys.read ---
def test_epys_read_datarate_data_shape_numpy():
    data, header, meta = ep.read.datarate(_datarateFile, metadata=True,
                                          pandas=False)
    assert data.shape == (366, 53)


def test_epys_read_datarate_data_shape_pandas():
    data, header, meta = ep.read.datarate(_datarateFile, metadata=True)
    assert data.shape == (366, 52)


def test_epys_read_datarate_meta_length():
    data, header, meta = ep.read.datarate(_datarateFile, metadata=True)
    assert len(meta) == 16


def test_epys_read_datarate_header_length():
    data, header, meta = ep.read.datarate(_datarateFile, metadata=True)
    assert len(header) == 53
