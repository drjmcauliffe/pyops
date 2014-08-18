
#!/usr/bin/env python

import re
import pandas as pd
from datetime import datetime, timedelta
import logging


def down_sample(df):
    """
    Function to remove redundant lines in data frame. This is pretty slow
    at the moment.
    """

    deletes = [False]  # we wanna keep the first row ...
    for i in range(df.shape[0] - 2):
        deletes.append(df.irow(i).tolist() == df.irow(i + 1).tolist()
                    == df.irow(i + 2).tolist())
    deletes.append(False)  # ... and the last row.
    keeps = [not i for i in deletes]  # flip the list
    if keeps.count(False) != 0:
        print('{} redundant lines removed'.format(keeps.count(False)))
    return df[keeps]


def parse_header(fname):
    """

    """

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    header = {}
    # data = []
    post_process = False
    experiments = []

    with open(fname, 'r') as fh:
        for line in fh:
            if 'len' in header:
                header['len'] += 1
            else:
                header['len'] = 0

            # Catch the header data and store it in dictionary.
            if re.match(r'#(.*):(.*)', line, re.M | re.I):
                keypair = line.strip('#\n').split(':')
                header[keypair[0].strip()] = keypair[1].strip()
                if 'Output Filename' in header:
                    if header['Output Filename'].split('_')[0] == 'data':
                        file_type = 'data'
                    elif header['Output Filename'].split('_')[0] == 'power':
                        file_type = 'power'
                    else:
                        print('ERROR: The input file is not of recognised type.')
                continue

            # Catch the reference date and add to dictionary.
            if re.match(r'Ref_date:(.*)', line, re.M | re.I):
                keypair = line.strip('#\n').split(':')
                ref_date = datetime.strptime(keypair[1].strip(), "%d-%b-%Y")
                header['Reference Date'] = ref_date
                continue

            # Catch the experiment names to list - data rate file_type
            if re.match(r'(.*)\<(.*)\>', line, re.M | re.I):
                for i in line.replace('.', '').replace('>', '').split():
                    experiments.append(i.replace('<', '').replace('_', '-'))
                header['experiments'] = experiments
                continue

            # Catch the column headers
            if re.match(r'Elapsed time(.*)', line, re.M | re.I):
                _headings = line.split()
                _headings[0:2] = [' '.join(_headings[0:2])]
                _headings = [h.replace('_', '-') for h in _headings]
                # if input is data rate file add experiments to headers
                if file_type == 'data':
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
                if file_type == 'power':
                    experiments = _headings[2:]
                    header['experiments'] = experiments
                header['headings'] = _headings
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
                header['units'] = units
                continue

            if post_process:
                # Raise an error if the the length of 'units' is not equal
                # to the length of '_headings'.
                if len(_headings) != len(units):
                    logger.ERROR("ERROR: The number of headings does not ",
                                 "match the number of units!")

            # if start of data close file and return header ...
            if re.match(r'[0-9]{3}_[0-9]{2}:[0-9]{2}:[0-9]{2}(.*)',
                        line, re.M | re.I):
                fh.close()
                return header
            # ... same but for data rate / power budget file
            if re.match(r'[0-9]{2}-[0-9]{3}T[0-9]{2}:[0-9]{2}:[0-9]{2}.[0-9]{3}Z(.*)',
                        line, re.M | re.I):
                fh.close()
                return header


def parse_time(*arg):
    """
    This function is a catch all for different time parsing methods.
    """
    if len(arg) == 1:  # 'probably' coming from power or data budgets 24-084T05:00:00.000Z
        year_doy_time = arg[0]
        if re.match(r'[0-9]{2}-[0-9]{3}T[0-9]{2}:[0-9]{2}:[0-9]{2}.[0-9]{3}Z(.*)',
                    year_doy_time, re.M | re.I):
            ref_date = datetime(int(year_doy_time.split('-')[0]) + 2000, 1, 1)
            dtdelta = timedelta(days=int(year_doy_time.split('-')[1].split('T')[0]))
            return ref_date + dtdelta
        else:
            print('Error: Can\'t recognise time string format of {}.'.format(year_doy_time))
            return 1
    elif len(arg) == 2:  # 'probably' coming from power or data rate outfiles.
        days_time, ref_date = arg
        if re.match(r'[0-9]{3}_[0-9]{2}:[0-9]{2}:[0-9]{2}(.*)',
                    days_time, re.M | re.I):
            days, time = days_time.split('_')
            hours, minutes, seconds = time.split(':')
            time = ref_date + timedelta(days=int(days), hours=int(hours),
                                        minutes=int(minutes), seconds=float(seconds))
            return time
        else:
            print('Error: Can\'t recognise time string format of {}.'.format(days_time))
            return 1
    else:
        print('Error: Can\'t handle {} arguments.'.format(len(arg)))
        return 1


def read(fname, meta=False):
    """
    This function reads any one of a number of EPS input/output files and
    returns the data in a pandas dataframe. The file metadata can also be
    returned if requested.

    :param fname: The path to the power_avg.out or data_rate_avg.out
    :type fname: str.
    :param meta: Flag to return the header dictionary
    :type state: bool.
    :returns:  pandas dataframe -- the return code.
    """
    print('parsing header')
    header = parse_header(fname)

    if 'Output Filename' in header:
        try:
            print('reading data table')
            data = pd.read_table(fname, skiprows=header['len'], header=None,
                                 names=header['headings'], sep=r"\s*", engine='python')
            print('parsing times strings')
            data['Elapsed time'] = [parse_time(x, header['Reference Date']) for x in data['Elapsed time']]
            print('setting index')
            data = data.set_index(['Elapsed time'])
            print('downsampling')
            data = down_sample(data)

            if meta:
                return data, header
            else:
                return data
        except:
            print('Error: Didn\'t recognise file format...')
            return 1
    else:
        try:
            budget = pd.read_table(fname, header=None, comment='#',
                                   names=['date', 'value'], sep=r"\s*",
                                   engine='python')
            budget = budget[budget['value'].notnull()]
            budget['date'] = [parse_time(x) for x in budget['date']]
            budget = budget.set_index(['date'])

            if meta:
                return budget, header
            else:
                return budget
        except:
            print('Error: Didn\'t recognise file format...')
            return 1
