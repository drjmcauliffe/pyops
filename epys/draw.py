# -*- coding: utf-8 -*-
from utils import getclosest, getorbelts, yesno, planetmu
from datetime import datetime
from PyAstronomy import pyasl
from PyAstronomy import constants as consts
import matplotlib.pyplot as plt
import numpy as np
import svgfig as svg
import inspect
import shutil
import spice
import math
import os

from io import StringIO
import telnetlib
import socket

consts.setSystem('SI')


class Horizons(telnetlib.Telnet, object):

    MERCURY = 199
    VENUS = 299
    EARTH = 399
    MARS = 499
    JUPITER = 599
    SATURN = 699
    URANUS = 799
    NEPTUNE = 899
    PLUTO = 999

    def __init__(self, timeout=socket._GLOBAL_DEFAULT_TIMEOUT):
        super(Horizons, self).__init__("localhost", 6775, timeout)

    def open(self, host, port=0, timeout=socket._GLOBAL_DEFAULT_TIMEOUT):
        super(Horizons, self).open(host, port, timeout)
        # Disable pager on start
        self._check_main()
        self.sendline("page")

    def sendline(self, s=""):
        self.write(s.encode('ascii') + b"\n")

    def elements(self, body, start_date, end_date, delta):
        """Compute osculatory elements, selected a body.

        Columns available:
        0JDCT     Epoch Julian Date, Coordinate Time
        2EC     Eccentricity, e
        3QR     Periapsis distance, q (km)
        4IN     Inclination w.r.t xy-plane, i (degrees)
        5OM     Longitude of Ascending Node, OMEGA, (degrees)
        6W      Argument of Perifocus, w (degrees)
        7Tp     Time of periapsis (Julian day number)
        8N      Mean motion, n (degrees/sec)
        9MA     Mean anomaly, M (degrees)
        10TA     True anomaly, nu (degrees)
        11A      Semi-major axis, a (km)
        12AD     Apoapsis distance (km)
        13PR     Sidereal orbit period (sec)

        # TODO: Better specify time delta
        # TODO: Better specify the body, from a list / dict
        # TODO: Choose reference

        """
        self._check_main()
        self._select_body(body)

        self.expect([b"Observe.*\] :"])
        self.sendline("e")

        idx, _, _ = self.expect([b"Coordinate.*\] :",
                                 b"Use previous center.*\] :"])
        if idx == 1:
            self.sendline("n")
            self.expect([b"Coordinate.*\] :"])

        self.sendline("sun")

        self.expect([b"Reference.*\] :"])
        self.sendline("eclip")

        self.expect([b"Starting.*\] :"])
        self.sendline(str(start_date))
        self.expect([b"Ending.*\] :"])
        self.sendline(str(end_date))
        self.expect([b"Output.*\] :"])
        self.sendline(delta)

        self.expect([b"Accept.*\] :"])
        self.sendline("n")
        self.expect([b"Output reference.*\] :"])
        self.sendline()
        self.expect([b"Output units.*\] :"])
        self.sendline("1")
        self.expect([b"Spreadsheet.*\] :"])
        self.sendline("yes")
        self.expect([b"Label.*\] :"])
        self.sendline("no")
        self.expect([b"Type.*\] :"])
        self.sendline()

        data = self.read_until(b"$$EOE").decode('ascii')
        ephem_str = data.partition("$$SOE")[-1].partition("$$EOE")[0].strip()
        # n_lines = len(ephem_str.splitlines())
        ephem_data = np.loadtxt(StringIO(ephem_str), delimiter=",",
                                usecols=(0, 2, 4, 5, 6, 10, 11), unpack=True)
        jd, ecc, inc, omega, argp, nu, a = ephem_data

        self.expect([b".*Select.* :"])
        self.sendline("N")
        self.expect([b"\n"])

        # return (jd, a, ecc, radians(inc), radians(omega), radians(argp),
        #         radians(nu))

        return (jd, a, ecc, inc, omega, argp, nu)

    def vectors(self, body, start_date, end_date, delta):
        """Compute position and velocity vector."""
        self._check_main()
        self._select_body(body)

        self.expect([b"Observe.*\] :"])
        self.sendline("v")

        idx, _, _ = self.expect([b"Coordinate.*\] :",
                                 b"Use previous center.*\] :"])
        if idx == 1:
            self.sendline("n")
            self.expect([b"Coordinate.*\] :"])

        self.sendline("@sun")

        self.expect([b"Reference.*\] :"])
        self.sendline("eclip")

        self.expect([b"Starting.*\] :"])
        self.sendline(str(start_date))
        self.expect([b"Ending.*\] :"])
        self.sendline(str(end_date))
        self.expect([b"Output.*\] :"])
        self.sendline(delta)

        self.expect([b"Accept.*\] :"])
        self.sendline("n")
        self.expect([b"Output reference.*\] :"])
        self.sendline("J2000")
        self.expect([b"Corrections.* :"])
        self.sendline("1")
        self.expect([b"Output units.*\] :"])
        self.sendline("1")
        self.expect([b"Spreadsheet.*\] :"])
        self.sendline("yes")
        self.expect([b"Label.*\] :"])
        self.sendline("no")
        self.expect([b"Select output table.*\] :"])
        self.sendline("2")

        data = self.read_until(b"$$EOE").decode('ascii')
        ephem_str = data.partition("$$SOE")[-1].partition("$$EOE")[0].strip()
        # n_lines = len(ephem_str.splitlines())
        ephem_data = np.loadtxt(StringIO(ephem_str), delimiter=",",
                                usecols=(0,) + tuple(range(2, 8)), unpack=True)
        jd, x, y, z, vx, vy, vz = ephem_data
        r = np.column_stack((x, y, z))
        v = np.column_stack((vx, vy, vz))

        self.expect([b".*Select.* :"])
        self.sendline("N")
        self.expect([b"\n"])

        return jd, r, v

    def _select_body(self, body):
        self.sendline(str(body))
        self.expect([b"Select .*, \?, <cr>:"])
        self.sendline("e")
        self.expect([b"\n"])

    def _check_main(self):
        idx, _, _ = self.expect([b"Horizons>"])
        if idx == -1:
            raise RuntimeError("I am lost!")


