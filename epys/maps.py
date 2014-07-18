#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
from wand.image import Image
from lxml import etree
from datetime import datetime
from events import getMonth
import sys
import os
import re
import zipfile
import shutil
import utils
import binascii

try:
    from pykml.factory import KML_ElementMaker as KML
    NOKMLLIB = False
except:
    NOKMLLIB = True


def _makeTime(time):
    """
        extracts time from an input lineand returns a datetime object.
    """
    date, time = time.split('_')
    day, month, year = date.split('-')
    month = getMonth(month)
    hour, minute, second = time.split(':')
    return datetime(int(year), int(month), int(day),
                    int(hour), int(minute), int(second))


def _swathCenter(line):
    """
        calculate center of swath
    """
    lats = [float(line[3]), float(line[5]), float(line[7]), float(line[9])]
    lngs = [float(line[4]), float(line[6]), float(line[8]), float(line[10])]

    clat = min(lats) + (max(lats) - min(lats)) / 2.
    clng = min(lngs) + (max(lngs) - min(lngs)) / 2.

    return '{}'.format(clat), '{}'.format(clng)


def _buildSwath(line, data, polyalt=5000):
    """
    So far, an ugly hack on building the KML elements
    """

    # split input line
    line = line.split()

    # add polygon altitude to end of line tuple
    line.append(polyalt)

    # parse the time element of the line
    dt = _makeTime(line[1])
    date = dt.date()
    time = dt.time()

    # define time format string
    format = "%Y-%m-%dT%H:%M:%SZ"

    # ensure longitude is between -/+ 180 degrees
    for i in [4, 6, 8, 10]:
        if float(line[i]) > 180.0:
            val = float(line[i]) - 360.0
            line[i] = str(val)

    # build the vertices of the swath (remember the first vertex has to
    # repeat at the end.
    vertices = []
    for c in [3, 5, 7, 9, 3, 5]:
        vertices.append(",".join([line[i] for i in [c + 1, c, -1]]))

    # get center of swath
    clat, clng = _swathCenter(line)

    # create an image placemark for the kml
    image = KML.Placemark(
        # define name based on experiment and filter/channel
        KML.name('{}: {}'.format(data['experiment'], data['filter'])),
        # define description
        # TODO: come up with a more flexible way of doing this...
        KML.description(
            'Orbit no.:                          {}\n'.format(
                data['orbit']),
            'Pericenter time (UTC):              {}\n'.format(
                data['pericenter time'].replace('_', ' ')),
            'First image time (UTC):             {}\n'.format(
                data['first image time'].replace('_', ' ')),
            'First image time (from pericenter): {}\n'.format(
                data['first image time from pericenter'].replace('_',
                                                                 ' ')),
            'Last image time (UTC):              {}\n'.format(
                data['last image time'].replace('_', ' ')),
            'Last image time (from pericenter):  {}\n\n'.format(
                data['last image time from pericenter'].replace('_', ' ')),
            'Image sequence:                     {}\n'.format(line[0]),
            'Image date:                         {}\n'.format(date),
            'Image time:                         {}\n'.format(time),
            'Orbit no.:                          {}\n\n'.format(
                data['orbit']),
            'Pericentre relative time:           {}\n'.format(
                line[2].replace('_', ' ')),
            'Duration:                           {}\n\n'.format(line[20]),
            'S/C altitude:                       {}\n'.format(line[21]),
            'S/C latitude:                       {}\n'.format(line[22]),
            'S/C longitude:                      {}\n'.format(line[23]),
            'S/C target elevation:               {}\n'.format(line[24]),
            'S/C target azimuth:                 {}\n\n'.format(line[25]),
            'Reflection Angle:                   {}\n'.format(line[27]),
            'Sun target elevation:               {}\n'.format(line[28]),
            'Sun target azimuth:                 {}\n'.format(line[29]),
            'Target phase:                       {}\n'.format(line[30]),
            'Target elongation:                  {}\n'.format(line[31]),
            'Local Time:                         {}\n'.format(line[32]),
            'Image smear:                        {}\n'.format(line[33]),
            'Mercury True Anomaly:               {}\n'.format(line[35])
        ),
        # specify appearance time
        KML.TimeSpan(
            #KML.begin(str(tempTime))
            KML.begin(dt.strftime(format))
        ),
        # the style for this swath has been mapped in <swath>stylemap
        KML.styleUrl('#{}stylemap'.format(data['filter'])),
        #KML.styleUrl('#{}1'.format(data['filter'])),
        # define where the 'eye' looks when this swath is double clicked
        KML.LookAt(
            KML.longitude(clng),
            KML.latitude(clat),
            KML.altitude('5000'),
            KML.heading('0'),
            KML.tilt('30'),
            KML.roll('0'),
            KML.altitudeMode('relativeToGround'),
            KML.range('1500000')
        ),
        # defined the geometry object that will hold the swath polygon
        KML.MultiGeometry(
            # defined the swath polygon
            KML.Polygon(
                #KML.tessellate('1'),
                KML.altitudeMode('relativeToGround'),
                #KML.altitudeMode('clampedToGround'),
                KML.outerBoundaryIs(
                    KML.LinearRing(
                        KML.coordinates(
                            " ".join(vertices)
                        )
                    )
                )
            )
        )
    )

    return image


