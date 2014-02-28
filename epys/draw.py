from svgfig import *
from math import *
from jplephem import *
import numpy as np
from jdcal import *


def _buildorbits(delta = "1d", scale = 15):

    print("Building orbit for planets...")

    start_date = datetime(2024, 1, 1)
    end_date = datetime(2025, 1, 1)

    jpl = Horizons()
    rlist = []
    rmins = []

    plnts = ("MERCURY", "VENUS", "EARTH")

    for planet in plnts:

        print("     > {}".format(planet))

        # Planet state and velocity vectors
        jd, r, v = jpl.vectors(getattr(jpl, planet),
                                start_date,
                                end_date,
                                delta)

        AU = 149597871.

        rv = [sqrt(x**2+y**2+z**2) for (x,y,z) in r]
        xy = [((x/AU)*scale, (y/AU)*scale) for (x,y) in r[:,0:2]]

        i = rv.index(min(rv))

        rmin = degrees(atan2(r[i,1], r[i,0]))

        rmins.append(rmin)
        rlist.append(xy)

    return rlist, rmins, jd.tolist()


def _frmline(a, b, c, d, line_op = 1.0):
    return Line(a, b, c, d, stroke_width="0.15pt",
                stroke_dasharray="2, 2", stroke_opacity=line_op)


def _getpos(start, end = False, delta = "1d"):

    # print("Gettings positions for given dates...")

    # Split start date and create datetime object...
    year1, month1, chart1 = start.split('/')
    start_date = datetime(int(year1), int(month1), int(chart1))

    # If an end date is not given add 1 chart to the start date and use
    # this as the end date...
    # TODO: update jpl_ephem to deal with single dates.
    if not end:
        end_date = datetime(int(year1), int(month1), int(chart1)+1)
    else:
        # If an end date is given deal with it...
        year2, month2, chart2 = end.split('/')
        end_date = datetime(int(year2), int(month2), int(chart2))

    jpl = Horizons()
    rlist = []

    plnts = ("MERCURY", "VENUS", "EARTH")

    for planet in plnts:

        print("     > {}".format(planet))

        # Planet osculating elements
        jd, a, ecc, inc, om, ap, nu = jpl.elements(getattr(jpl, planet),
                                                    start_date,
                                                    end_date,
                                                    delta)

        # Planet state and velocity vectors
        jd, r, v = jpl.vectors(getattr(jpl, planet),
                                start_date,
                                end_date,
                                delta)

        if not end:
            rlist.append((planet, jd[0], a[0], ecc[0], inc[0], om[0],
                                ap[0], nu[0], r[0], v[0]))
        else:
            for chart in jd:
                i = np.where(jd==chart)
                mylist = (planet, jd[i][0], a[i][0], ecc[i][0], inc[i][0],
                            om[i][0], ap[i][0], nu[i][0], r[i][0].tolist(),
                            v[i][0].tolist())
                rlist.append(mylist)

    rlist.sort(key=lambda x: x[1])

    return [rlist[i:i+len(plnts)] for i in range(0, len(rlist), len(plnts))]


def _gradient(id, colors, gradrot, rotang, x, y):

    # TODO: Fix the gradient rotation...

    # print("Building gradient for {}".format(id))

    xp = x*cos(radians(rotang)) - y*sin(radians(rotang))
    yp = x*sin(radians(rotang)) + y*cos(radians(rotang))

    return SVG("linearGradient",
                SVG("stop", stop_color=colors[0], stop_opacity=1,
                    offset="40%"),
                SVG("stop", stop_color=colors[1], stop_opacity=1,
                    offset="60%"),
                x1="0%", y1="0%", x2="100%", y2="0%",
                spreadMethod="pad",
                id="{}Grad".format(id),
                gradientTransform="rotate({}, {}, {})".format(45, xp, yp))


def _outerframe(date, frmSize = 15, frm_op = 0.5, diag_scl = 0.65,
    frm_font_size = 3, frm_ticks = 8, frm_miniticks =  False):

    # print("Building outer frame...")

    frmSize = frmSize*1.2

    frm = LineAxis(frmSize, 0, frmSize, 2*pi, 0, 2*pi)
    frm.text_start = -2.5
    frm.text_angle = 180.
    frm.text_attr["font-size"] = frm_font_size
    frm.text_attr["opacity"] = frm_op
    frm.attr["stroke_opacity"] = frm_op
    frm.ticks = [x*2*pi/frm_ticks for x in range(frm_ticks)]
    frm.labels = lambda x: "%g" % (x*180/pi)

    if frm_miniticks:
        frm_miniticks = [x*2*pi/frm_ticks/9 for x in range(frm_ticks*9)]

    frm.miniticks = frm_miniticks

    # Makes a circle out of the Line Axis.
    frm_plot = Fig(frm, trans="x*cos(y), x*sin(y)")

    # Draw the vertical ...
    xs = 0.9
    frmLine1 = _frmline(0, -frmSize*xs, 0, frmSize*xs, line_op = frm_op)
    # ... and horizontal frame lines through the sun.
    frmLine2 = _frmline(-frmSize*xs, 0, frmSize*xs, 0, line_op = frm_op)
    # Draw the diagonal frame lines.
    frmLine3 = _frmline(-frmSize*diag_scl, -frmSize*diag_scl,
                              frmSize*diag_scl,  frmSize*diag_scl,
                              line_op = frm_op)
    frmLine4 = _frmline(-frmSize*diag_scl,  frmSize*diag_scl,
                              frmSize*diag_scl, -frmSize*diag_scl,
                              line_op = frm_op)

    # And there was light...
    sun_ball = _sun()

    meta_data = Text(-frmSize+2, frmSize+1, "Date: {}".format(date),
                        font_size = frm_font_size-1, opacity = frm_op)

    return Fig(frm_plot, Fig(frmLine1, frmLine2, frmLine3, frmLine4),
                sun_ball, meta_data)