def _gatherhorizonsdata(delta="1d", scale=15):

    print("Building orbit for planets from JPL Horizons...")

    start_date = datetime(2024, 5, 7)
    end_date = datetime(2025, 5, 6)

    jpl = Horizons()
    rlist = []
    rmins = []

    plnts = ("MERCURY", "VENUS", "EARTH")

    for planet in plnts:

        print("     > {}".format(planet))

        # Planet state and velocity vectors
        jd, r, v = jpl.vectors(getattr(jpl, planet), start_date, end_date,
                               delta)

        jd, a, ecc, inc, omega, argp, nu = jpl.elements(getattr(jpl, planet),
                                                        start_date,
                                                        end_date,
                                                        delta)

        print(jd, a, ecc, inc, omega, argp, nu)

        # set AU in kilometers
        AU = 1  # consts.AU / 1000  # 149597871.

        scale = 1

        rv = [math.sqrt(x ** 2 + y ** 2 + z ** 2) for (x, y, z) in r]
        xy = [((x / AU) * scale, (y / AU) * scale) for (x, y) in r[:, 0:2]]

        i = rv.index(min(rv))

        rmin = math.degrees(math.atan2(r[i, 1], r[i, 0]))

        rmins.append(rmin)
        rlist.append(xy)

    return rlist, rmins, jd.tolist()


