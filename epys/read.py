"""
This module contains a number of functions to read and parse various EPS/MAPPS
input and output data file formats and return the information (usually) in the
form of a pandas dataframe.
"""

import copy
import re
import os
import pandas as pd
import numpy as np
import tempfile as tf
from epys.utils import plotly_prep, background_colors, getMonth, get_unique_from_list, is_elapsed_time, parse_time
from datetime import datetime
import logging
from plotly.graph_objs import Data, Layout, Figure, XAxis, YAxis
import plotly.plotly as py
from epys.plots import brewer_plot, modes_schedule, create_plot, get_modes_schedule, data_plot, power_plot, get_power_plot, get_data_plot


class epstable:
    """
    This is the base class for data tables in epys. Upon instantiation it is
    provided with a filename which is read into a header dictionary and a
    Pandas dataframe. The class has a number of methods for querying its
    characteristics, plotting its contents and merging other tables into it.
    """
    def __init__(self, fname, csv, columns=False):
        """
        This constructor method initialises the epstable object.

        :param fname: input filename
        :type fname: str
        :param columns: user supplied list of column headings
        :type columns: list or tuple
        :returns: epstable object consisting of a header dictionary and Pandas dataframe
        """
        # read in the data
        if csv:
            self.data, self.header = read_csv(fname, meta=True, columns=columns)
        else:
            self.data, self.header = read(fname, meta=True, columns=columns)

    # def __str__(self):
    #     pass

    # def __repr__(self):
    #     return self.header

    def range(self):
        """
        This method returns the time range of the dataframe as pandas Timestamp objects
        """
        return self.data.index[0], self.data.index[-1]

    def range_str(self):
        """
        This methond returns the time range of the dataframe as strings
        """
        return str(self.data.index[0]), str(self.data.index[-1])

    def range_jd(self):
        """
        This method returns the time range of the dataframe as julian date floats
        """
        return self.data.index[0].to_julian_date(), self.data.index[-1].to_julian_date()

    def range_datetime(self):
        """
        This method returns the time range of the dataframe as datetime objects pandas.tslib.Timestamp
        """
        return self.data.index[0].to_datetime(), self.data.index[-1].to_datetime()

    def head(self, n=False):
        """
        This method returns the first n (default 5) rows of the dataframe
        """
        if n:
            return self.data.head(n=n)
        else:
            return self.data.head()

    def tail(self, n=False):
        """
        This method returns the last n (default 5) rows of the dataframe
        """
        if n:
            return self.data.tail(n=n)
        else:
            return self.data.tail()

    def thin(self):
        """
        This method removes columns with only zeros.
        """
        self.data = self.data.ix[:, (self.data != 0).any(axis=0)]

    def iplot(self, selection=False, limits=False, title=False,
              x_title=False, x_range=False,
              y_title=False, y_range=False,
              showlegend=True, bg_alpha=False, with_layout=False):
        """
        This method pre-processes the table object for plotting.

        :param selection: a sub-selection of columns to plot
        :type selection: list
        :param limits: start and end times of data to plot
        :type limits: datetime
        :param title: plot title
        :type title: str
        :param x_title: x-axis title
        :type x_title: str
        :param x_range: x-axis plot range
        :type x_range: list
        :param y_title: y-axis title
        :type y_title: str
        :param y_range: y-axis plot range
        :type y_range: list
        :param showlegend: flag to show the plot legend or not
        :type showlegend: boolean
        :param bg_alpha: factor for transparency of seasonal background
        :type bg_alpha: float (default=0.3)
        :returns:
        """

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
             showlegend=showlegend, bg_alpha=bg_alpha, with_layout=with_layout)

    def join(self, df_to_join, in_place=False):
        """
        This method joins a second table object to this one

        :param df_to_join: table object to joint to this one
        :type df_to_join: epstable
        :param in_place: flag to join in place or return new instance
        :type in_place: boolean
        :returns:
        """
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

    def sub(self, table_to_subtract, in_place=False):
        """
        This method subtracts the contents of second table from the
        contents of this one. Be careful with this... it's not been widely
        tested, I'm not sure what happens if the data tables have different
        column numbers and/or names.

        :param table_to_subtract: data table to subtract from this one
        :type table_to_subtract: epstable
        :param in_place: flag to perform the subtraction on this instance or
        return a new instance
        :type in_place: boolean
        :returns:
        """

        if in_place:
            self.data = self.data.sub(table_to_subtract.data)
        else:
            table_copy = copy.deepcopy(self)
            table_copy.data = table_copy.data.sub(table_to_subtract.data)
            return table_copy


