# -*- coding: utf-8 -*
"""
This module contains a number of functions to read and parse various EPS/MAPPS
input and output data file formats and return the information (usually) in the
form of a pandas dataframe.
"""

import copy
import re
import pandas as pd
import numpy as np
from epys.utils import plotly_prep, background_colors
from datetime import datetime, timedelta
import logging
from plotly.graph_objs import Data, Layout, Figure, XAxis, YAxis
import plotly.plotly as py


class epstable:

    def __init__(self, fname, columns=False):
        self.data, self.header = read(fname, meta=True, columns=columns)

    # def __str__(self):
    #     pass

    # def __repr__(self):
    #     return self.header

    def range(self):
        return self.data.index[0], self.data.index[-1]

    def range_str(self):
        return str(self.data.index[0]), str(self.data.index[-1])

    def range_jd(self):
        return self.data.index[0].to_julian_date(), self.data.index[-1].to_julian_date()

    def range_datetime(self):
        return self.data.index[0].to_datetime(), self.data.index[-1].to_datetime()

    def head(self):
        return self.data.head()

    def tail(self):
        return self.data.tail()

    def thin(self):
        self.data = self.data.ix[:, (self.data != 0).any(axis=0)]

    def iplot(self, selection=False, limits=False, title=False,
              x_title=False, x_range=False,
              y_title=False, y_range=False,
              showlegend=True, bg_alpha=False):

        if selection:
            if selection.__class__.__name__ == 'str':
                selection = re.split(' |,', selection)
                selection = [x for x in selection if x != '']
            cols = []
            for term in selection:
                results = [x for x in self.data.columns if term in x]
                for result in results:
                    cols.append(result)
            data_to_plot = self.data[cols]
        else:
            data_to_plot = self.data

        plot(data_to_plot, limits=limits, title=title,
            x_title=x_title, x_range=x_range,
            y_title=y_title, y_range=y_range,
            showlegend=showlegend, bg_alpha=bg_alpha)

    def join(self, df_to_join, in_place=False):
        # try:
        if in_place:
            self.data = merge_dataframes(self.data, df_to_join.data)
            try:
                self.data = self.data.sortlevel(axis=1)
            except:
                print('Warning: can only sort by level with a hierarchical index.')
        else:
            table_copy = copy.deepcopy(self)
            table_copy.data = merge_dataframes(table_copy.data, df_to_join.data)
            return table_copy
        # except:
        #     print('Ooops: that didn\'t work! Make sure your column ' +
        #           'and row indices match if using MutltiIndex. ' +
        #           'Or maybe the columns you\'re adding already exist.')
        #     return

    def sub(self, table_to_subtract, chop=False):
        """
        This function __does_something_unbelievable__

        :param table_to_subtract: _add_description_here_
        :type table_to_subtract: _add_type_here_
        :param chop: _add_description_here_
        :type chop: _add_type_here_
        :returns:
        """

        if chop:
            self.data = self.data.sub(table_to_subtract.data)
        else:
            table_copy = copy.deepcopy(self)
            table_copy.data = table_copy.data.sub(table_to_subtract.data)
            return table_copy


class powertable(epstable):

    def __init__(self, fname):
        self.data, self.header = read(fname, meta=True)
        self.columns = zip(self.header['headings'], self.header['units'])
        self.instruments = self.header['experiments']

    # def select(self, level1, level2, level3, chop=False):
    #     if not level1:
    #         level1 = slice(None)
    #     if not level2:
    #         level2 = slice(None)
    #     if not level3:
    #         level3 = slice(None)
    #     if chop:
    #         self.data = self.data.loc[slice(None), (level1, level2, level3)]
    #     else:
    #         table_copy = copy.deepcopy(self)
    #         table_copy.data = table_copy.data.loc[slice(None), (level1, level2, level3)]
    #         return table_copy