def _gatherorbitdata(delta="1d", scale=15, verbose=False):

    print("Building orbit for planets with SPICE...")

    spice.kclear()

    # Load the kernels that this program requires.
    spice.furnsh('epys.mk')

    # convert starting epoch to ET
    et0 = spice.str2et('2024/05/07 00:00')
    rate = 24 * 2  # Every 30 mins
    days = [(et0 + (day * (86400 / rate))) for day in range(366 * rate)]

    # internal variables and constants
    planets = ("MERCURY", "VENUS", "EARTH")
    AU = consts.AU / 1000.  # AU [km]
    argps = []
    argpxys = []
    xyvecs = []
    nuvecs = []

    for planet in planets:

        print("     > {}".format(planet))

        dates = []
        rvec = []   # vector of centric radii
        xyvec = []  # vector of (x,y) coordinates
        nuvec = []  # vector of nu (True Anomaly) values
        incvec = []  # vector of inclination values

        for et in days:

            if verbose:
                print('ET Seconds Past J2000: {}'.format(et))

            # Compute the apparent state of MERCURY as seen from
            # the SUN in ECLIPJ2000
            starg, ltime = spice.spkezr(planet, et, 'ECLIPJ2000',
                                        'NONE', 'SUN')

            x, y, z, vx, vy, vz = [el / AU * scale for el in starg]
            r = math.sqrt(x ** 2 + y ** 2 + z ** 2)

            if verbose:
                print('\nApparent state of MERCURY as seen from',
                      ' Sun in the J2000:')
                print(' X = {:10.4f} km (LT+S)'.format(x))
                print(' Y = {:10.4f} km (LT+S)'.format(y))
                print(' Z = {:10.4f} km (LT+S)'.format(z))
                print('VX = {:10.4f} km/s (LT+S)'.format(vx))
                print('VY = {:10.4f} km/s (LT+S)'.format(vy))
                print('VZ = {:10.4f} km/s (LT+S)'.format(vz))

            # calculate orbital elements from the starg state vector
            elts = spice.oscelt(starg, et, planetmu('Sun'))

            # define a solver for Kepler's equation
            ks = pyasl.MarkleyKESolver()

            # solve for the Eccentric Anomaly (E) with the
            # Mean Anomaly (M = elts[5]) and the
            # Eccentricity (ecc = elts[1])
            E = ks.getE(elts[5], elts[1])

            # calculate the True Anomaly (nu) from E and ecc (elts[1])
            nuarg1 = math.sqrt(1 - elts[1]) * math.cos(E / 2)
            nuarg2 = math.sqrt(1 + elts[1]) * math.sin(E / 2)

            # atan2 in python needs the arguments as (y,x)
            # rather than (x,y) ...?
            nu = 2 * math.atan2(nuarg2, nuarg1)

            rvec.append(r)  # append r for each day
            xyvec.append((x, y))  # append (x,y) coords for each day
            nuvec.append(nu)  # append True anomaly for each day

            # build date in ISO format
            date = '{} {}'.format(spice.et2utc(et, 'ISOC', 0).split('T')[0],
                                  spice.et2utc(et, 'ISOC', 0).split('T')[1])
            dates.append(date)  # append date for each day
            incvec.append(elts[2])  # append inc. for each day (rads)

            # print(date, nu * spice.dpr(), x, y, z, r, elts[0])

        # for this planet find the argument of pericenter (argp):
        # find the index of the min. r value for calculated range.
        argpi = rvec.index(min(rvec))

        # calculate argp x and y values and argp using atan2
        argpxy = (xyvec[argpi][0], xyvec[argpi][1] * math.cos(incvec[argpi]))
        argp = math.degrees(math.atan2(argpxy[1], argpxy[0]))

        argpxys.append(argpxy)  # append argp (x,y) coords.
        argps.append(argp)  # append argp
        xyvecs.append(xyvec)  # append (x,y) coords. vector
        nuvecs.append(nuvec)  # append true anomaly vector

    spice.kclear()

    return days, dates, xyvecs, argps, argpxys, nuvecs


def _frmline(a, b, c, d, line_op=1.0):
    return svg.Line(a, b, c, d, stroke_width="0.15pt",
                    stroke_dasharray="2, 2", stroke_opacity=line_op)


def _gradient(id, colors, gradrot, rotang, x, y):

    # TODO: Fix the gradient rotation...

    # print("Building gradient for {}".format(id))

    xp = x * math.cos(math.radians(rotang)) - \
        y * math.sin(math.radians(rotang))
    yp = x * math.sin(math.radians(rotang)) + \
        y * math.cos(math.radians(rotang))

    return svg.SVG("linearGradient",
                   svg.SVG("stop", stop_color=colors[0], stop_opacity=1,
                           offset="40%"),
                   svg.SVG("stop", stop_color=colors[1], stop_opacity=1,
                           offset="60%"),
                   x1="0%", y1="0%", x2="100%", y2="0%",
                   spreadMethod="pad",
                   id="{}Grad".format(id),
                   gradientTransform="rotate({}, {}, {})".format(45, xp, yp))