def _docSkel(name):
    name = re.sub('[^a-zA-Z0-9\n\.]', ' ', name.split('.')[0]).title()
    doc = KML.kml(
        KML.Document(
            KML.name(name),
            KML.open('1'),
            KML.visibility('1'),
            # uncomment the following if you want to hide the children
            #            KML.Style(
            #                KML.ListStyle(
            #                    KML.listItemType('checkHideChildren')
            #                ),
            #                id='check-hide-children',
            #                ),
            #            KML.styleUrl('#check-hide-children'),
        )
    )
    return doc


def _makeStyle(name, color):
    """
        Build swath pairs and map...
    """

    # style for the normal state of a swath
    stylen = KML.Style(
        KML.IconStyle(
            KML.scale('0.4'),
            KML.Icon(
                KML.href('http://maps.google.com/mapfiles/kml/shapes/star.png')
            )
        ),
        KML.LineStyle(
            KML.color('ff{}'.format(color)),
            KML.width(2.0)
        ),
        KML.LabelStyle(
            KML.color('990000ff'),
            KML.width('2')
        ),
        KML.PolyStyle(
            KML.color('00{}'.format(color)),
            KML.fill('1'),
            KML.outline('1')
        ),
        id='{}n'.format(name)
    )

    # style for the 'mouse-over' state of a swath
    styleh = KML.Style(
        KML.IconStyle(
            KML.scale('0.8'),
            KML.Icon(
                KML.href('http://maps.google.com/mapfiles/kml/shapes/star.png')
            )
        ),
        KML.LineStyle(
            KML.color('ffff4158'),
            KML.width(1.5)
        ),
        KML.LabelStyle(
            KML.color('990000ff'),
            KML.width('2')
        ),
        KML.PolyStyle(
            KML.color('fff7fff'),
            KML.fill('1'),
            KML.outline('1')
        ),
        id='{}h'.format(name)
    )

    # mapping of above styles
    stylem = KML.StyleMap(
        KML.Pair(
            KML.key('normal'),
            KML.styleUrl('#{}n'.format(name))
        ),
        KML.Pair(
            KML.key('highlight'),
            KML.styleUrl('#{}h'.format(name))
        ),
        id='{}stylemap'.format(name)
    )

    # Expand to make the style simpler...

    # kurl = 'http://maps.google.com/mapfiles/kml/shapes/star.png'

    #    style1 = KML.Style(
    #        KML.IconStyle(
    #            KML.scale('0.4'),
    #            KML.Icon(
    #                KML.href(kurl)
    #            )
    #        ),
    #        KML.LabelStyle(
    #            KML.color('990000ff'),
    #            KML.width('2')
    #        ),
    #        KML.LineStyle(
    #            KML.color('ff0000ff'),
    #            KML.width(2.0)
    #        ),
    #        KML.PolyStyle(
    #            KML.color('997f7fff'),
    #            KML.fill('1'),
    #            KML.outline('1')
    #        ),
    #        id='{}1'.format(name),
    #    )

    return stylen, styleh, stylem