def _planetdiag(name, rpos, rotang = 0.0, orb_scl = 1.0,
    frmSizecl = 10.0, diag_op = 1.0):

    # print("Building {} diagram...".format(name))

    colors = []

    if name == "MERCURY":
        colors = ["#C8C5E2", "#373163"]
    if name == "VENUS":
        diag_op = 0.2
        colors = ["#EDE051", "#393506"]
    if name == "EARTH":
        colors = ["#00AFEF", "#003C52"]

    colorurl="url(#{}Grad)".format(name[0:4].lower())

    # Scale the position vector ...
    # rpos = [x*frmSizecl*orb_scl for x in rpos]

    # Simplify ...
    r_x = rpos[0]
    r_y = rpos[1]

    gradrot = degrees(atan2(r_y, r_x))

    # Build a white ball for background ...
    ball_bg = _planetdot(name, rpos, r_dot_size = 2.0, dot_color = "white",
                            dot_str_op = diag_op)
    # ... and a color ball for foreground.
    ball_fg = _planetdot(name, rpos, r_dot_size = 2.0, dot_color = colors[0],
                            dot_op = diag_op, dot_str_op = diag_op)

    # Stack coloured ball on top of white background ball...
    ball = Fig(ball_bg, ball_fg)

    grad = _gradient(name[0:4].lower(), colors, gradrot, rotang, r_x, r_y)

    if name == "MERCURY" :

        # print("Buidling MPO orbit schematic...")

        # MPO line scaling factor
        mpo_line_sf = 2.0

        # MPO line start and end points
        mpo_line_st = r_x-orb_scl*mpo_line_sf
        mpo_line_en = r_x+orb_scl*mpo_line_sf*0.720811474

        node_size = 0.15

        x1 = mpo_line_st - node_size
        x2 = mpo_line_st + node_size
        y1 = r_y - node_size
        y2 = r_y + node_size
        dec_node = Fig(Rect(x1=x1, y1=y1, x2=x2, y2=y2, fill="black"),
                        trans=rotate(0,mpo_line_st,r_y))

        x1 = mpo_line_en - node_size
        x2 = mpo_line_en + node_size
        y1 = r_y - node_size
        y2 = r_y + node_size
        asc_node = Fig(Rect(x1=x1, y1=y1, x2=x2, y2=y2, fill="black"),
                        trans=rotate(45,mpo_line_en,r_y))

        mpo_line = Fig(Line(mpo_line_st, r_y,mpo_line_en, r_y,
                            stroke_width="0.15pt",),
                       asc_node,
                       dec_node,
                       trans = rotate(-rotang, r_x, r_y))


        # r_trans = rotate(theta, 0, 0)
        ball.d.append(Fig(mpo_line))

    return Fig(ball, trans=rotate(rotang, 0, 0)), grad


def _planetdot(name, rpos, dot_color = "#C8C5E2", r_dot_size = 0.6,
    dot_op=1.0, dot_str_op = 1.0):

    r_x = rpos[0]
    r_y = rpos[1]
    cname = dot_color.replace("#", "")

    ret_dot = Fig(Dots([(r_x, r_y)],
                    make_symbol("dot_{}_{}".format(name, cname),
                                fill=dot_color, fill_opacity=dot_op,
                                stroke="black", stroke_width="0.15pt",
                                stroke_opacity=dot_str_op),
                    r_dot_size, r_dot_size))

    return ret_dot


def _planetdotang(a, b, theta, r_dot_adj = 0.23, dot_color = "#C8C5E2",
    r_dot_size = 0.6, rot_x = 0.0, rot_y = 0.0, dot_op=1.0, dot_str_op = 1.0):
    if theta < 180:
        r_dot_adj = r_dot_adj*-1.0
    r_dot = _rellipse(a, b, theta)
    r_trans = rotate(theta, rot_x, rot_y)
    # print(r_dot)
    ret_dot = Fig(Dots([(r_dot, 0)],
                    make_symbol("dot_{}_{}".format(theta, dot_color),
                                fill=dot_color, fill_opacity=dot_op,
                                stroke="black", stroke_width="0.15pt",
                                stroke_opacity=dot_str_op),
                    r_dot_size, r_dot_size), trans=r_trans)
    # print(theta)
    # print(r_dot*cos(radians(theta)), r_dot*sin(radians(theta)))
    return ret_dot


