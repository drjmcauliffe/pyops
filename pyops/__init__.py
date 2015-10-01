#!/usr/bin/env python
"""
pyops is a python library for the manipulation, processing and plotting
of the input and output files of ESA Experiment Planning Software (EPS).

.. WARNING::
   This is a very beta-project. It's not on PyPI and can't be installed
   via PIP.
"""

__author__ = 'Jonathan McAuliffe'
__email__ = 'watch.n.learn@gmail.com'
__version__ = '0.3.5'
__url__ = 'https://github.com/johnnycakes79/pyops'

# from pyops import classes, draw, events, maps, orbit, read, utils

# from pyops.draw import planetsplot

from pyops.read import epstable, datatable, powertable, read, Modes
from pyops.dashboard import Dashboard
from pyops.evf import EVF
from pyops.itl import ITL, shift_time
from pyops.edf import EDF
from pyops.utils import plotly_prep, background_colors