class datatable(epstable):

    def __init__(self, fname):
        """
        This function __does_something_unbelievable__

        :param fname: _add_description_here_
        :type fname: _add_type_here_
        :returns:
        """
        # read in the data
        self.data, self.header = read(fname, meta=True)
        # define experiments list
        self.instruments = self.header['experiments']
        # correct poorly- or un-named columns...
        unit_swaps = [('Kbits', 'kbit'), ('/sec', '/s'), ('Gbits', 'Gbit')]
        for swap in unit_swaps:
            for u in range(len(self.header['units'])):
                if swap[0] in self.header['units'][u]:
                    self.header['units'][u] = self.header['units'][u].replace(swap[0], swap[1])
        self.columns = zip(self.header['headings'], self.header['units'])
        cols = self.columns[1:]
        arrays = [[x[0].split()[0] for x in cols],
                  [x[0].split()[1] for x in cols],
                  [x[1] for x in cols]]
        self.data.columns = pd.MultiIndex.from_arrays(arrays)
        self.data = self.data.sortlevel(axis=1)
        # from each 'Accum' column produce a 'Volume column'
        for inst in self.instruments:
            try:
                self.data[inst, 'Volume', 'Gbit'] = self.data[inst, 'Accum', 'Gbit'].sub(self.data[inst, 'Accum', 'Gbit'].shift(), fill_value=0)
            except:
                print('The conversion of \'Accum\' to \'Volume\' didn\'t work for \'{}\'.'.format(inst))
        self.data = self.data.sort_index(axis=1)

    def select(self, level1, level2, level3, chop=False):
        """
        This function __does_something_unbelievable__

        :param level1: _add_description_here_
        :type level1: _add_type_here_
        :param level2: _add_description_here_
        :type level2: _add_type_here_
        :param level3: _add_description_here_
        :type level3: _add_type_here_
        :param chop: _add_description_here_
        :type chop: _add_type_here_
        :returns:
        """
        if not level1:
            level1 = slice(None)
        if not level2:
            level2 = slice(None)
        if not level3:
            level3 = slice(None)
        if chop:
            self.data = self.data.loc[slice(None), (level1, level2, level3)]
        else:
            table_copy = copy.deepcopy(self)
            table_copy.data = table_copy.data.loc[slice(None), (level1, level2, level3)]
            return table_copy


def plot(data, limits=False, title=False, x_title=False, x_range=False,
        y_title=False, y_range=False, showlegend=True, bg_alpha=False,
        yaxis1_limit=7000):
    """
    This function __does_something_unbelievable__

    :param limits: _add_description_here_
    :type limits: _add_type_here_
    :param title: _add_description_here_
    :type title: _add_type_here_
    :param x_title: _add_description_here_
    :type x_title: _add_type_here_
    :param x_range: _add_description_here_
    :type x_range: _add_type_here_
    :param y_title: _add_description_here_
    :type y_title: _add_type_here_
    :param y_range: _add_description_here_
    :type y_range: _add_type_here_
    :returns:
    """

    multiaxis = False

    if not limits:
        limits = [data.index[0], data.index[-1]]

    # print(limits)

    try:
        start = data.index.searchsorted(limits[0])
        end = data.index.searchsorted(limits[1])
    except:
        print('TypeError: \'limits\' should be a list of datetime objects, for now... sorry!')
        return

    if start == end:
        print('OOOPS: Your requested range appears to be outside the range of the data set:')
        print('data set > {} to {}'.format(str(data.index[0]), str(data.index[-1])))
        print('limits     > {} to {}'.format(str(limits[0]), str(limits[1])))
        return
    else:
        # Process the <i>power_data</i> dataframe into a <b>plotly</b>-ready <i>dictionary-list</i>.
        if data[start:end].shape[0] * data[start:end].shape[1] > 400000:
            print('Plotly will have issue with plotting so many points.')
            print('Suggestions: set plot limits or downsample data')
            return
        else:
            data_plotly, y_title_backup = plotly_prep(data[start:end])

            if y_title_backup.__class__.__name__ == 'tuple':
                multiaxis = True
                yaxis1_limit = max([max(x['y']) for x in data_plotly if x['yaxis'] == 'y1'])
                yaxis1_limit += yaxis1_limit * 0.1
            else:
                yaxis1_limit = max(data.max().tolist())
                yaxis1_limit += yaxis1_limit * 0.1

            # Ugly build for background color data...
            bg_colors = background_colors(top_limit=yaxis1_limit, bg_alpha=bg_alpha)

            # Create a plotly Data Graph Object from the plotly-ready
            # <b>power_data_plotly</b> dictionary.
            plot_data = Data(bg_colors + data_plotly)

            # Prepare plotly Graph Objects for the plot axes, layout and
            # figure  using data from <b>header</b>.
            if not title:
                title = ''

            if not x_title:
                x_title = ''
            if not x_range:
                x_range = [limits[0], limits[1]]
            xaxis = XAxis(title=x_title, range=x_range)

            if multiaxis:
                yaxis = YAxis(title=y_title_backup[0], range=[0, yaxis1_limit])
                yaxis2 = YAxis(title=y_title_backup[1],
                             overlaying='y',
                             side='right')
                # legend = Legend(x=1, y=1)
                layout = Layout(title=title, yaxis1=yaxis, yaxis2=yaxis2, xaxis1=xaxis,
                                showlegend=showlegend)
            else:
                if not y_title:
                    y_title = y_title_backup
                if not y_range:
                    y_max = max(data.max().tolist())
                    y_range = [0, y_max + y_max * 0.1]
                    # y_range = [0, 600]
                yaxis = YAxis(title=y_title, range=y_range)
                layout = Layout(title=title, yaxis1=yaxis, xaxis1=xaxis,
                                showlegend=showlegend)

            fig = Figure(data=plot_data, layout=layout)

            #Plot with <b>plotly</b>.
            py.iplot(fig, layout=layout)


