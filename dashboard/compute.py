from bokeh.embed import components
from bokeh.resources import CDN
from collections import defaultdict
from datetime import datetime as dt
from datetime import timedelta as td
from highcharts import Highchart
from io import BytesIO
from numpy import exp, cos, linspace, random, array
from pandas_highcharts.core import serialize, json_encode

import base64
import bokeh.plotting as bplt
import json
import matplotlib.pyplot as plt
import mpld3
import os, re, time, glob
import pandas as pd
import string

def read_header(filename):
    header = {}
    skiprows = 0
    with open(filename, 'r') as fh:
            for line in fh:
                skiprows += 1
                if re.match(r'ddd_hh:mm:ss(.*)', line, re.M | re.I):
                    break
                if ':' in line:
                    key, value = line.replace('#','').strip().split(':', 1)
                    header[key.replace('(', '').replace(
                        ')', '')] = value.strip().replace('"', '')
            if header['Output Filename'].startswith('power'):
                header_rows = 2
            if header['Output Filename'].startswith('data'):
                header_rows = 3
            header['skiprows'] = skiprows-header_rows
            header['Ref_date'] = dt.strptime(header['Ref_date'], '%d-%B-%Y')
            header['rows'] = header_rows
    return header

def parse_dates(x, ref_date):
    days, time = x.split('_')
    hours, minutes, seconds = time.split(':')
    delta = td(days = int(days), hours=int(hours),
               minutes=int(minutes), seconds=int(seconds))
    return ref_date + delta

def read_file(filename):
    header = read_header(filename)
    df = pd.read_csv(filename, skiprows=header['skiprows'],
        header=list(range(0, header['rows'])), index_col=0)
    df['Elapsed time'] = [parse_dates(x, header['Ref_date']) for x in df.index]
    df = df.set_index(['Elapsed time'])
    return df

def damped_vibrations(t, A, b, w):
    return A*exp(-b*t)*cos(w*t)

def compute_png(A, b, w, T, resolution=500):
    """Return filename of plot of the damped_vibration function."""
    t = linspace(0, T, resolution+1)
    u = damped_vibrations(t, A, b, w)
    plt.figure()  # needed to avoid adding curves in plot
    plt.plot(t, u)
    plt.title('A=%g, b=%g, w=%g' % (A, b, w))

    figfile = BytesIO()
    plt.savefig(figfile, format='png')
    figfile.seek(0)  # rewind to beginning of file
    figdata_png = base64.b64encode(figfile.getvalue())

    return figdata_png

def compute_svg(A, b, w, T, resolution=500):
    """Return filename of plot of the damped_vibration function."""
    t = linspace(0, T, resolution+1)
    u = damped_vibrations(t, A, b, w)
    plt.figure()  # needed to avoid adding curves in plot
    plt.plot(t, u)
    plt.title('A=%g, b=%g, w=%g' % (A, b, w))

    figfile = BytesIO()
    plt.savefig(figfile, format='svg')
    figfile.seek(0)
    figdata_svg = '<svg' + figfile.getvalue().split('<svg')[1]
    figdata_svg = unicode(figdata_svg,'utf-8')
    return figdata_svg

def compute_mpld3(A, b, w, T, resolution=500):
    """Return filename of plot of the damped_vibration function."""
    t = linspace(0, T, resolution+1)
    u = damped_vibrations(t, A, b, T)
    fig, ax = plt.subplots()
    ax.plot(t, u)
    ax.set_title("A={}, b={}, w={}".format(A, b, w))

    html_text = mpld3.fig_to_html(fig)
    return html_text

def compute_bokeh(A, b, w, T, resolution=500):
    """Return filename of plot of the damped_vibration function."""
    t = linspace(0, T, resolution+1)
    u = damped_vibrations(t, A, b, w)

    # create a new plot with a title and axis labels
    TOOLS = "pan,wheel_zoom,hover,box_zoom,reset,save,box_select,lasso_select"
    p = bplt.figure(title="simple line example", tools=TOOLS,
                   x_axis_label='t', y_axis_label='y', logo=None)
    # add a line renderer with legend and line thickness
    p.line(t, u, legend="u(t)", line_width=2)
    script, div = components(p)
    head = """
        <link rel="stylesheet"
         href="http://cdn.pydata.org/bokeh/release/bokeh-0.9.0.min.css"
         type="text/css" />
        <script type="text/javascript"
         src="http://cdn.pydata.org/bokeh/release/bokeh-0.9.0.min.js">
        </script>
        <script type="text/javascript">
        Bokeh.set_log_level("info");
        </script>
        """
    return head, script, div

