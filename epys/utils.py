# -*- coding: utf-8 -*
"""
This module is very useful...
"""
from bisect import bisect_left
import os
import sys
import spice
from plotly.graph_objs import Scatter


def all_same(items):
    return all(x == items[0] for x in items)


def background_colors(top_limit=7000, limits=False, bg_alpha=False):
    """
    This function builds a list of plotly Scatter traces for the power
    based seasons. Currently a manual hack.
    TODO: read in power file and build color traces.

    :param top_limit: maximum y-values of background traces.
    :type top_limit: int or float
    :returns: list of plotly Scatter objects
    """
    if not bg_alpha:
        bg_alpha = 0.2

    no_limit = u'''rgba(0, 255, 0, {})'''.format(bg_alpha)
    some_limit = u'''rgba(255,165,0, {})'''.format(bg_alpha)
    big_limit = u'''rgba(255,0,0, {})'''.format(bg_alpha)

    bg_colors = []
    bg_colors.append(Scatter(x=['2024-03-27 18:18:00', '2024-06-03 19:18:00'], y=[top_limit, top_limit], fill='tozeroy', mode='line', yaxis='y1', showlegend=False, fillcolor=no_limit))  # 60
    bg_colors.append(Scatter(x=['2024-06-03 19:18:00', '2024-06-09 20:18:00'], y=[top_limit, top_limit], fill='tozeroy', mode='line', yaxis='y1', showlegend=False, fillcolor=some_limit))  # 301
    bg_colors.append(Scatter(x=['2024-06-09 20:18:00', '2024-06-17 15:48:00'], y=[top_limit, top_limit], fill='tozeroy', mode='line', yaxis='y1', showlegend=False, fillcolor=big_limit))  # 336
    bg_colors.append(Scatter(x=['2024-06-17 15:48:00', '2024-06-23 17:18:00'], y=[top_limit, top_limit], fill='tozeroy', mode='line', yaxis='y1', showlegend=False, fillcolor=some_limit))  # 25
    bg_colors.append(Scatter(x=['2024-06-23 17:18:00', '2024-08-30 18:18:00'], y=[top_limit, top_limit], fill='tozeroy', mode='line', yaxis='y1', showlegend=False, fillcolor=no_limit))  # 60
    bg_colors.append(Scatter(x=['2024-08-30 18:18:00', '2024-09-05 19:48:00'], y=[top_limit, top_limit], fill='tozeroy', mode='line', yaxis='y1', showlegend=False, fillcolor=some_limit))  # 301
    bg_colors.append(Scatter(x=['2024-09-05 19:48:00', '2024-09-13 14:48:00'], y=[top_limit, top_limit], fill='tozeroy', mode='line', yaxis='y1', showlegend=False, fillcolor=big_limit))  # 336
    bg_colors.append(Scatter(x=['2024-09-13 14:48:00', '2024-09-19 16:48:00'], y=[top_limit, top_limit], fill='tozeroy', mode='line', yaxis='y1', showlegend=False, fillcolor=some_limit))  # 25
    bg_colors.append(Scatter(x=['2024-09-19 16:48:00', '2024-11-26 17:48:00'], y=[top_limit, top_limit], fill='tozeroy', mode='line', yaxis='y1', showlegend=False, fillcolor=no_limit))  # 60
    bg_colors.append(Scatter(x=['2024-11-26 17:48:00', '2024-12-02 18:48:00'], y=[top_limit, top_limit], fill='tozeroy', mode='line', yaxis='y1', showlegend=False, fillcolor=some_limit))  # 301
    bg_colors.append(Scatter(x=['2024-12-02 18:48:00', '2024-12-10 14:18:00'], y=[top_limit, top_limit], fill='tozeroy', mode='line', yaxis='y1', showlegend=False, fillcolor=big_limit))  # 336
    bg_colors.append(Scatter(x=['2024-12-10 14:18:00', '2024-12-16 15:48:00'], y=[top_limit, top_limit], fill='tozeroy', mode='line', yaxis='y1', showlegend=False, fillcolor=some_limit))  # 25
    bg_colors.append(Scatter(x=['2024-12-16 15:48:00', '2025-02-22 16:48:00'], y=[top_limit, top_limit], fill='tozeroy', mode='line', yaxis='y1', showlegend=False, fillcolor=no_limit))  # 60
    bg_colors.append(Scatter(x=['2025-02-22 16:48:00', '2025-02-28 18:18:00'], y=[top_limit, top_limit], fill='tozeroy', mode='line', yaxis='y1', showlegend=False, fillcolor=some_limit))  # 301
    bg_colors.append(Scatter(x=['2025-02-28 18:18:00', '2025-03-08 13:18:00'], y=[top_limit, top_limit], fill='tozeroy', mode='line', yaxis='y1', showlegend=False, fillcolor=big_limit))  # 336
    bg_colors.append(Scatter(x=['2025-03-08 13:18:00', '2025-03-14 15:18:00'], y=[top_limit, top_limit], fill='tozeroy', mode='line', yaxis='y1', showlegend=False, fillcolor=some_limit))  # 25
    bg_colors.append(Scatter(x=['2025-03-14 15:18:00', '2025-05-21 16:18:00'], y=[top_limit, top_limit], fill='tozeroy', mode='line', yaxis='y1', showlegend=False, fillcolor=no_limit))  # 60
    bg_colors.append(Scatter(x=['2025-05-21 16:18:00', '2025-05-27 17:18:00'], y=[top_limit, top_limit], fill='tozeroy', mode='line', yaxis='y1', showlegend=False, fillcolor=some_limit))  # 301
    bg_colors.append(Scatter(x=['2025-05-27 17:18:00', '2025-06-04 12:48:00'], y=[top_limit, top_limit], fill='tozeroy', mode='line', yaxis='y1', showlegend=False, fillcolor=big_limit))  # 336
    bg_colors.append(Scatter(x=['2025-06-04 12:48:00', '2025-06-08 00:00:00'], y=[top_limit, top_limit], fill='tozeroy', mode='line', yaxis='y1', showlegend=False, fillcolor=some_limit))  # 25

    return bg_colors