def merge_dataframes(into_df, from_df):
    """
    This function merges two pandas data frames. The inital purpose was
    to merge sparse power and data downlink budgets into non-sparse EPS/MAPPS
    data_rate_avg.out and power_avg.out dataframes.

    :param into_df: power or data rate dataframe.
    :type into_df: pandas dataframe
    :param from_df: power or data downlink budget.
    :type from_df: pandas dataframe
    :returns: a merged dataframe with redundant NaN rows removed.
    """

    into_df_cols = into_df.columns.tolist()
    from_df_cols = from_df.columns.tolist()
    merged = pd.merge(from_df, into_df, how='outer', left_index=True, right_index=True)
    merged = merged[from_df_cols + into_df_cols]
    from_df_new = merged[from_df_cols]
    current_values = from_df.values[0]

    for i in xrange(merged.shape[0]):
        if np.isnan(from_df_new.values[i]).all():
            from_df_new.values[i] = current_values
        else:
            current_values = from_df_new.values[i]

    merged[from_df_cols] = from_df_new
    merged = merged.truncate(before=into_df.index.values[0],
                             after=into_df.index.values[-1])

    # build index of NaN rows for removal in the return statement
    inds = pd.isnull(merged[into_df_cols]).all(1).nonzero()[0]

    return merged.drop(merged.index[inds])


def parse_header(fname):
    """
    This function takes as input an EPS/MAPPS input or output data file and
    attempts to parse the header and return a key-value dictionary of meta
    data.

    :param fname: EPS/MAPPS input or output data file name
    :type fname: str
    :returns: key-value dictionary of meta data.
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
            if re.match(r'[0-9]{2}-[0-9]{3}T[0-9]{2}:[0-9]{2}:[0-9]{2}(.*)Z(.*)',
                        line, re.M | re.I):
                fh.close()
                return header


def parse_time(*arg):
    """
    This function is a catch all for different time parsing methods.

    :param *arg: date string
    :returns: a datetime object
    """
    if len(arg) == 1:  # 'probably' coming from power or data budgets 24-084T05:00:00.000Z
        year_doy_time = arg[0]
        if re.match(r'[0-9]{2}-[0-9]{3}T[0-9]{2}:[0-9]{2}:(.*)Z(.*)',
                    year_doy_time, re.M | re.I):
            ref_date = datetime(int(year_doy_time.split('-')[0]) + 2000, 1, 1)
            days = int(year_doy_time.split('-')[1].split('T')[0])
            if days > 60 and ((int(year_doy_time.split('-')[0]) + 2000) % 4) == 0:
                days -= 1
            hours = int(year_doy_time.split('-')[1].split('T')[1].split(':')[0])
            minutes = int(year_doy_time.split('-')[1].split('T')[1].split(':')[1])
            seconds = int(round(float(year_doy_time.split('-')[1].split('T')[1].split(':')[2][:-1])))
            dtdelta = timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds)
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


def read(fname, meta=False, columns=False):
    """
    This function reads any one of a number of EPS input/output files and
    returns the data in a pandas dataframe. The file metadata can also be
    returned if requested.

    :param fname: The path to the power_avg.out or data_rate_avg.out
    :type fname: str.
    :param meta: Flag to return the header dictionary
    :type meta: bool.
    :returns: pandas dataframe -- the return code.
    """
    header = {}
    header = parse_header(fname)
    if 'Output Filename' in header:
        try:
            data = pd.read_table(fname, skiprows=header['len'], header=None,
                                 names=header['headings'], sep=r"\s*", engine='python')
            data['Elapsed time'] = [parse_time(x, header['Reference Date']) for x in data['Elapsed time']]
            data = data.set_index(['Elapsed time'])
            data.index.names = ['Date']
            data = remove_redundant_data(data)
            if meta:
                return data, header
            else:
                return data
        except:
            print('Error: Didn\'t recognise file format...')
            return 1
    else:
        try:
            budget = pd.read_table(fname, header=None, comment='#', sep=r"\s*",
                                   # names=columns,
                                   engine='python')
            budget = budget[budget.ix[:, 1].notnull()]
            budget.ix[:, 0] = [parse_time(x) for x in budget.ix[:, 0]]
            budget.rename(columns={0: 'date'}, inplace=True)
            budget = budget.set_index(['date'])
            if columns:
                if len(columns) != len(budget.columns):
                    print('Error: \'columns\' length not equal to number of columns')
                else:
                    budget.columns = columns
            if meta:
                return budget, header
            else:
                return budget
        except:
            print('Error: Didn\'t recognise file format...')
            return 1


def remove_redundant_data(df):
    """
    This function reduces the size of a dataframe by reducing blocks of
    sequential identical data lines greater than 2 to only the earliest
    and latest.

    :param df: pandas dataframe
    :type df: pandas dataframe
    :returns: a smaller pandas dataframe
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