def _outerframe(date, frmSize=15, frm_op=0.5, diag_scl=0.65, mpoargp=False,
                frm_font_size=3, frm_ticks=8, frm_miniticks=False):

    # print("Building outer frame...")
    callerfunc = inspect.stack()[1][3]

    frmSize = frmSize * 1.2

    frm = svg.LineAxis(frmSize, 0, frmSize, 2 * math.pi, 0, 2 * math.pi)
    frm.text_start = -2.5
    frm.text_angle = 180.
    frm.text_attr["font-size"] = frm_font_size
    frm.text_attr["opacity"] = frm_op
    frm.attr["stroke_opacity"] = frm_op
    frm.ticks = [x * 2 * math.pi / frm_ticks for x in range(frm_ticks)]
    if callerfunc == 'planetsplot':
        frm.labels = lambda x: "%g" % (x * 180 / math.pi)
    else:
        frm.labels = False
    if frm_miniticks:
        frm_miniticks = [x * 2 * math.pi / frm_ticks / 9 for x in
                         range(frm_ticks * 9)]
    frm.miniticks = frm_miniticks

    # Makes a circle out of the Line Axis.
    frm_plot = svg.Fig(frm, trans="x*cos(y), x*sin(y)")

    # Draw the vertical ...
    xs = 0.9
    frmLine1 = _frmline(0, -frmSize * xs, 0, frmSize * xs, line_op=frm_op)
    # ... and horizontal frame lines through the sun.
    frmLine2 = _frmline(-frmSize * xs, 0, frmSize * xs, 0, line_op=frm_op)
    # Draw the diagonal frame lines.
    frmLine3 = _frmline(-frmSize * diag_scl, -frmSize * diag_scl,
                        frmSize * diag_scl, frmSize * diag_scl,
                        line_op=frm_op)
    frmLine4 = _frmline(-frmSize * diag_scl, frmSize * diag_scl,
                        frmSize * diag_scl, -frmSize * diag_scl,
                        line_op=frm_op)

    # And there was light...
    sun_ball = _sun()

    # Metadata
    callerfunc = inspect.stack()[1][3]
    if callerfunc == 'planetsplot':
        titletag = 'Planetary Constellation Mid-Season'
    if callerfunc == 'mpoplot':
        titletag = 'MPO Orbit Mid-Season'

    refdata = svg.Fig()
    textop = 6.0

    # TODO: fix the messy way the placement x, y are defined.
    metatitle = svg.Text(-frmSize - 3.5, frmSize + 3, titletag,
                         font_size=frm_font_size, opacity=textop,
                         text_anchor="start")
    metadate = svg.Text(-frmSize - 3.5, frmSize + 1, "{}".format(date),
                        font_size=frm_font_size, opacity=textop,
                        text_anchor="start")
    if callerfunc == 'mpoplot' and mpoargp:
        metaargp = svg.Text(-frmSize - 3.5, frmSize - 1,
                            "Arg. Periherm: {:6.1f}degsym".format(mpoargp),
                            font_size=frm_font_size, opacity=textop,
                            text_anchor="start")
    else:
        metaargp = svg.Fig()

    if callerfunc == 'planetsplot':
        xy = (-frmSize + 6.8, -frmSize - 1.8)
        reforb, grad = _planetdiag("MERCURY", xy, 0)

        reforbtext1 = svg.Text(-frmSize + 4, -frmSize - 2, "Descending",
                               font_size=frm_font_size, opacity=textop,
                               text_anchor="end")

        reforbtext2 = svg.Text(-frmSize + 9, -frmSize - 2.0, "Ascending",
                               font_size=frm_font_size, opacity=textop,
                               text_anchor="start")
        refdata = svg.Fig(reforb, reforbtext1, reforbtext2)

    return svg.Fig(frm_plot,
                   svg.Fig(frmLine1, frmLine2, frmLine3, frmLine4),
                   sun_ball,
                   metatitle,
                   metadate,
                   metaargp,
                   refdata)


def _orbitdot(a, b, theta, r_dot_adj=0.1, color="#C8C5E2", r_dot_size=0.6,
              rot_x=0.0, rot_y=0.0, dot_op=1.0, dot_str_op=1.0):
    if theta > 180:
        r_dot_adj = r_dot_adj * -1.0
    r_dot = _rellipse(a, b, theta)  # +r_dot_adj*sin(theta)
    r_trans = svg.rotate(theta, rot_x, rot_y)
    # print(r_dot)
    ret_dot = svg.Fig(svg.Dots([(r_dot, 0)],
                      svg.make_symbol("dot_{}_{}".format(theta, color),
                                      fill=color, fill_opacity=dot_op,
                                      stroke="black", stroke_width="0.15pt",
                                      stroke_opacity=dot_str_op),
                      r_dot_size, r_dot_size), trans=r_trans)
    #print(defs)
    return ret_dot


