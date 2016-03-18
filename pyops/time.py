"""
This module provides a series of time/date utilities.
"""
from __future__ import print_function
import spiceypy as spice
from datetime import datetime, timedelta


def oem_to_datetime(oem_time_string):
    """
    converts oem datetime record to python datetime object

    Args:
        oem_time (string): datetime string
    """
    date, time = oem_time_string.split('T')

    year, month, day = date.split('-')

    hour, minute, second_fraction = time.split(':')
    second, fraction = second_fraction.split('.')

    return datetime(int(year), int(month), int(day),
                    int(hour), int(minute), int(second),
                    int(fraction[0:3]))


def datetime_to_et(dtime, scale='UTC'):
    """
    convert a python datetime to SPICE ephemerides seconds (TBD)

    Args:
        dtime (datetime): python datetime
        scale (str, optional): time scale of input time (default: UTC)

    Returns:
        float: SPICE ephemerides sceonds (TBD)
    """
    return spice.str2et(dtime.strftime(
        '%m/%d/%y %H:%M:%S.%f ({})'.format(scale)))


def et_to_datetime(et, scale='TDB'):
    """
    convert a SPICE ephemerides epoch (TBD seconds) to a python datetime
    object. The default time scale returned will be TDB but can be set
    to any of the accepted SPICE time scales.

    Args:
        et (float): SPICE ephemerides sceonds (TBD)
        scale (str, optional): time scale of output time (default: TDB)

    Returns:
        datetime: python datetime
    """
    t = spice.timout(et, 'YYYY-MON-DD HR:MN:SC.### ::{}'.format(scale), 41)
    return datetime.strptime(t, '%Y-%b-%d %H:%M:%S.%f')


def et_to_utc(et):
    """Summary
    convert SPICE epoch in Ephemerides seconds (TDB) to a
    UTC time string.

    Args:
        et (float): SPICE epoch in Ephemerides seconds (TDB)

    Returns:
        string: UTC time
    """
    return spice.et2utc(et, 'ISOC', 3, 30)


def itl_to_datetime(itltime):
    """
    convert EPS ITL time format to python datetime object

    Args:
        itltime (string): EPS ITL time string formt

    Returns:
        datetime: python datetime
    """
    return datetime.strptime(itltime, '%d-%b-%Y_%H:%M:%S')


def xldate_to_datetime(xldate):
    """
    convert an Excel format time to python datetime object

    Args:
        xldate (float): days in Excel format

    Returns:
        datetime: python datetime
    """
    temp = datetime(1900, 1, 1)
    delta = timedelta(days=xldate)
    return temp+delta


# def mjd20002datetime(mjd2000):
#     y, m, d, fd = jdcal.jd2gcal(
#         jdcal.MJD_0,jdcal.MJD_JD2000+float(mjd2000)-0.5)
#     hour = 24* fd
#     mins = 60*(hour - int(hour))
#     sec = 60*(mins - int(mins))
#     usec = 1000000*(sec-int(sec))
#     return dt(y, m, d, int(hour), int(mins), int(sec), int(usec))

# def datetime2et(dtime):
#     return spice.str2et(dtime.strftime("%m/%d/%y %H:%M:%S.%f"))

# def mjd20002et(mjd2000):
#     return datetime2et(mjd20002datetime(mjd2000))



# def et2mjd2000(et):
#     return float(spice.et2utc(et, 'J', 7, 30).split(' ')[1]) - \
#                                     jdcal.MJD_0 - jdcal.MJD_JD2000 + 0.5


# def mjd20002datetime(mjd2000):
#     y, m, d, fd = jdcal.jd2gcal(jdcal.MJD_0,jdcal.MJD_JD2000+float(mjd2000)-0.5)
#     hour = 24* fd
#     mins = 60*(hour - int(hour))
#     sec = 60*(mins - int(mins))
#     usec = 1000000*(sec-int(sec))
#     return dt(y, m, d, int(hour), int(mins), int(sec), int(usec))

# def datetime2et(dtime):
#     return spice.str2et(dtime.strftime("%m/%d/%y %H:%M:%S.%f"))

# def mjd20002et(mjd2000):
#     return datetime2et(mjd20002datetime(mjd2000))

# def et2utc(et):
#     return spice.et2utc(et, 'ISOC', 3, 30)

# def et2datetime(et):
#     utc = et2utc(et)
#     utc_date, utc_time = utc.split('T')
#     y, m, d = utc_date.split('-')
#     hour, mins, sec = utc_time.split(':')
#     sec, usec = sec.split('.')
#     return dt(int(y), int(m), int(d), int(hour), int(mins), int(sec), int(usec))

# def et2mjd2000(et):
#     return float(spice.et2utc(et, 'J', 7, 30).split(' ')[1]) - jdcal.MJD_0 - jdcal.MJD_JD2000 + 0.5


# Main function
def main():
    """
        does nothing for now...
    """
    print('This is a random collection of functions... TBS - to be sorted.')


if __name__ == "__main__":
    main()