def _buildKML(input, styles, experiments):
    """
        Put all the pieces together...
    """
    # create a KML file skeleton
    doc = _docSkel(input)

    # add the styles
    for style in styles:
        for part in style:
            doc.Document.append(part)

    # add the experiments
    for experiment in experiments.keys():
        doc.Document.append(experiments[experiment])

    return doc


def _writeKML(input, doc):
    """
        create and write to a KML file with the same name as
        the input file.
    """
    kmlName = "{}.kml".format(input.rsplit(".", 1)[0])
    outfile = open(kmlName, 'w')
    print(etree.tostring(doc, pretty_print=True), file=outfile)
    print("\nXML Doc written to {}.\n".format(kmlName))
    outfile.close()


def _gmapsusage(filename):
    """
        Construct a usage string.
    """
    usage = "{} <mapps_image_dump_file> [path_to_mapps_config_file]".format(
        filename)
    # Print usage string.
    print("\n[Usage]: python {}\n".format(usage))


def gmaps(input, configFile):
    """
       Check and deal with command line agruments.
    """

    if NOKMLLIB:
        print("\nOoops! 'gmaps' needs KML_ElementMaker from pykml.factory")
        print("       Try: pip install pykml\n")
    else:
        # # Check input arguments
        # if len(sys.argv) < 2 or len(sys.argv) > 3:
        #     # ... show usage hint...
        #     _gmapsusage(sys.argv[0])
        #     # ... exit!
        #     raise SystemExit(1)

        # input = sys.argv[1]
        # if sys.argv[2]:
        #     configFile = sys.argv[2]
        # else:
        #     configFile = False

        # create containers
        experiments = {}
        filters = {}
        currents = {}
        styles = []

        # Open input file for reading.
        infile = open(input, 'r')

        # Scan through the file line-by-line.
        # TODO: look into moving this for loop into a function
        for line in infile.readlines():
            if line.startswith('Trail'):
                break

            # TODO: Replace the crude pattern matching below with RegEx...
            if line.startswith('Experiment:'):
                expr = line.split(': ')[1].strip()
                if expr not in experiments:
                    experiments[expr] = KML.Folder(KML.name(expr.replace('_',
                                                                         ' ')),
                                                   KML.open('1'),
                                                   id='expr_{}'.format(expr))
                currents['experiment'] = expr

            if line.startswith('Swath:'):
                fltr = line.split(': ')[1].strip()
                if fltr not in filters:
                    filters[fltr] = KML.Folder(KML.name(fltr.replace('_', ' ')),
                                               KML.open('0'),
                                               KML.visibility('1'),
                                               KML.Style(KML.ListStyle(KML.listItemType('checkHideChildren')), id='check-hide-children'),
                                               KML.styleUrl('#check-hide-children'),
                                               id='fltr_{}'.format(fltr))
                    experiments[currents['experiment']].append(filters[fltr])
                currents['filter'] = fltr

            if line.startswith('Orbit:'):
                orbit = line.split()[1].strip()
                currents['orbit'] = orbit

            if line.startswith('Pericenter time (UTC):'):
                peric_time = line.split(': ')[1].strip()
                currents['pericenter time'] = peric_time

            if line.startswith('First image time (UTC):'):
                first_image_t = line.split(': ')[1].strip()
                currents['first image time'] = first_image_t

            if line.startswith('First image time (from pericenter):'):
                first_image_t_frm_peric = line.split(': ')[1].strip()
                currents['first image time from pericenter'] = first_image_t_frm_peric

            if line.startswith('Last image time (UTC):'):
                last_image_t = line.split(': ')[1].strip()
                currents['last image time'] = last_image_t

            if line.startswith('Last image time (from pericenter):'):
                last_image_t_frm_peric = line.split(': ')[1].strip()
                currents['last image time from pericenter'] = last_image_t_frm_peric

            # build an 'image' placemark element
            if line.startswith(' '):
                image = _buildSwath(line, currents)
                filters[currents['filter']].append(image)

        infile.close()

        # the styles for the different swaths
        colors = {}

        # if the MAPPS ini has been provided get colours from it.
        if configFile:
            inifile = open(configFile, 'r')
            for line in inifile.readlines():
                if '\swathColorName=' in line:
                    cHTML = line.rsplit("=#", 1)[1].strip()
                    cKML = '{}{}{}'.format(cHTML[4:6], cHTML[2:4], cHTML[0:2])
                    #print(cHTML, cKML)
                    bits = line.split('\\')[4]
                    #print(bits)
                    colors[bits] = cKML
        else:
            for fltr in filter.keys():
                cKML = binascii.b2a_hex(os.urandom(4))
                colors[fltr] = cKML
                # colors = ['641400E6', '6414F03C', '647828F0',
                #           '647828F0', '64F0FF14', '6478FFF0']

        for fltr in filters.keys():
            styles.append(_makeStyle(fltr, colors[fltr]))

        # build the KML file
        doc = _buildKML(input, styles, experiments)

        # TODO: fix schema checking...
        # schema_gx = Schema("kml22gx.xsd")
        # print(schema_gx.assertValid(doc))

        # write xml structure to kml file
        _writeKML(input, doc)