class Modes(epstable):

    def __init__(self, fname):
        """
        This constructor method initialises the Modes object.

        :param fname: input filename
        :type fname: str
        :returns: Modes object
        """
        # read in the data
        self.header, temporaryFile = read_csv_header(fname, meta=True)
        if "module_states" in fname:
            self.header["headings"] = \
                ["Elapsed time"] + [self.header["headings"][i + 1] + " "
                + self.header["units"][i + 1]
                for i in range(len(self.header["units"][1:]))]
        else:
            self.header["headings"] = \
                ["Elapsed time"] + self.header["units"][1:]
        self.data = read_csv(self.header, temporaryFile)

    def plot_schedule(self):
        """
        This function plots module states or modes timeline, it can be possibly
        linked with some other plot trough the given x_range.

        :returns: nothing
        """
        modes_schedule(self.data)

    def get_plot_schedule(self, x_range=None):
        """
        This function returns a plot of the module states or modes timeline,
        it can be possibly linked with some other plot trough the given x_range

        :param x_range: x_range from another figure to link with
        :type x_range: x_range bokeh format
        :returns: if get_plot bokeh figure, else pandas dataframe
        """
        return get_modes_schedule(self.data, x_range)

    def merge_schedule(self, df, instruments, get_plot=False, x_range=None):
        """
        This function returns a plot of the module states and modes merged
        timeline, it can be possibly linked with some other plot trough the
        given x_range It is possible to just received the pandas dataframe if
        we don't want to recive the plot throught the get_plot parameter. We
        can also select what instruments to plot through the instruments
        parameter.

        :param df: Data frame to be merged with self.data
        :type: pandas dataframe
        :param instruments: list of the instruments to plot
        :type instruments: list of strings
        :param get_plot: Flag to return a figure or pandas dataframe
        :type get_plot: boolean
        :param x_range: x_range from another figure to link with
        :type x_range: x_range bokeh format
        :returns: if get_plot bokeh figure, else pandas dataframe
        """
        # Merging both dataframes
        new_df = pd.merge(self.data, df, how='outer', left_index=True,
                          right_index=True, sort=True)
        # Filling the NaN fields with the last not NaN value in the column
        new_df.fillna(method='ffill', inplace=True)

        # Filtering the values we want to show based on the instruments
        columns_to_show = [x for x in new_df.columns.values
                           for y in x.split(' ') if y in instruments]
        deleted_columns = [x for x in new_df.columns.values
                           if x not in columns_to_show]
        # Dropping the filtered values
        new_df.drop(deleted_columns, axis=1, inplace=True)

        if get_plot:
            return get_modes_schedule(new_df, x_range)

        return new_df


class powertable(epstable):

    def __init__(self, fname, csv):
        """
        This constructor method initialises the powertable object.

        :param fname: input filename
        :type fname: str
        :returns: powertable object
        """
        # read in the data
        if csv:
            self.header, temporaryFile = read_csv_header(fname, meta=True)
            self.data = read_csv(self.header, temporaryFile)
        else:
            self.data, self.header = read(fname, meta=True)
        self.columns = zip(self.header['headings'], self.header['units'])
        self.instruments = self.header['experiments']

    def select(self, args, chop=False):
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

        if chop:
            self.data = self.data[args]
        else:
            table_copy = copy.deepcopy(self)
            table_copy.data = table_copy.data[args]
            return table_copy

    def brewer_plot(self, instruments=None):
        """
        This function plots a stacked power usage df, the instruments to be
        plotted can be given as a parameter.

        :param instruments: list of parameters to be plotted
        :type instruments: list of strings
        :returns: nothing
        """
        if instruments is None:
            instruments = self.instruments
        brewer_plot(self.data, self.instruments, instruments)

    def get_brewer_plot(self, instruments=None, x_range=None):
        """
        This function returns a figure of a stacked power usage df, 
        the instruments to be plotted can be given as a parameter. We can also
        link it to another figure using the x_range parameter.

        :param instruments: list of parameters to be plotted
        :type instruments: list of strings
        :param x_range: x_range from another figure to link with
        :type x_range: x_range bokeh format
        :returns: nothing
        """
        if instruments is None:
            instruments = self.instruments
        return create_plot(self.data, instruments, x_range)

    def power_plot(self, instruments=None):
        """
        This function plots a power usage df, the instruments to be
        plotted can be given as a parameter.

        :param instruments: list of parameters to be plotted
        :type instruments: list of strings
        :returns: nothing
        """
        if instruments is None:
            instruments = self.instruments
        power_plot(self.data, instruments)

    def get_power_plot(self, instruments=None):
        """
        This function returns a figure of a power usage df,
        the instruments to be plotted can be given as a parameter. We can also
        link it to another figure using the x_range parameter.

        :param instruments: list of parameters to be plotted
        :type instruments: list of strings
        :param x_range: x_range from another figure to link with
        :type x_range: x_range bokeh format
        :returns: nothing
        """
        if instruments is None:
            instruments = self.instruments
        return get_power_plot(self.data, instruments)


