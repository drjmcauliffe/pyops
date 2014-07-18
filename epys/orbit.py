#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import logging
import numpy as np
from scipy import linalg
from spice import et2utc
from spice import furnsh


def transform(fname, metadata=False):
    """
    This function reads a Mission Analysis Orbit file and performs a matrix
    transformation on it. Currently only from the Mercury Equatorial frame to
    the Earth Equatorial frame.

    :param fname: The path to the orbit file.
    :type fname: str.
    :param metadata: Flag to return the metadata dictionary
    :type state: bool.
    :returns:  numpy.array -- the return code.
    """

    furnsh("/Users/jmcaulif/Code/naif/generic/lsk/naif0010.tls")

    logging.basicConfig(level=logging.INFO)

    mdata = {}
    data = {}

    with open(fname, 'r') as fh:
        for line in fh:
            t, x, y, z, vx, vy, vz = [float(x) for x in line.split()]

            T = np.array([[0.98159386604468, 0.19098031873327, 0.0],
                          [-0.16775718426422, 0.86223242348167,
                           0.47792549108063],
                          [0.09127436261733, -0.46912873047114,
                           0.87840037851502]])

            Tinv = linalg.inv(T)

            r = np.array([[x, y, z]])
            v = np.array([[vx, vy, vz]])

            r_new = Tinv.dot(r.T).T
            v_new = Tinv.dot(v.T).T

            x, y, z = r_new[0]
            vx, vy, vz = v_new[0]

            t = et2utc(t * 86400, 'isoc', 2)

            print("{} {:9.2f} {:9.2f} {:9.2f} {:9.6f} {:9.6f} {:9.6f}".
                  format(t, x, y, z, vx, vy, vz))

    fh.close()

    if metadata:
        return data, mdata
    else:
        return data


def demotransform():
    """
    This function can be used to quickly get some data back for testing.
    It uses a pre-defined test orbit file.
    """

    # Grab the working directory and current file name by splitting
    # the os.path value.
    this_dir, this_filename = os.path.split(__file__)

    # Get the path to the parent directory for the current working directory.
    parent_dir = os.path.abspath(os.path.join(this_dir, os.pardir))

    # Build the path to the sample data files.
    samplefile = os.path.join(parent_dir,
                              "sample_data/8848MPO_DF50011_inMME2000.d40")

    # Run the test file through epys.read and save returned object to 'data'.
    # Ask for the return of the 'metadata' and save to 'meta'.
    data = transform(samplefile, metadata=False)

    # Return 'data' and 'meta' to the caller.
    return data

if __name__ == '__main__':
    demotransform()