def splitter(originalFile, no_levels=3, zip=False, inichunk=False,
             demo=False):

    if demo:
        print('\nMAPPS Map Spliter **DEMO**, v0.1, 2014.')
    else:
        print('\nMAPPS Map Spliter, v0.1, 2014.')

    sys.stdout.write("\n   Importing original image...")
    sys.stdout.flush()
    img = Image(filename=originalFile)
    sys.stdout.write(" complete.\n")
    sys.stdout.flush()

    imgwidth = img.width
    imgheight = img.height

    if imgwidth / imgheight != 2:
        print('\n   Ooops!!! The Image Width to Height ratio should be 2!!!')
        return

    else:

        stem = originalFile.split('.')[0]

        if not os.path.exists(stem):
            os.makedirs(stem)
        else:
            print('\n   Uh-oh! The directory {} already exists.'.format(stem))
            if utils.yesno('   Do you want to replace it?'):
                shutil.rmtree(stem)
                os.makedirs(stem)
            else:
                return

        levels = range(1, no_levels + 1)
        for level in levels:

            print('\n   Processing Level {}'.format(level))

            split = 2 ** level
            segs = range(split)
            div = 1. / split

        for h in segs:
            for w in segs:
                w1 = int(imgwidth * div * w)
                w2 = int(imgwidth * div * (w + 1))
                h1 = int(imgheight * div * h)
                h2 = int(imgheight * div * (h + 1))

                imgtmp = img[w1:w2, h1:h2]
                # print(w1, w2, h1, h2)
                imgtmp.transform(resize='1440x720!')
                imgtmp.format = 'jpeg'

                hlevel = '{0:03d}'.format(h + 1)
                wlevel = '{0:03d}'.format(w + 1)
                saveas = os.path.join(stem, '{}_{}_{}_{}.jpg'.format(
                    stem, level, hlevel, wlevel))

                print('      Writing: {}'.format(saveas))
                imgtmp.save(filename=saveas)

                if imgtmp.width != 1440:
                    print('ERROR: image width = {}\n'.format(imgtmp.width))
                if imgtmp.height != 720:
                    print('ERROR: image height = {}\n'.format(imgtmp.height))

        # process input image
        img.transform(resize='1440x720')
        img.format = 'jpeg'
        img.save(filename=os.path.join(stem, '{}_0_001_001.jpg'.format(
            stem)))

        # create ini file segment
        if inichunk:
            utils.inifix(stem, no_levels)

        # zip output
        if zip:
                print('\n   Zipping output to {}.zip'.format(stem))
                zipf = zipfile.ZipFile('{}.zip'.format(stem), 'w')
                utils.zipdir('{}/'.format(stem), zipf)
                zipf.close()
                shutil.rmtree(stem)

        print('\nFinished!\n')

        return