class datatable(epstable):

    def __init__(self, fname, csv):
        """
        This constructor method initialises the datatable object.

        :param fname: input filename
        :type fname: str
        :returns: datatable object
        """
        # read in the data
        if csv:
            self.header, temporaryFile = read_csv_header(fname, meta=True)
            self.temp_header = copy.deepcopy(self.header)
            self.temp_header["headings"] = self.temp_header["headings"][
                len(self.temp_header["headings"]) / 2:]
            self.data = read_csv(self.temp_header, temporaryFile)
        else:
            self.data, self.header = read(fname, meta=True)
            self.temp_header = self.header
        # define experiments list
        self.instruments = self.header['experiments']
        # correct poorly- or un-named columns...
        unit_swaps = [('Kbits', 'kbit'), ('/sec', '/s'), ('Gbits', 'Gbit')]
        for swap in unit_swaps:
            for u in range(len(self.header['units'])):
                if swap[0] in self.header['units'][u]:
                    self.header['units'][u] = self.header['units'][u].replace(swap[0], swap[1])
                    # Removing parenthesis
                    if self.header['units'][u][0] == '(':
                        self.header['units'][u] = self.header['units'][u][1:]
                    if self.header['units'][u][-1] == ')':
                        self.header['units'][u] = self.header['units'][u][:-1]
        self.columns = zip(self.temp_header['headings'], self.header['units'])
        if not csv:
            cols = self.columns[1:]
            arrays = [[x[0].split()[0] for x in cols],
                      [x[0].split()[1] for x in cols],
                      [x[1] for x in cols]]
            self.data.columns = pd.MultiIndex.from_arrays(arrays)
        else:
            cols = [self.instruments, self.temp_header['headings'][1:], self.header['units'][1:]]
            self.data.columns = pd.MultiIndex.from_arrays(cols)

        self.data = self.data.sortlevel(axis=1)

        # from each 'Accum' column produce a 'Volume column'
        for inst in get_unique_from_list(self.instruments):
            try:
                # [inst, 'Volume', 'Gbit'] = [inst, 'Accum', 'Gbit'][i] - [inst, 'Accum', 'Gbit'][i+1] 
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

    def data_plot(self, instruments=None):
        """
        This function plots a data rate df, the instruments to be
        plotted can be given as a parameter.

        :param instruments: list of parameters to be plotted
        :type instruments: list of strings
        :returns: nothing
        """
        if instruments is None:
            instruments = [ins.split(' ') for ins in self.temp_header["headings"][1:]]
        data_plot(self.data, instruments)

    def get_data_plot(self, instruments=None, parameters=None, x_range=None):
        """
        This function returns a  plot of the data rate for the given
        instruments and linked to a possible x_range. If parameters is not None
        they include the exact parameters to be plotted (Instruement and Value)

        :param instruments: list of the instruments to plot
        :type instruments: list of strings
        :param parameters: list of the exact values to be plotted
        :type parameters: list of tuples of a couple of strings
        :param x_range: x_range from another figure to link with
        :type x_range: x_range bokeh format
        :returns: bokeh figure
        """
        if parameters is None:
            if instruments is None:
                instruments = get_unique_from_list(self.instruments)
            parameters = ['Volume']
            instruments = [(ins, p) for ins in instruments for p in parameters]
        else:
            instruments = parameters
        return get_data_plot(self.data, instruments, x_range)