def compute_highcharts_simple(A, b, w, T, resolution=500):
    """Return filename of plot of the damped_vibration function."""
    t = linspace(0, T, resolution+1)
    u = damped_vibrations(t, A, b, T)
    d = {'t': t, 'u': u}
    df = pd.DataFrame(d)
    df.set_index('t', inplace=True)

    chart = serialize(df, chart_type='stock', render_to='my-chart',
                      output_type='json' )
    return chart

def compute_highcharts(A, b, w, T, resolution=10000):
    """Return filename of plot of the damped_vibration function."""
    t = linspace(0, T, resolution+1)
    u = damped_vibrations(t, A, b, T)
    d = {'t': t, 'u': u}
    df = pd.DataFrame(d)
    df.set_index('t', inplace=True)

    data = serialize(df, output_type='dict', chart_type='stock',
                      render_to='my-chart',
                      )

    data['chart']['type'] = 'line'
    data['chart']['zoomType'] = 'x'
    data['chart']['panning'] = True
    data['chart']['panKey'] = 'shift'
    data['chart']['plotBackgroundColor'] = '#FCFFC5'

    data["plotOptions"] = {
                "spline": {
                    "color": "#FF0000",
                    "lineWidth": 1,
                    "states": { "hover": { "lineWidth": 1 } },
                    "marker": {"enabled": True }
                }
            }

    chart = 'new Highcharts.Chart({});'.format(json_encode(data))

    return chart

def timeline_pandas_highcharts():
    """Return filename of plot of the damped_vibration function."""

    data = defaultdict(lambda: defaultdict(dict))

    timeline_data = pd.read_csv('timeline.txt')

    data['chart']['type'] = 'columnrange'
    data['chart']['inverted'] = True
    data['chart']['zoomType'] = 'y'
    data['chart']['panning'] = True
    data['chart']['panKey'] = 'shift'
    data['chart']['renderTo'] = 'my-chart'

    data['title']['text'] = 'BepiTimeline Test'

    data['scrollbar']['enable'] = True

    data['xAxis']['categories'] = list(set(timeline_data['Instrument'].values.tolist()))

    data['yAxis']['type'] = 'datetime'

    data['yAxis']['title']['text'] = 'Timespan'

    data['plotOptions']['columnrange']['grouping'] =  False

    data['legend']['enabled'] = True

    data['tooltip']['headerFormat'] = '<b>{series.name}</b><br/>'
    data['tooltip']['pointFormat'] = '{point.low} - {point.high}'

    data['series'] = []

    grouped = timeline_data.groupby('Instrument')
    grouped = [grouped.get_group(x) for x in grouped.groups]

    for level, frame in enumerate(grouped):
        df = {}
        df['name'] = frame['Instrument'].values[0]
        df['data'] = []

        for row in frame.itertuples():
            block = {}
            block['x'] = level
            st = dt.strptime(row[2], '%Y-%m-%d %H:%M')
            st = int((st-dt(1970,1,1)).total_seconds()*1000)
            en = dt.strptime(row[3], '%Y-%m-%d %H:%M')
            en = int((en-dt(1970,1,1)).total_seconds()*1000)
            block['low'] = st
            block['high'] = en
            block['mode'] = row[4]
            block['power'] = row[5]
            block['data_rate'] = row[6]
            df['data'].append(block)

        data['series'].append(df)

    chart = 'new Highcharts.Chart({});'.format(json_encode(data))

    print( data['title']['text'] )

    return [data['series'], data['xAxis']['categories'], data['title']['text']]

def timeline_python_highcharts():
    """Return filename of plot of the damped_vibration function."""

    H = Highchart()

    timeline_data = pd.read_csv('timeline.txt')

    options = {
        'chart': {
            'type': 'columnrange',
            'inverted': True,
            'zoomType': 'y'
        },
        'title': {
            'text': 'BepiTimeline Test'
        },
        'xAxis': {
            'categories': list(set(timeline_data['Instrument'].values.tolist()))
        },
        'yAxis': {
            'type': 'datetime'
        },
        'tooltip': {
             'formatter': "function () {return Highcharts.dateFormat('%e %B %H:%M', this.point.low) + ' - ' + Highcharts.dateFormat('%e %B %H:%M', this.point.high);}"
        },
        'plotOptions': {
            'columnrange': {
                'grouping': False
            }
        }
    }

    H.set_dict_options(options)

    grouped = timeline_data.groupby('Instrument')
    grouped = [grouped.get_group(x) for x in grouped.groups]

    for level, frame in enumerate(grouped):
        df = {}
        df['name'] = frame['Instrument'].values[0]
        df['data'] = []

        for row in frame.itertuples():
            block = {}
            block['x'] = level
            st = dt.strptime(row[2], '%Y-%m-%d %H:%M')
            st = int((st-dt(1970,1,1)).total_seconds()*1000)
            en = dt.strptime(row[3], '%Y-%m-%d %H:%M')
            en = int((en-dt(1970,1,1)).total_seconds()*1000)
            block['low'] = st
            block['high'] = en
            df['data'].append(block)

        H.add_data_set(df['data'], 'columnrange', df['name'] )

        print(H.iframe)

    return 0

