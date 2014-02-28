from datetime import datetime

from io import StringIO
import telnetlib
import socket

import numpy as np
from numpy import radians

import matplotlib as mpl
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt


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
        n_lines = len(ephem_str.splitlines())
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
        self.sendline()
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
        n_lines = len(ephem_str.splitlines())
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


if __name__ == '__main__':
    start_date = datetime(2024, 5, 7)
    end_date = datetime(2024, 5, 6)
    delta = "1d" # TODO: Better specify time delta

    jpl = Horizons()

    # Earth osculating elements
    jd, a, ecc, inc, omega, argp, nu = jpl.elements(jpl.MERCURY, start_date, end_date,
                                                    delta)
    print(jd, a, ecc, inc, omega, argp, nu )
    #print(omega)
    #print(nu)

    #Position and velocity vectors
    jd_e, r_e, v_e = jpl.vectors(jpl.EARTH, start_date, end_date, delta)

    jd_v, r_v, v_v = jpl.vectors(jpl.VENUS, start_date, end_date, delta)

    jd_m, r_m, v_m = jpl.vectors(jpl.MERCURY, start_date, end_date, delta)


    print(r_m[:,0])

    # fig = plt.figure()
    # ax = fig.gca(projection='3d')

    plt.axis([-1.5e8, 1.5e8, -1.5e8, 1.5e8])

    plt.plot(r_e[:,0], r_e[:,1] )

    plt.plot(r_v[:,0], r_v[:,1])

    plt.plot(r_m[:,0], r_m[:,1])

    plt.plot(0,0, 'yo')

    plt.show()

    # Happy astronomying!