def _planetdiag(name, rpos, rotang=0.0, orb_scl=1.0, frmSizecl=10.0,
                diag_op=1.0):

    # print("Building {} diagram...".format(name))

    colors = []

    if name == "MERCURY":
        colors = ["#C8C5E2", "#373163"]
    if name == "VENUS":
        diag_op = 0.4
        colors = ["#EDE051", "#393506"]
    if name == "EARTH":
        colors = ["#00AFEF", "#003C52"]

    # colorurl="url(#{}Grad)".format(name[0:4].lower())

    # Scale the position vector ...
    # rpos = [x*frmSizecl*orb_scl for x in rpos]

    # Simplify ...
    r_x = rpos[0]
    r_y = rpos[1]

    gradrot = math.degrees(math.atan2(r_y, r_x))

    # Build a white ball for background ...
    ball_bg = _planetdot(name, rpos, r_dot_size=2.0 * orb_scl,
                         dot_color="white", dot_str_op=diag_op)
    # ... and a color ball for foreground.
    ball_fg = _planetdot(name, rpos, r_dot_size=2.0 * orb_scl,
                         dot_color=colors[0], dot_op=diag_op,
                         dot_str_op=diag_op)

    # Stack coloured ball on top of white background ball...
    ball = svg.Fig(ball_bg, ball_fg)

    grad = _gradient(name[0:4].lower(), colors, gradrot, rotang, r_x, r_y)

    if name == "MERCURY":

        # print("Buidling MPO orbit schematic...")

        # MPO line scaling factor
        mpo_line_sf = 2.0

        # MPO line start and end points
        mpo_line_st = r_x - orb_scl * mpo_line_sf
        mpo_line_en = r_x + orb_scl * mpo_line_sf * 0.720811474

        node_size = 0.15

        x1 = mpo_line_st - node_size
        x2 = mpo_line_st + node_size
        y1 = r_y - node_size
        y2 = r_y + node_size
        dec_node = svg.Fig(svg.Rect(x1=x1, y1=y1, x2=x2, y2=y2, fill="black"),
                           trans=svg.rotate(0, mpo_line_st, r_y))

        x1 = mpo_line_en - node_size
        x2 = mpo_line_en + node_size
        y1 = r_y - node_size
        y2 = r_y + node_size
        asc_node = svg.Fig(svg.Rect(x1=x1, y1=y1, x2=x2, y2=y2, fill="black"),
                           trans=svg.rotate(45, mpo_line_en, r_y))

        mpo_line = svg.Fig(svg.Line(mpo_line_st, r_y, mpo_line_en, r_y,
                           stroke_width="0.15pt",),
                           asc_node,
                           dec_node,
                           trans=svg.rotate(-rotang, r_x, r_y))

        # r_trans = rotate(theta, 0, 0)
        ball.d.append(svg.Fig(mpo_line))

    return svg.Fig(ball, trans=svg.rotate(rotang, 0, 0)), grad


def _planetdot(name, rpos, dot_color="#C8C5E2", r_dot_size=0.6,
               dot_op=1.0, dot_str_op=1.0):

    r_x = rpos[0]
    r_y = rpos[1]
    cname = dot_color.replace("#", "")

    ret_dot = svg.Fig(svg.Dots([(r_x, r_y)],
                      svg.make_symbol("dot_{}_{}".format(name, cname),
                                      fill=dot_color, fill_opacity=dot_op,
                                      stroke="black", stroke_width="0.15pt",
                                      stroke_opacity=dot_str_op),
                      r_dot_size, r_dot_size))

    return ret_dot


def _planetdotang(a, b, theta, r_dot_adj=0.23, dot_color="#C8C5E2",
                  r_dot_size=0.6, rot_x=0.0, rot_y=0.0, dot_op=1.0,
                  dot_str_op=1.0):
    if theta < 180:
        r_dot_adj = r_dot_adj * -1.0
    r_dot = _rellipse(a, b, theta)
    r_trans = svg.rotate(theta, rot_x, rot_y)
    # print(r_dot)
    ret_dot = svg.Fig(svg.Dots([(r_dot, 0)],
                      svg.make_symbol("dot_{}_{}".format(theta, dot_color),
                                      fill=dot_color, fill_opacity=dot_op,
                                      stroke="black", stroke_width="0.15pt",
                                      stroke_opacity=dot_str_op),
                      r_dot_size, r_dot_size), trans=r_trans)
    # print(theta)
    # print(r_dot*cos(radians(theta)), r_dot*sin(radians(theta)))
    return ret_dot


def _rellipse(a, b, theta):
    rret = (b ** 2) / (a - math.sqrt(a ** 2 - b ** 2) *
                       math.cos(math.radians(180 - theta)))
    return rret


def _sun(id="Sun", posx=0, posy=0, size=1.5, fill="yellow",
         stroke="orange", stroke_width="0.1pt"):
    return svg.Dots([(0, 0)], svg.make_symbol(id, stroke=stroke,
                    fill=fill, stroke_width=stroke_width), size, size)