def timeline(filename):
    """Return filename of plot of the damped_vibration function."""

    data = defaultdict(lambda: defaultdict(dict))

    timeline_input_data = pd.read_csv(filename)
    timeline_title = ''
    timeline_categories = list(
        set(timeline_input_data['Instrument'].values.tolist()))
    timeline_yaxis_title = 'Timespan'

    # build data

    timeline_data = []

    grouped = timeline_input_data.groupby('Instrument')
    grouped = [grouped.get_group(x) for x in grouped.groups]

    for level, frame in enumerate(grouped):
        df = {}
        df['name'] = frame['Instrument'].values[0]
        df['data'] = []

        for row in frame.itertuples():
            block = {}
            block['x'] = level
            st = dt.strptime(row[2], '%Y-%m-%d %H:%M')
            st = int((st-dt(1970,1,1)).total_seconds()*1000)
            en = dt.strptime(row[3], '%Y-%m-%d %H:%M')
            en = int((en-dt(1970,1,1)).total_seconds()*1000)
            block['low'] = st
            block['high'] = en
            block['mode'] = row[4]
            block['power'] = row[5]
            block['data_rate'] = row[6]
            df['data'].append(block)

        timeline_data.append(df)

    result = [
        timeline_data,
        timeline_categories,
        timeline_title
        ]

    return result

def datarate(filename):
    """Return filename of plot of the damped_vibration function."""

    df = read_file(filename)

    # add data volume columns
    for column in df.columns.values.tolist():
        if 'Accum' in column:
            instr = column[0]
            df[instr, 'Volume', 'Gbits'] = df[instr, 'Accum', 'Gbits'].sub(
                df[instr, 'Accum', 'Gbits'].shift(), fill_value=0)
    df = df.sort_index(axis=1)

    insts = ['BELA','ISA','MERMAG','MERTIS','MGNS','MIXS_SIXS',
             'PHEBUS','SERENA','SIMBIOSYS']

    # slice out a few specific dataframes
    df_insts_accum_gbits = {
        'data': df[insts].filter(like='Accum'),
        'title': ''}
    df_insts_volume_gbits = {
        'data': df[insts].filter(like='Volume'),
        'title': 'Data Rate [Gbit/s]'}
    df_insts_upload_kbitsps = {
        'data': df[insts].filter(like='Upload'),
        'title': ''}
    df_ssmm_accum_gbits = {
        'data': df.filter(like='SSMM').filter(like='Accum'),
        'title': ''}
    df_ssmm_volume_gbits = {
        'data': df.filter(like='SSMM').filter(like='Volume'),
        'title': ''}

    # select dataframe to use
    df = df_insts_volume_gbits

    labels = insts # df.columns.tolist()

    data = serialize(df['data'], render_to='datarate', title='',
                       output_type='dict')

    for x in data['series']:
        x['name'] = x['name'][0]

    # data['subtitle'] = {'text': 'a subtitle here...'}
    data['plotOptions'] = {'spline': {
         'lineWidth': 2,
         'states': {
         'hover': {
         'lineWidth': 3}
         }}}
    data['chart']['type'] = 'line'
    data['chart']['zoomType'] = 'x'
    data['chart']['panning'] = True
    data['chart']['panKey'] = 'shift'
    data['title']['text'] = df['title']

    result = 'new Highcharts.StockChart({});'.format(json_encode(data))

    return result

def power(filename):
    """Return filename of plot of the damped_vibration function."""

    df = read_file(filename)

    labels = df.columns.tolist()

    data = serialize(df, render_to='power', title='',
                       output_type='dict')

    # data['subtitle'] = {'text': 'a subtitle here...'}
    data['plotOptions'] = {'spline': {
         'lineWidth': 2,
         'states': {
         'hover': {
         'lineWidth': 3}
         }}}
    data['chart']['type'] = 'line'
    data['chart']['zoomType'] = 'x'
    data['chart']['panning'] = True
    data['chart']['panKey'] = 'shift'

    result = 'new Highcharts.StockChart({});'.format(json_encode(data))

    return result

