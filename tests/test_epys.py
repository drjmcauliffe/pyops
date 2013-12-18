#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_epys
----------------------------------

Tests for `epys` module.
"""

import unittest

from epys import epys


class TestEpys(unittest.TestCase):

    def setUp(self):
        self.data_rate_file = "./sample_data/data_rate_avg.out"

    def test_epys_read_data_rate_data_shape(self):
        data, meta = epys.read(self.data_rate_file, metadata=True)
        assert data.shape == (367, 53)

    def test_epys_read_data_rate_meta_length(self):
        data, meta = epys.read(self.data_rate_file, metadata=True)
        assert len(meta) == 16

    def test_epys_demo_data_rate_data_shape(self):
        data, meta = epys.demo()
        assert data.shape == (367, 53)

    def test_epys_demo_data_rate_meta_length(self):
        data, meta = epys.demo()
        assert len(meta) == 16

    def tearDown(self):
        pass


if __name__ == '__main__':
    unittest.main()