def _rellipse(a, b, theta):
    rret = (b**2)/(a-sqrt(a**2-b**2)*cos(radians(180-theta)))
    return rret


def _sun(id = "Sun", posx = 0, posy = 0, size = 1.5, fill = "yellow",
    stroke = "orange", stroke_width = "0.1pt"):
    return Dots([(0, 0)], make_symbol(id, stroke=stroke,
                fill=fill,stroke_width=stroke_width), size, size)


def planetsplot(user_dates = None, delta = "1d", master_scale = 15):
    """
    ... explain what this does...
    """

    # Build basic orbits and calculate offset angles.
    orbits, offsets, dates =_buildorbits(delta, master_scale)

    if not user_dates:
        pass # TODO: user can specify specific dates or true anomalies.

    if len(orbits[0]) == len(dates):

        # print(len(orbits), len(orbits[0]), len(dates))

        # This angle will put the Hermean perihelion on the X-axis.
        rotang = -offsets[0]

        # Gather position data for each chart based on dates.
        # charts = _getpos("2024/01/01", end = "2024/01/03")

        # dates = ("2024/01/01", "2024/01/02")

        # A graphic will be created for each date in dates:

        for date in dates:

            dx = dates.index(date)

            # Verify that the epochs of each planet are the same.
            # if chart[0][1] == chart[1][1] == chart[2][1]:


            # -- Outer frame -----------------------------------------------------

            # Opacity of degree frame and Venus graphic
            frame_op = 0.5

            # Process JD time into calendar time strings
            calbase = 2400000.5
            caldat = jd2gcal(calbase, date-calbase)
            eyear = "{}".format(caldat[0])
            emonth = "{0:02d}".format(caldat[1])
            eday = "{0:02d}".format(caldat[2])
            epoch = "{}/{}/{}".format(eday, emonth, eyear)
            ep_name = "{}{}{}".format(eyear, emonth, eday)

            # print(dx, ep_name)

            frame = _outerframe(epoch, frmSize = master_scale, frm_op = frame_op)


            # -- First Point of Aires --------------------------------------------

            # merc_loan = 48.331
            # merc_argp = 29.124
            arend = make_marker("fopa_arrowend", "arrow_end",
                                fill_opacity=frame_op)

            x1, y1 = 0, 0
            x2, y2 = master_scale*1.4, 0

            fpoa = Line(x1, y1, x2, y2, stroke_width=".4pt",
                            stroke_opacity=frame_op, arrow_end=arend)

            xp = x2*cos(radians(rotang)) - y2*sin(radians(rotang))
            yp = x2*sin(radians(rotang)) + y2*cos(radians(rotang))

            fpoa_text = Text(xp+5, yp-0.5, "First Point of Aires",
                            font_size = 2, opacity = frame_op)
            fpoa = Fig(Fig(fpoa, trans=rotate(rotang,0,0)),fpoa_text)


            # -- Some containers -------------------------------------------------

            orbs = []
            circles = []
            defs = SVG("defs")


            # -- Orbit circles -----------------------------------------------

            # Build the SVG for each orbit.
            for orbit in orbits:

                if orbits.index(orbit) == 1:
                    orbit_op = frame_op
                else:
                    orbit_op = 1.0

                # Mercury's orbit will have perihelion on the X-axis
                circles.append(Fig(Poly(orbit, stroke_width=".25pt",
                                        stroke_opacity=orbit_op),
                                trans=rotate(rotang,0,0)))


            # -- Planet orbs -------------------------------------------------

            points = [orbits[0][dx],orbits[1][dx],orbits[2][dx]]

            # Build the planet orb and gradient
            # for each planet for this chart.
            for point in points:

                AU = 149597871. # km
                # Planetary inputs ...
                if points.index(point) == 0:
                    name = "MERCURY"
                    nu = degrees(atan2(point[1], point[0]))+rotang
                    if nu < 0:
                        nu = nu+360
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
            svg = Fig(fpoa, frame, circles[0], circles[1], circles[2],
                        orbs[0], orbs[1], orbs[2]).SVG(window(-wa, wa, -wa, wa))

            # print(defs)

            svg.prepend(defs)

            # print(svg)

            svg.save("merc_orbit_plot_{}_{}.svg".format(int(ep_name), nu))

        # You'll jump to hear if the epochs for all 3 planets are not equal.
    else:
        print("There is an epoch error between the planet time values...")


if __name__ == '__main__':
    planetsplot()