def getclosest(myList, myNumber):
    '''
    Assumes myList is sorted. Returns closest value to myNumber.
    If two numbers are equally close, return the smallest number.

    :param myList:
    :param myNumber:
    :returns:
    '''
    pos = bisect_left(myList, myNumber)
    if pos == 0:
        return myList[0]
    if pos == len(myList):
        return myList[-1]
    before = myList[pos - 1]
    after = myList[pos]
    if after - myNumber < myNumber - before:
        return after
    else:
        return before


def getorbelts(epoch, planet='MERCURY', spacecraft='MPO', verbose=False,
               ltcorr='NONE', reframe='J2000'):
    """
    Main function that ...
    """

    spice.kclear()

    # Load the kernels that this program requires.
    spice.furnsh('epys.mk')

    # convert starting epoch to ET
    et = spice.str2et(epoch)

    orbelts = []

    if verbose:
        print('ET Seconds Past J2000: {}'.format(et))
        print('Date: {}'.format(spice.et2utc(et, 'C', 0)))

    # Compute the apparent state of MPO as seen from Mercury in J2000
    starg, ltime = spice.spkezr(spacecraft, et, reframe, ltcorr, planet)

    # Let starg contain the initial state of a spacecraft relative to
    # the center of a planet at epoch ET, and let GM be the gravitation
    # parameter of the planet. The call

    mu = planetmu(planet)
    elts = spice.oscelt(starg, et, mu)

    # elts.append(spice.et2utc(et,'ISOC', 0).split('T')[0])

    orbelts.append(elts[0])
    orbelts.append(elts[1] * spice.dpr())
    orbelts.append(elts[2] * spice.dpr())
    orbelts.append(elts[3] * spice.dpr())
    if elts[4] * spice.dpr() > 180.:
        orbelts.append(elts[4] * spice.dpr() - 360)
    else:
        orbelts.append(elts[4] * spice.dpr())
    orbelts.append(elts[5] * spice.dpr())
    orbelts.append(elts[0] - 2439)

    # spice.kclear()

    return orbelts


def yesno(question, default="yes"):
    '''
    Ask a yes/no question via raw_input() and return their answer.

    :param question: is a string that is presented to the user.
    :param default: is the presumed answer if the user just hits <Enter>. It must be "yes" (the default), "no" or None (meaning an answer is required of the user).
    :returns: The "answer" return value is one of "yes" or "no".
    '''
    valid = {"yes": True, "y": True, "ye": True,
             "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        choice = raw_input().lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' "
                             "(or 'y' or 'n').\n")


def zipdir(path, zip):
    """
    This function _add_summary_here_

    :param path: _add_description_here_
    :param zip: _add_description_here_
    :returns:
    """

    for root, dirs, files in os.walk(path):
        for file in files:
            zip.write(os.path.join(root, file))


