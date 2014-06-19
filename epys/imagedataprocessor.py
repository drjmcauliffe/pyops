def gmaps(input, configFile):
    """
       Check and deal with command line agruments.
    """

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

        if line.startswith('seqnr'):
                print(','.join(currents.keys()))

        # build an 'image' placemark element
        if line.startswith(' '):
            # image = _buildSwath(line, currents)
            # filters[currents['filter']].append(image)
            print(currents.values())

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

if __name__ == '__main__':
    gmaps('/Users/jmcaulif/Code/python/epys/epys/imagedatadump.dat', '/Users/jmcaulif/Code/bepic/ESA/bepi_mapps_v65.ini')
