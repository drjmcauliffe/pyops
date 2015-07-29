from bokeh.plotting import figure, show, output_notebook, gridplot
from bokeh.palettes import brewer
from collections import OrderedDict
from bokeh.models import HoverTool
import numpy as np


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