def plot(data, limits=False, title=False, x_title=False, x_range=False,
        y_title=False, y_range=False, showlegend=True, bg_alpha=False,
        yaxis1_limit=7000, with_layout=False):
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

    if not with_layout:
        data_plotly, y_title_backup = plotly_prep(data)
        fig = Figure(data=data_plotly)
        py.iplot(fig)
        return 0

    multiaxis = False

    if not limits:
        limits = [data.index[0], data.index[-1]]

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

def parse_ref_date(line):
    """
    This function parses ref_date string format into date time
    format.

    :param line: line containing reference date
    :type line: str
    :returns: reference date in date time format.
    """
    if re.match(r'Ref_date:(.*)', line, re.M | re.I):
        keypair = line.strip('#\n').split(':')
        ref_date = datetime.strptime(keypair[1].strip(), "%d-%b-%Y")
        return ref_date


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
                header['Reference Date'] = parse_ref_date(line)
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


def read_csv_header(fname, meta=False, columns=False):
    """
    This function reads from a filename and processes the header. The rest of
    the file is copied in a temporary file which will be processed later and
    removed at the end.

    :param fname: The path to the power_avg.out or data_rate_avg.out
    :type fname: str.
    :param meta: Flag to return the header dictionary
    :type meta: bool.
    :returns: pandas dataframe -- the return code.
    """

    # Creating a temporary file where we will have only useful data
    temporaryFile = tf.NamedTemporaryFile(delete=False)
    header = {}
    with open(fname) as f:
        for line in f:
            # Filtering new lines characters
            if line.endswith("\n"):
                line = line[:-1]
            # Filtering lines with comments
            if '#' in line.split(' ')[0]:
                aux = line.split(':')
                if len(aux) > 1:
                    # Storing them into the header
                    header[aux[0][1:].strip()] = aux[1].strip()
            # Filtering blanklines
            elif len(line.split(',')) > 1:
                # Filtering headers of the data
                if not is_elapsed_time(line.split(',')[0]):
                    # Filtering units, not a very scalabe filter
                    # but it works for now...
                    if "hh:mm:ss" in line.split(',')[0]:
                        header["units"] = line.split(',')
                    # Filtering the rest of the headers
                    elif not header.has_key("headings"):
                        header["headings"] = line.split(',')
                    else:
                        header["headings"] += line.split(',')
                else:
                    # Storing useful data in the temporary file
                    temporaryFile.write(line + "\n")
    # Filtering the experiments from the header, not a very scalable filter
    # but it works for now...
    if "headings" in header:
        header["experiments"] = [x for x in header["headings"] if x.upper() == x and len(x)>0]
    # Closing source file and setting temp. file's cursor at the beginning
    f.close()
    temporaryFile.seek(0, 0)
    return header, temporaryFile


def read_csv(header, temporaryFile):
    """
    This function reads a temporary file and dumps all the data in csv format
    into a pandas dataframe.

    :param header: data frame cotaining information of the header of the file
    :type header: pandas dataframe
    :param temporaryFile: path to the temporaryFile which contains the data
    :type temporaryFile: string
    :returns: pandas dataframe
    """

    # Inserting useful data into pandas
    data = pd.read_csv(temporaryFile, header=None, sep=",", decimal='.')
    data.columns = header["headings"]
    # Closing and deleting temporary file
    temporaryFile.close()
    os.unlink(temporaryFile.name)
    # Preparing data to behave as the main Jonathan's script does
    data = prepare_table(data, header)

    return data


def prepare_table(data, header):
    """
    This function prepares de input data to be handled for the rest of the
    functions in this library.

    :param data: raw data
    :type data: pandas dataframe
    :param header: data frame cotaining information of the header of the file
    :type header: pandas dataframe
    :returns: pandas dataframe
    """

    # Getting the reference date from the header and transforming it into
    # datetime format
    ref_date = header["Ref_date"].split('-')[0] + "-" +\
        str(getMonth(header["Ref_date"].split('-')[1])) + "-" + \
        header["Ref_date"].split('-')[2]
    ref_date = datetime.strptime(ref_date, "%d-%m-%Y")

    # Converting the Elapsed time column into datetime format and we set it
    # as the new index of the table
    data["Elapsed time"] = \
        [parse_time(x, ref_date) for x in data["Elapsed time"]]
    data = data.sort_index(by=['Elapsed time'], ascending=[True])
    data = data.set_index("Elapsed time")
    data.index.names = ['Date & Time']

    # Removing redundant data from the dataframe
    data = remove_redundant_data(data)
    return data