def planetsplot(userdates=None, delta="1d", master_scale=15, demo=False,
                showplots=False):
    """
    ... explain what this does...
    """

    outdir = '../sample_data/output'
    # if demo:
    #     shutil.rmtree(outdir)
    #     os.makedirs(outdir)
    # else:
    #     if not os.path.exists(outdir):
    #         os.makedirs(outdir)
    #     else:
    #         print('\n   Uh-oh! The directory {} already exists.'.format(
    #             outdir))
    #         if yesno('   Do you want to replace it?'):
    #             shutil.rmtree(outdir)
    #             os.makedirs(outdir)
    #         else:
    #             return

    orbitdata = _gatherorbitdata(delta=delta, scale=master_scale)
    ets, dates, orbits, argps, argpxys, nus = orbitdata

    if userdates is None:
        userdates = dates

    if showplots:
        plt.subplot(1, 1, 1)
        for xy in orbits:
            plt.plot([x[0] for x in xy], [y[1] for y in xy],
                     'rx', label='SPICE')
        for xy in argpxys:
            plt.plot(xy[0], xy[1], 'go')
        plt.show()

    if len(orbits[0]) == len(dates) == len(ets):

        # This rotation will put the Hermean perihelion on the X-axis.
        rotang = -argps[0]

        # Load the kernels that this program requires.
        spice.kclear()
        spice.furnsh('epys.mk')

        # A graphic will be created for each 'date' in 'userdates':
        for date in userdates:

            # get the position-index of the 'et' in the 'orbitdata' list
            # of 'ets' that is closest to the 'date' in the 'userdates'
            et = spice.str2et(date)
            dx = ets.index(getclosest(ets, et))

            # -- Outer frame -------------------------------------------------

            # Opacity of degree frame and Venus graphic
            frame_op = 0.8

            # Process calendar time strings
            date = '{} {}'.format(spice.et2utc(et, 'ISOC', 0).split('T')[0],
                                  spice.et2utc(et, 'ISOC', 0).split('T')[1])
            edate, etime = date.split()
            eyear = "{}".format(edate.split('-')[0])
            emonth = "{0:02d}".format(int(edate.split('-')[1]))
            eday = "{0:02d}".format(int(edate.split('-')[2]))
            epoch = "{}/{}/{}".format(eday, emonth, eyear)
            ep_name = "{}{}{}_{}".format(eyear, emonth, eday,
                                         etime.replace(':', ''))

            frame = _outerframe(epoch, frmSize=master_scale, frm_op=frame_op)

            # -- First Point of Aires ----------------------------------------

            # merc_loan = 48.331
            # merc_argp = 29.124
            arend = svg.make_marker("fopa_arrowend", "arrow_end",
                                    fill_opacity=0.4)

            x1, y1 = 10, 0
            x2, y2 = master_scale * 1.3, 0

            fpoa = svg.Line(x1, y1, x2, y2, stroke_width=".4pt",
                            stroke_opacity=0.4, arrow_end=arend)

            xp = (x2 * math.cos(math.radians(rotang)) -
                  y2 * math.sin(math.radians(rotang)))
            yp = (x2 * math.sin(math.radians(rotang)) +
                  y2 * math.cos(math.radians(rotang)))

            fpoa_text = svg.Text(xp + 6.5, yp - 1.0, "First Point of Aries",
                                 font_size=3, opacity=0.75)
            fpoa = svg.Fig(svg.Fig(fpoa, trans=svg.rotate(rotang, 0, 0)),
                           fpoa_text)

            # -- Some containers ---------------------------------------------

            orbs = []
            circles = []
            defs = svg.SVG("defs")

            # -- Orbit circles -----------------------------------------------

            # Build the SVG for each orbit.
            for orbit in orbits:

                if orbits.index(orbit) == 1:
                    orbit_op = 0.4
                else:
                    orbit_op = 1.0

                # Mercury's orbit will have perihelion on the X-axis
                circles.append(svg.Fig(svg.Poly(orbit, stroke_width=".25pt",
                                                stroke_opacity=orbit_op),
                                       trans=svg.rotate(rotang, 0, 0)))

            # -- Planet orbs -------------------------------------------------

            points = [orbits[0][dx], orbits[1][dx], orbits[2][dx]]

            # Build the planet orb for each planet for this chart.
            for point in points:

                # Planetary inputs ...
                if points.index(point) == 0:
                    name = "MERCURY"
                    nu = math.degrees(math.atan2(point[1], point[0])) + rotang
                    if nu < 0:
                        nu = nu + 360
                    # print(nu, nu-rotang, rotang)
                    nu = "{0:03d}".format(int(nu))
                if points.index(point) == 1:
                    name = "VENUS"
                if points.index(point) == 2:
                    name = "EARTH"

                # point_r  = [x/AU for x in point]

                orb, grad = _planetdiag(name, point, rotang)

                orbs.append(orb)
                defs.append(grad)

            # -- Build final figure ------------------------------------------

            wa = master_scale * 1.5
            svgout = svg.Fig(fpoa, frame,
                             circles[0], circles[1], circles[2],
                             orbs[0], orbs[1], orbs[2]
                             ).SVG(svg.window(-wa, wa, -wa, wa))

            svgout.prepend(defs)
            svgout.save(os.path.join(outdir,
                                     "merc_orbit_plot_{}_{}.svg".format(
                                         ep_name, nu)))

        spice.kclear()

    else:
        # You'll jump to hear if the epochs for all 3 planets are not equal.
        print("There is an epoch error between the planet time values...")


