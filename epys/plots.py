import pandas as pd
from bokeh.plotting import figure, show, output_notebook, gridplot
from bokeh.palettes import brewer
from collections import OrderedDict
from bokeh.models import HoverTool
import numpy as np
from bokeh.models import ColumnDataSource, Range1d, FactorRange
from datetime import datetime

# BREWER_PLOT
def brewer_plot(data, instruments_all, instruments=None,):

    output_notebook(hide_banner=True)

    big_figure = create_plot(data, instruments_all)
    small_figure = create_plot(data, instruments, big_figure.x_range)

    p = gridplot([[big_figure], [small_figure]])

    show(p)


def create_plot(data, instruments, x_range=None):
    # Create a set of tools to use
    tools = "pan,wheel_zoom,box_zoom,reset,hover"

    areas = stacked(data, instruments)

    colors = palette(len(areas))

    x2 = np.hstack((data.index.values[::-1], data.index.values))

    if x_range is None:
        f = figure(x_axis_label=data.index.name, y_axis_label='Watts',
                   x_axis_type="datetime", tools=tools)
    else:
        f = figure(x_axis_label=data.index.name, y_axis_label='Watts',
                   x_axis_type="datetime", x_range=x_range, tools=tools)
    for pos in range(len(colors)):
        f.patch(x2, list(areas.values())[pos], color=colors[pos],
                legend=instruments[pos], line_color=None, alpha=0.8)

    f.grid.minor_grid_line_color = '#eeeeee'

    hover = f.select(dict(type=HoverTool))
    hover.tooltips = [
        # add to this
        ("index", "$index"),
    ]

    return f


def palette(number):
    """
    This function returns a palette of hex colors of size number.

    :param number: Amount of different colors needed
    :type number: integer
    :returns: list of strings
    """
    if number > 40:
        print ("Ooops, too many parameters, not enough colors...")

    if number < 3:
        palette = brewer["Spectral"][3]
    elif number < 12:
        palette = brewer["Spectral"][number]
    else:
        palette = brewer["Spectral"][11]
        palette += list(reversed(brewer["RdBu"][11]))
        palette += brewer["YlGnBu"][9]
        palette += list(reversed(brewer["YlGn"][9]))
        palette += brewer["PiYG"][11]

    return palette[:number]


def stacked(df, categories):
    areas = OrderedDict()
    last = np.zeros(len(df[categories[0]]))
    for cat in categories:
        next = last + df[cat]
        areas[cat] = np.hstack((last[::-1], next))
        last = next
    return areas


# MODES_SCHEDULE
def modes_schedule(data):
    output_notebook()
    data = add_difference_column(data)
    start_end_table = build_start_end_table(data)
    source = ColumnDataSource(start_end_table)
    instruments = [colum for colum in data if colum.upper() == colum]

    p = figure(
        x_range=Range1d(start_end_table["Start time"].min(), start_end_table["End time"].max()),
        y_range=FactorRange(factors=instruments),
        plot_height=600, plot_width=1000
    )
    p.quad(left='Start time', right='End time', top='Instrument_top',
           bottom='Instrument_bottom', source=source)
    show(p)



def add_difference_column(data):

    difference = [[]]
    data = data.transpose()
    prev_row = data[data.columns.values[0]]
    pos = 0
    for row in data:
        for element in data[row].index:
            if not prev_row[element] == data[row][element]:
                if not len(difference) == pos + 1:
                    difference.append([element])
                else:
                    difference[pos].append(element)
        prev_row = data[row]
        pos += 1

    data = data.transpose()
    data["Change"] = difference
    return data


def build_start_end_table(data):

    df = pd.DataFrame({"End time": [], "Instrument": [],
                       "Mode": [], "Start time": []})

    data = data.transpose()
    for row in data:
        row_t = data[row].transpose()
        for instrument in row_t["Change"]:
            df.loc[len(df) + 1] = [None, instrument, row_t[instrument], row]

    data = data.transpose()
    instruments = [colum for colum in data if colum.upper() == colum]

    for ins in instruments:
        shift = df.loc[df["Instrument"] == ins].shift(-1)
        if len(shift) > 1:
            for i in range(len(shift.index.values)):
                df.loc[shift.index.values[i], "End time"] = \
                    shift["Start time"][shift.index.values[i]]

    for pos in range(len(df["End time"])):
        if not type(df["End time"][pos+1]) is pd.tslib.Timestamp:
            df.loc[pos+1, "End time"] = df["Start time"].max()
    df[["End time", "Start time"]] = df[["End time", "Start time"]].astype(datetime)

    df["Instrument_bottom"] = [row + ":0.1" for row in df["Instrument"].values]
    df["Instrument_top"] = [row + ":0.9" for row in df["Instrument"].values]
    return df