def tabular(input, configFile):
    """
       Check and deal with command line agruments.
    """

    # create containers
    # experiments = {}
    filters = {}
    currents = {}
    styles = []
    first = True

    # Open input file for reading.
    infile = open(input, 'r')

    header = ['seqnr','image time (UTC)','peri reltime','p1 lat','p1 long',
              'p2 lat','p2 long','p3 lat','p3 long','p4 lat','p4 long',
              'type','p5 lat','p5 long','p6 lat','p6 long','p7 lat','p7 long',
              'p8 lat','p8 long','duration','altitude','SC latitude',
              'SC longitude','SC target elev','SC target  azimuth',
              'distance','reflection','Sun tgt elev','Sun tgt azimuth',
              'tgt phase','tgt elongation','local time','img smear',
              'tg phase','perihelion','attdata']

    # Scan through the file line-by-line.
    # TODO: look into moving this for loop into a function
    for line in infile.readlines():
        if line.startswith('Trail'):
            break

        # TODO: Replace the crude pattern matching below with RegEx...
        if line.startswith('Experiment:'):
            expr = line.split(': ')[1].strip()
            currents['experiment'] = expr

        if line.startswith('Swath:'):
            fltr = line.split(': ')[1].strip()
            currents['filter'] = fltr

        if line.startswith('Orbit:'):
            orbit = line.split()[1].strip()
            currents['orbit'] = orbit

        if line.startswith('Pericenter time (UTC):'):
            peric_time = line.split(': ')[1].strip()
            currents['pericenter time'] = peric_time

        if line.startswith('First image time (UTC):'):
            first_image_t = line.split(': ')[1].strip()
            currents['first image time'] = first_image_t

        if line.startswith('First image time (from pericenter):'):
            first_image_t_frm_peric = line.split(': ')[1].strip()
            currents['first image time from pericenter'] = first_image_t_frm_peric

        if line.startswith('Last image time (UTC):'):
            last_image_t = line.split(': ')[1].strip()
            currents['last image time'] = last_image_t

        if line.startswith('Last image time (from pericenter):'):
            last_image_t_frm_peric = line.split(': ')[1].strip()
            currents['last image time from pericenter'] = last_image_t_frm_peric

        if line.startswith('seqnr') and first:
            print(','.join(currents.keys()+header))
            first = False

        # build an 'image' placemark element
        if line.startswith(' '):
            # image = _buildSwath(line, currents)
            # filters[currents['filter']].append(image)
            print(','.join(currents.values()+line.split()))

        infile.close()

        # the styles for the different swaths
        colors = {}

        # if the MAPPS ini has been provided get colours from it.
        if configFile:
            inifile = open(configFile, 'r')
            for line in inifile.readlines():
                if '\swathColorName=' in line:
                    cHTML = line.rsplit("=#", 1)[1].strip()
                    cKML = '{}{}{}'.format(cHTML[4:6], cHTML[2:4], cHTML[0:2])
                    #print(cHTML, cKML)
                    bits = line.split('\\')[4]
                    #print(bits)
                    colors[bits] = cKML
        else:
            for fltr in filter.keys():
                cKML = binascii.b2a_hex(os.urandom(4))
                colors[fltr] = cKML
                # colors = ['641400E6', '6414F03C', '647828F0',
                #           '647828F0', '64F0FF14', '6478FFF0']

        for fltr in filters.keys():
            styles.append(_makeStyle(fltr, colors[fltr]))

        # build the KML file
        # doc = _buildKML(input, styles, experiments)

        # TODO: fix schema checking...
        # schema_gx = Schema("kml22gx.xsd")
        # print(schema_gx.assertValid(doc))

        # write xml structure to kml file
        # _writeKML(input, doc)


# demo wrappers for testing the above...
def gmapsdemo():
    gmaps('imagedatadump.dat', '/Users/jmcaulif/Code/bepic/ESA/bepi_mapps_v65.ini')


def splitterdemo():
    shutil.rmtree("demo")
    splitter("demo.png", demo=True, no_levels=2)


def tabulardemo():
    tabular('../sample_data/imagedatadump.dat', '/Users/jmcaulif/Code/bepic/ESA/bepi_mapps_v65.ini')


if __name__ == '__main__':
    # gmapsdemo()
    # splitterdemo()
    tabulardemo()