def mpoplot(userdates, master_scale=15, demo=False):
    """
    ... explain what this does...
    """

    outdir = '../sample_data/output'
    # if demo:
    #     shutil.rmtree(outdir)
    #     os.makedirs(outdir)
    # else:
    #     if not os.path.exists(outdir):
    #         os.makedirs(outdir)
    #     else:
    #         print('\n   Uh-oh! The directory {} already exists.'.format(
    #             outdir))
    #         if yesno('   Do you want to replace it?'):
    #             shutil.rmtree(outdir)
    #             os.makedirs(outdir)
    #         else:
    #             return

    # Clear and load the kernels that this program requires.
    spice.kclear()
    spice.furnsh('epys.mk')

    # A graphic will be created for each 'date' in 'dates':
    for date in userdates:

        et = spice.str2et(date)
        datestr = (spice.et2utc(et, 'ISOC', 0))

        # -- Outer frame -------------------------------------------------

        dist_scl = 250.0

        elts = getorbelts(date)
        arg_peri = elts[4]

        # Opacity of degree frame and Venus graphic
        frame_op = 0.5

        # # Process JD time into calendar time strings
        # datestr = spice.et2utc(et, 'ISOC', 0)
        date = '{} {}'.format(datestr.split('T')[0],
                              datestr.split('T')[1])
        edate, etime = date.split()
        eyear = "{}".format(edate.split('-')[0])
        emonth = "{0:02d}".format(int(edate.split('-')[1]))
        eday = "{0:02d}".format(int(edate.split('-')[2]))
        epoch = "{}/{}/{}".format(eday, emonth, eyear)
        ep_name = "{}{}{}".format(eyear, emonth, eday)

        frame = _outerframe(epoch, frmSize=master_scale, frm_op=frame_op,
                            mpoargp=arg_peri)

        # -- Mercury Planet --------------------------------------------------

        # tru_ano = 90
        # look_from = 270

        # x1 = "{}%".format((100*math.sin(math.radians((tru_ano+90)/2.))))
        # x2 = "{}%".format(100-(100*sin(radians((tru_ano+90)/2.))))

        angs = range(0, 360, 1)

        plt.plot(angs, ["{}".format((100 * math.sin(math.radians(x / 2))))
                        for x in angs], 'yo-')
        plt.plot(angs, ["{}".format(100 - (100 *
                        math.sin(math.radians(x / 2)))) for x in angs], 'ro-')
        # plt.show()

        stop1 = "#C8C5E2"
        # stop2 = "#373163"

        defs = svg.SVG("defs",
                       svg.SVG("linearGradient",
                               svg.SVG("stop", stop_color=stop1,
                                       stop_opacity=1, offset="45%"),
                               svg.SVG("stop", stop_color=stop1,
                                       stop_opacity=1, offset="55%"),
                               x1="0%", y1="0%", x2="100%", y2="0%",
                               spreadMethod="pad",
                               id="mercGrad")
                       )

        # defs = svg.SVG('defs',
        #                svg.SVG('radialGradient',
        #                        svg.SVG('stop',
        #                                stop_color=stop1,
        #                                stop_opacity=1,
        #                                offset='38%'),
        #                        svg.SVG('stop',
        #                                stop_color=stop2,
        #                                stop_opacity=1,
        #                                offset='40%'),
        #                        cx='50%', cy='50%',
        #                        fx='230%', fy='50%',
        #                        r='300%',
        #                        spreadMethod='pad',
        #                        id='mercGrad')
        #                )

        merc_rad = 2439.99  # km
        merc_rad_scl = merc_rad / dist_scl
        merc_ball = svg.Ellipse(0, 0, 0, merc_rad_scl, merc_rad_scl,
                                fill="url(#mercGrad)", stroke_width="0.15pt")

        # -- MPO Orbit --

        mpo_orb_ecc = 0.163229
        mpo_orb_sma = 3394.0  # km
        mpo_orb_sma_scl = mpo_orb_sma / dist_scl
        mpo_orb_smi_scl = mpo_orb_sma_scl * math.sqrt(1 - mpo_orb_ecc ** 2)

        # Make things cleaner
        a = mpo_orb_sma_scl
        b = mpo_orb_smi_scl

        mpo_orb = svg.Ellipse(-math.sqrt(a ** 2 - b ** 2), 0, 0, a, b,
                              fill="none", stroke_width="0.25pt")
        # apof = 8
        mpo_orb_apses = svg.Line(-_rellipse(a, b, 180) - 5, 0,
                                 _rellipse(a, b, 0) + 10, 0,
                                 stroke_width="0.15pt",
                                 stroke_dasharray="2, 2")

        dot_angs = range(0, 360, 20)
        dots = [_orbitdot(a, b, x, color="black") for x in dot_angs]
        mpo_orb_dots = svg.Fig()
        for dot in dots:
            mpo_orb_dots.d.append(dot)

        mpo_orb_trans = svg.rotate(arg_peri, 0, 0)
        mpo_orb_plot = svg.Fig(mpo_orb, mpo_orb_apses, mpo_orb_dots,
                               trans=mpo_orb_trans)

        # -- Direction arrow -------------------------------------------------

        dirarend = svg.make_marker("dirarrowend", "arrow_end",
                                   fill_opacity=0.2)
        dirarend.attr["markerWidth"] = 7.5

        x1, y1 = master_scale + 1, 0.4,
        x2, y2 = master_scale + 1, 1

        dirarwstrt = svg.Line(x1, y1, x2, y2, stroke_width=".4pt",
                              stroke_opacity=0.2, arrow_end=dirarend)

        dirarw = svg.Fig(dirarwstrt, trans="x*cos(y), x*sin(y)")

        # -- Apsis view ------------------------------------------------------

        apvx, apvy = master_scale + 3, -master_scale - 3
        apsisviewball = svg.Ellipse(apvx, apvy,
                                    0, merc_rad_scl * 0.25,
                                    merc_rad_scl * 0.25,
                                    fill="url(#mercGrad)",
                                    stroke_width="0.15pt")

        apsisviewlats = svg.Fig()

        for x in range(-9, 10, 3):

            hscl = math.sin(math.radians(x * 10))
            wscl = math.cos(math.radians(x * 10))

            x1 = apvx - (merc_rad_scl * 0.25 * wscl)
            y1 = apvy + (merc_rad_scl * 0.25 * hscl)
            x2 = apvx + (merc_rad_scl * 0.25 * wscl)
            y2 = apvy + (merc_rad_scl * 0.25 * hscl)

            apsisviewlats.d.append(svg.Line(x1, y1, x2, y2,
                                   stroke_width=".2pt",
                                   stroke_opacity=0.4))

        apvarend = svg.make_marker("apvarrowend",
                                   "arrow_end",
                                   fill_opacity=0.6)
        apvarend.attr["markerWidth"] = 3.0
        apvarend.attr["markerHeight"] = 3.0

        x1, y1 = apvx, apvy - 3
        x2, y2 = apvx, apvy + 3
        apsisvieworbit = svg.Line(x1, y1, x2, y2,
                                  stroke_width=".4pt",
                                  stroke_opacity=0.6,
                                  arrow_end=apvarend)

        xd = apvx
        yd = apvy + (merc_rad_scl * 0.25 * math.sin(math.radians(arg_peri)))
        apsisviewdot = svg.Fig(svg.Dots([(xd, yd)],
                                        svg.make_symbol("apsisdot",
                                                        fill="black",
                                                        fill_opacity=0.6
                                                        ),
                                        0.6, 0.6
                                        )
                               )

        apsisview = svg.Fig(apsisviewball,
                            apsisviewlats,
                            apsisvieworbit,
                            apsisviewdot)

        # -- Build final figure ----------------------------------------------

        wa = master_scale * 1.5
        svgout = svg.Fig(frame,
                         merc_ball,
                         mpo_orb_plot,
                         dirarw,
                         apsisview
                         ).SVG(svg.window(-wa, wa, -wa, wa))

        svgout.prepend(defs)

        argp = int(arg_peri)
        svgout.save(os.path.join(outdir,
                                 "mpo_orbit_plot_{}_{}.svg".format(ep_name,
                                                                   argp)
                                 )
                    )


if __name__ == '__main__':

    # I want plots for these dates...
    dates = ("2024-May-07 00:00", "2024-May-09 14:31", "2024-May-28 09:14",
             "2024-Jun-13 15:50", "2024-Jun-29 22:26", "2024-Jul-27 15:28",
             "2024-Aug-24 08:30", "2024-Sep-09 15:06", "2024-Sep-25 21:42",
             "2024-Oct-23 14:44", "2024-Nov-20 07:46", "2024-Dec-06 14:22",
             "2024-Dec-22 20:58", "2025-Jan-19 14:00", "2025-Feb-16 07:02",
             "2025-Mar-04 13:38", "2025-Mar-20 20:14", "2025-Apr-17 13:16",
             "2025-May-03 02:19")
    # dates = ("2024-May-07 00:00", "2024-May-09 14:31")

    # ... some planetary constellation plots...
    planetsplot(userdates=dates, demo=True)

    # ... and some spacecraft orbit plots.
    # mpoplot(dates, demo=True)
