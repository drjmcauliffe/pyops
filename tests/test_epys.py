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
        pass

    def test_epys_read(self):
        samplefile = "./resources/sample_data/data_rate_avg.out"
        data, meta = epys.read(samplefile, metadata=True)

        assert data.shape == (367, 53)

    def tearDown(self):
        pass


if __name__ == '__main__':
    unittest.main()
