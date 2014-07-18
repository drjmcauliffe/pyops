#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import spice
from bisect import bisect_left


def getclosest(myList, myNumber):
    """
    Assumes myList is sorted. Returns closest value to myNumber.
    If two numbers are equally close, return the smallest number.
    """
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
    """Ask a yes/no question via raw_input() and return their answer.

    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
        It must be "yes" (the default), "no" or None (meaning
        an answer is required of the user).

    The "answer" return value is one of "yes" or "no".
    """
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
    for root, dirs, files in os.walk(path):
        for file in files:
            zip.write(os.path.join(root, file))


def inifix(stem, no_levels):
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


def plotlyprep(df):
    """
    Coverting a Pandas Data Frame to Plotly interface:
        http://nbviewer.ipython.org/gist/nipunreddevil/7734529
    """

    if df.index.__class__.__name__ == "DatetimeIndex":
        #Convert the index to MySQL Datetime like strings
        x = df.index.format()
        #Alternatively, directly use x, since DateTime index is np.datetime64
        #see http://nbviewer.ipython.org/gist/cparmer/7721116
        #x=df.index.values.astype('datetime64[s]')
    else:
        x = df.index.values

    lines = {}
    for key in df:
        lines[key] = {}
        lines[key]["x"] = x
        lines[key]["y"] = df[key].values
        lines[key]["name"] = key

    #Appending all lines
    lines_plotly = [lines[key] for key in df]
    return lines_plotly


if __name__ == '__main__':
    print(getorbelts('2024/05/07 12:00'))
