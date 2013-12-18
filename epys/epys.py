#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import pdb
import numpy as np
from datetime import datetime, timedelta
import logging

def read(fname, metadata=False):
    """
    This function reads an EPS generated data-rate file and returns the data
    in a numpy array.  The file metadata can also be returned if requested.

    :param fname: The path to the data_rate_avg.out
    :type fname: str.
    :param metadata: Flag to return the metadata dictionary
    :type state: bool.
    :returns:  numpy.array -- the return code.
    """

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    mdata = {}
    post_process = False
    hdings = []

    with open(fname, 'r') as fh:
        for line in fh:

            logger.info("Catch the header data and store it in dictionary.")
            if re.match( r'#(.*):(.*)', line, re.M|re.I):
                keypair = line.strip('#\n').split(':')
                mdata[keypair[0].strip()] = keypair[1].strip()
                continue

            logger.info("Catch the reference date and add to dictionary.")
            if re.match( r'Ref_date:(.*)', line, re.M|re.I):
                keypair = line.strip('#\n').split(':')
                mdata['Reference Date'] = keypair[1].strip()
                ref_date = datetime.strptime(mdata['Reference Date'], "%d-%b-%Y")
                continue

            logger.info("Catch the experiment names to list.")
            if re.match( r'(.*)\<(.*)\>', line, re.M|re.I):
                xprmnts = [i.replace('<','').replace('_','-') for i in line.replace('.','').replace('>','').split()]
                continue

            logger.info("Catch the column headers and prefix them with experiment list.")
            if re.match( r'Elapsed time(.*)', line, re.M|re.I):
                _hdings = line.split()
                _hdings[0:2] = [' '.join(_hdings[0:2])]
                for j in range(1,3):
                    _hdings[j] = xprmnts[0] + ' ' + _hdings[j]
                for j in range(3,5):
                    _hdings[j] = xprmnts[1] + ' ' + _hdings[j]
                x = 2
                for j in range(5,len(_hdings),4):
                    for h in range(4):
                        _hdings[j+h] = xprmnts[x] + ' ' + _hdings[j+h]
                    x = x + 1
                continue

            logger.info("Catch the units line and process ...")
            if re.match( r'ddd_hh:mm:ss(.*)', line, re.M|re.I):
                _units = line.replace('(','').replace(')','').split()
                units = _units[0:2]
                for u in range(2,len(_units)):
                    if 'sec' in _units[u]:
                        units.append(_units[u])
                        units.append(_units[u])
                    else:
                        units.append(_units[u])
                post_process = True
                continue

            if post_process:
                logger.info("Raise an error if the the length of 'units' is not equal to the length of '_hdings'.")
                if len(_hdings) != len(units):
                    logger.ERROR('ERROR: The number of headings does not match the number of units!')

                logger.info("Pair the headings and the units ...")
                for i in range(len(_hdings)):
                    logger.debug('index: %d', i)
                    logger.debug('size of _hdings: %d', len(_hdings))
                    logger.debug('size of units: %d', len(units))
                    hdings.append({'head':_hdings[i], 'unit':units[i]})

                logger.info("Prepare 'data' array...")
                data = np.array([x['head'] for x in hdings])
                post_process = False

            logger.info("Check for start of data")
            if re.match( r'[0-9]{3}_[0-9]{2}:[0-9]{2}:[0-9]{2}(.*)', line, re.M|re.I):
                days_time = line.split()[0]
                _data = [float(x) for x in line.split()[1:]]
                days, time = days_time.split('_')
                hours, minutes, seconds = time.split(':')
                _time = ref_date + timedelta(days=int(days), hours=int(hours), minutes=int(minutes), seconds=float(seconds))
                _time = (_time - datetime(2000,1,1)).total_seconds()
                _data.insert(0, _time)
                _data = np.asarray(_data)

                data = np.vstack((data,_data))

    fh.close()

    if metadata:
        return data, mdata
    else:
        return data

def main():
    """
    If epys.py is run this main function will be executed.
    """

    test = read("/Users/jmcaulif/Code/python/epys/resources/sample_data/data_rate_avg.out")

    print(type(test), test.shape)

if __name__ == "__main__":
    main()
