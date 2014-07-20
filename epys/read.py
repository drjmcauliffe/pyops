
#!/usr/bin/env python

import re
import os
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import logging


def datarate(fname, metadata=False, pandas=True):
    """
    This function reads an EPS generated data-rate file and returns
    the data in a numpy array.  The file metadata can also be returned
    if requested.

    :param fname: The path to the data_rate_avg.out
    :type fname: str.
    :param metadata: Flag to return the metadata dictionary
    :type state: bool.
    :param pandas: Flag to return a pandas dataframe (True) or numpy array
    :type state: bool.
    :returns:  pandas dataframe or numpy.array -- the return code.
    """

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    mdata = {}
    data = []
    post_process = False
    headings = []
    experiments = []

    with open(fname, 'r') as fh:
        for line in fh:

            # Catch the header data and store it in dictionary.
            if re.match(r'#(.*):(.*)', line, re.M | re.I):
                keypair = line.strip('#\n').split(':')
                mdata[keypair[0].strip()] = keypair[1].strip()
                continue

            # Catch the reference date and add to dictionary.
            if re.match(r'Ref_date:(.*)', line, re.M | re.I):
                keypair = line.strip('#\n').split(':')
                mdata['Reference Date'] = keypair[1].strip()
                ref_date = datetime.strptime(mdata['Reference Date'],
                                             "%d-%b-%Y")
                continue

            # Catch the experiment names to list.
            if re.match(r'(.*)\<(.*)\>', line, re.M | re.I):
                for i in line.replace('.', '').replace('>', '').split():
                    experiments.append(i.replace('<', '').replace('_', '-'))
                continue

            # Catch the column headers and prefix them with experiment list.
            if re.match(r'Elapsed time(.*)', line, re.M | re.I):
                _headings = line.split()
                _headings[0:2] = [' '.join(_headings[0:2])]
                for j in range(1, 3):
                    _headings[j] = experiments[0] + ' ' + _headings[j]
                for j in range(3, 5):
                    _headings[j] = experiments[1] + ' ' + _headings[j]
                x = 2
                for j in range(5, len(_headings), 4):
                    for h in range(4):
                        _headings[j + h] = experiments[x] + \
                            ' ' + _headings[j + h]
                    x = x + 1
                continue

            # Catch the units line and process ...
            if re.match(r'ddd_hh:mm:ss(.*)', line, re.M | re.I):
                _units = line.replace('(', '').replace(')', '').split()
                units = _units[0:2]
                for u in range(2, len(_units)):
                    if 'sec' in _units[u]:
                        units.append(_units[u])
                        units.append(_units[u])
                    else:
                        units.append(_units[u])
                post_process = True
                continue

            if post_process:
                # Raise an error if the the length of 'units' is not equal
                # to the length of '_headings'.
                if len(_headings) != len(units):
                    logger.ERROR("ERROR: The number of headings does not ",
                                 "match the number of units!")

                # Pair the headings and the units ...")
                for i in range(len(_headings)):
                    headings.append({'head': _headings[i], 'unit': units[i]})

                # Prepare 'data' array...
                header = np.array([x['head'] for x in headings])
                data = np.arange(len(header))
                post_process = False

            # Check for start of data
            if re.match(r'[0-9]{3}_[0-9]{2}:[0-9]{2}:[0-9]{2}(.*)',
                        line, re.M | re.I):
                days_time = line.split()[0]
                _data = [float(x) for x in line.split()[1:]]
                days, time = days_time.split('_')
                hours, minutes, seconds = time.split(':')
                _time = ref_date + timedelta(days=int(days), hours=int(hours),
                                             minutes=int(minutes),
                                             seconds=float(seconds))
                _data.insert(0, _time)
                _data = np.asarray(_data)

                data = np.vstack((data, _data))

    fh.close()

    # remove first data row with dummy data
    data = data[1:]

    if pandas:
        data = pd.DataFrame(data, columns=header)
        data = data.set_index(header[0])

    if metadata:
        return data, header, mdata
    else:
        return data, header


def power(fname, metadata=False, pandas=True):
    """
    This function reads an EPS generated power file and returns
    the data in a numpy array or pandas dataframe. The file metadata can
    also be returned if requested.

    :param fname: The path to the power_avg.out
    :type fname: str.
    :param metadata: Flag to return the metadata dictionary
    :type state: bool.
    :param pandas: Flag to return a pandas dataframe (True) or numpy array
    :type state: bool.
    :returns:  pandas dataframe or numpy.array -- the return code.
    """
    pass


def dataratedemo():
    """
    This function can be used to quickly get some data back for testing.
    It uses a pre-defined test data_rate_avg.out file.
    """

    # Grab the working directory and current file name by splitting
    # the os.path value.
    this_dir, this_filename = os.path.split(__file__)

    # Get the path to the parent directory for the current working directory.
    parent_dir = os.path.abspath(os.path.join(this_dir, os.pardir))

    # Build the path to the sample data files.
    samplefile = os.path.join(parent_dir, "tests/data/data_rate_avg.out")

    # Run the test file through epys.read and save returned object to 'data'.
    # Ask for the return of the 'metadata' and save to 'meta'.
    data, header, meta = datarate(samplefile, metadata=True)

    print('data array shape:   {}'.format(data.shape))
    print('meta data length:   {}'.format(len(meta)))
    print('header data length: {}'.format(len(header)))

    # Return 'data' and 'meta' to the caller.
    return data, header, meta

if __name__ == '__main__':
    dataratedemo()