def inifix(stem, no_levels):
    """
    This function _add_summary_here_

    :param stem: _add_description_here_
    :param no_levels: _add_description_here_
    :returns:
    """

    print('\n   Writing config chunk to {}.ini'.format(stem))
    iniChunk = open(os.path.join(stem, '{}.ini'.format(stem)), "w")
    iniChunk.write('***Update elements between asterisks***\n')
    iniChunk.write('[Background]\n')
    iniChunk.write('Definitions\\***00X***\\appearsInToolbar=true\n')
    iniChunk.write('Definitions\\***00X***\\autoNrOfLevels=true\n')
    iniChunk.write('Definitions\\***00X***\\backgroundType=ImageSet\n')
    iniChunk.write('Definitions\\***00X***\\baseImageName=',
                   '{}_%1_%2_%3.jpg\n'.format(stem))
    iniChunk.write('Definitions\\***00X***\\hasIcon=true\n')
    iniChunk.write('Definitions\\***00X***\\hasLegend=false\n')
    iniChunk.write('Definitions\\***00X***\\hasOffset=false\n')
    iniChunk.write('Definitions\\***00X***\\iconName=shdrelmap.xpm\n')
    iniChunk.write('Definitions\\***00X***\\imageHeight=720\n')
    iniChunk.write('Definitions\\***00X***\\imageWidth=1440\n')
    iniChunk.write('Definitions\\***00X***\\isActive=true\n')
    iniChunk.write('Definitions\\***00X***\\longitudeOffset=90\n')
    iniChunk.write('Definitions\\***00X***\\maxPolarLevels=2\n')
    iniChunk.write('Definitions\\***00X***\\menuAccelerator=',
                   '***set quick key combo***\n')
    iniChunk.write('Definitions\\***00X***\\menuTextLabel=',
                   '***set label name*** (***set quick key combo***)\n')
    iniChunk.write('Definitions\\***00X***\\nrOfLevels={}\n'.format(no_levels))
    iniChunk.write('Definitions\\***00X***\\toolbarMessageText=',
                   '{}\n'.format(stem.replace('_', ' ').upper()))
    iniChunk.write('Definitions\\***00X***\\menuStatusTipText=',
                   '{}\n'.format(stem.replace('_', ' ').upper()))
    iniChunk.close()


def planetmu(planet):

    # unit = μ (km3s−2)
    # source: http://en.wikipedia.org/wiki/Standard_gravitational_parameter

    planetmu = {'Sun': 132712440018, 'Mercury': 22032, 'Venus': 324859,
                'Earth': 398600.4418, 'Moon': 4902.8000, 'Mars': 42828,
                'Ceres': 63.1, 'Jupiter': 126686534, 'Saturn': 37931187,
                'Uranus': 5793939, 'Neptune': 6836529, 'Pluto': 871,
                'Eris': 1108}

    return planetmu[planet.title()]


def plotly_prep(df):
    """
    This fuction prepares a Pandas dataframe for plotting in Plotly:
        http://nbviewer.ipython.org/gist/nipunreddevil/7734529


    :param df: dataframe for pre-processing for plotly
    :type df: pandas dataframe
    :returns: plotly-ready list of dictionaries
    """
    if df.index.__class__.__name__ == "DatetimeIndex":
        # convert the index to MySQL Datetime like strings
        x = df.index.format()
        # zlternatively, directly use x, since DateTime index is np.datetime64
        # see http://nbviewer.ipython.org/gist/cparmer/7721116
        # x=df.index.values.astype('datetime64[s]')
    else:
        x = df.index.values

    lines = {}
    multidx = False
    keeps = []

    # if the columns header are tuples and not strings then we're
    # dealing with a multi-index
    if df.columns[0].__class__.__name__ == 'tuple':
        multidx = True

    if multidx:
        # exclude redundant information from the legend.
        for i in range(len(df.columns[0])):
            keeps.append(not all_same([key[i] for key in df]))

        if all_same(keeps) is True and keeps[0] is False:
            keeps = [not i for i in keeps]
            keeps[-1] = False

        # get the set of axes by making a list of the last element
        # of each key in the dataframe, then converting this to a
        # set and then back to a list.
        axes = list(set([key[-1] for key in df]))

    # build a list of dictionaries for each trace with meta data.
    for key in df:
        # if we're dealing with a multi-index assign this trace to the
        # appropriate axis by checking the last element of the key list
        # against the axes set.
        if multidx:
            axis = axes.index(key[-1]) + 1
        # define dict for this trace
        lines[key] = {}
        # assign the x values defined above to the dict key 'x'
        lines[key]["x"] = x
        # assign the values for this key to the dict key 'y'
        lines[key]["y"] = df[key].values
        if multidx:
            # if multi-index specify axis as defined above
            lines[key]["yaxis"] = 'y{}'.format(axis)
            # and build a name for the trace using the non-redundant parts
            # of the key. what this means is that if you are plotting 10 traces
            # all of the same variable then the name and unit of the variable
            # will be redundant and need not show up in the name which will
            # be used to populate the legend.
            lines[key]["name"] = ' '.join([k for k in key if keeps[key.index(k)]])
        else:
            # if we're not dealing with a multi-index the key will just be a string
            # and can bue used for the trace name.
            lines[key]["name"] = key

    if multidx:
        # if dealing with a multi-index flip the keeps list to define a
        # 'what-to-cut' list.
        cuts = [not i for i in keeps]
        # build a  y-axis title stem using the bits cut from the trace name.
        y_title = ' '.join([k for k in df.columns[0] if cuts[df.columns[0].index(k)]])
        if len(axes) == 2:
            # if we have 2 axes then build a tuple of the title stem and the units
            # wrapped in brackets.
            y_title = (y_title + ' [' + axes[0] + ']', y_title + ' [' + axes[1] + ']')
        if len(axes) > 2:
            # if we have more than 2 axes... panic. this isn't dealt with yet.
            print('Hmmm, more than 2 unit types...')
    else:
        # other wise leave it empty
        y_title = ''

    # build list of all traces ..
    lines_plotly = [lines[key] for key in df]
    # and return the list as the y-title.
    return lines_plotly, y_title
