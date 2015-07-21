from epys import events


# Time functions
# =================================

# 1. getMonth(month) tests
def test_getMonthFromStringToInt():
    """
        It should return the number of the month if given a string
        and returns the name of the month if given and int
    """
    # months = ['January', 'February', 'March', 'April', 'May', 'June',
    #           'July', 'August', 'September', 'October' 'November',
    #           'December']
    mons = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug',
            'Sep', 'Oct', 'Nov', 'Dec']
    number = 1
    for month in mons:
        assert events.getMonth(month) == number
        number += 1


def test_getMonthFromIntToString():
    """
        It should return the number of the month if given a string
        and returns the name of the month if given and int
    """
    # months = ['January', 'February', 'March', 'April', 'May', 'June',
    #           'July', 'August', 'September', 'October' 'November',
    #           'December']
    mons = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug',
            'Sep', 'Oct', 'Nov', 'Dec']
    number = 1
    for month in mons:
        assert events.getMonth(number) == month
        number += 1


def test_getMonthUnexpectedInputs():
    # TODO
    assert 1 == 1


# 1. extractTime(line) tests
"""
From data.events.notes.evf
Time values
===========
- a time value may be given in the POR or EPS relative time format
- an EPS <time> field is in the format [[sign][ddd_]hh:mm:ss]
- [sign] is an optional sign ('-' or '+')
- [ddd] is an optional day number
- [ddd] may consist of one, two or three digits, and may be zero
- [hh] is the number of hours (00..23)
- [mm] is the number of minutes (00..59)
- [ss] is the number of seconds (00..59)
- [hh], [mm], [ss] must be specified and must have two characters each
- a POR relative time value is in the format [[-][ddd.]hh:mm:ss[.mmm]]
- [ddd] is the optional number of days
- [hh], [mm], [ss] is defined similarly as above
- [.mmm] is optional and specifies the number of milliseconds
- the EPS software will always ignore the [.mmm] value
"""


# def test_extract_time_eps_format():
"""
        extracts time from an event file input line
        and returns a datetime object.
    """
"""
    eps_line = '01:02:03   SUN_IN_FOV (EXP = OSIRIS ITEM = NAC)'
    time = events.extractTime(eps_line)
    assert time.day == 0
    assert time.hour == 1
    assert time.minute == 2
    assert time.second == 3

    eps_line = '0_01:02:03   SUN_IN_FOV (EXP = OSIRIS ITEM = NAC)'
    time = events.extractTime(eps_line)
    assert time.day == 0
    assert time.hou == 1
    assert time.minut == 2
    assert time.second == 3

    eps_line = '23_01:02:03   SUN_IN_FOV (EXP = OSIRIS ITEM = NAC)'
    time = events.extractTime(eps_line)
    assert time.day == 23
    assert time.hour == 1
    assert time.minute == 2
    assert time.second == 3

    eps_line = '223_01:02:03   SUN_IN_FOV (EXP = OSIRIS ITEM = NAC)'
    time = events.extractTime(eps_line)
    assert time.day == 223
    assert time.hour == 1
    assert time.minute == 2
    assert time.second == 3

    eps_line = '+23_01:02:03   SUN_IN_FOV (EXP = OSIRIS ITEM = NAC)'
    time = events.extractTime(eps_line)
    assert time.day == 23
    assert time.hour == 1
    assert time.minute == 2
    assert time.second == 3

    eps_line = '-23_01:02:03   SUN_IN_FOV (EXP = OSIRIS ITEM = NAC)'
    time = events.extractTime(eps_line)
    assert time.day == -23
    assert time.hour == 1
    assert time.minute == 2
    assert time.second == 3


def test_extract_time_por_format():
    """
"""
        extracts time from an event file input line
        and returns a datetime object.
    """
"""
    por_line = '01:02:03   SUN_IN_FOV (EXP = OSIRIS ITEM = NAC)'
    time = events.extractTime(por_line)
    assert time.day == 0
    assert time.hour == 1
    assert time.minute == 2
    assert time.second == 3

    por_line = '0.01:02:03   SUN_IN_FOV (EXP = OSIRIS ITEM = NAC)'
    time = events.extractTime(por_line)
    assert time.day == 0
    assert time.hour == 1
    assert time.minute == 2
    assert time.second == 3

    por_line = '23.01:02:03   SUN_IN_FOV (EXP = OSIRIS ITEM = NAC)'
    time = events.extractTime(por_line)
    assert time.day == 23
    assert time.hour == 1
    assert time.minute == 2
    assert time.second == 3

    por_line = '223.01:02:03   SUN_IN_FOV (EXP = OSIRIS ITEM = NAC)'
    time = events.extractTime(por_line)
    assert time.day == 223
    assert time.hour == 1
    assert time.minute == 2
    assert time.second == 3

    por_line = '-23.01:02:03   SUN_IN_FOV (EXP = OSIRIS ITEM = NAC)'
    time = events.extractTime(por_line)
    assert time.day == -23
    assert time.hour == 1
    assert time.minute == 2
    assert time.second == 3

    por_line = '-23.01:02:03.385   SUN_IN_FOV (EXP = OSIRIS ITEM = NAC)'
    time = events.extractTime(por_line)
    assert time.day == -23
    assert time.hour == 1
    assert time.minute == 2
    assert time.second == 3
    assert time.millisecond == 385
    """


# 1. extractDate(line) tests
"""
From data.events.notes.evf
Date values
===========
- a date value may be given in the POR or EPS absolute time format
- an EPS <date> value is in the format [dd-month-yyyy[_hh:mm:ss]]
- [dd] is the day number
- [dd] may consist of one or two digits, and may start with zero
- [month] is the full (spelled out) month or any abbreviation
  with a minimum of 3 characters
- [yyyy] is the full year number
- [_hh:mm:ss] is optional and is defined similarly as in the time format
- the '_' character is mandatory here if the time of the day is given
- the time of the day defaults to _00:00:00
- a POR absolute time value is in the format [yy-dddThh:mm:ss[.mmm]Z]
- [yy] is the year in the 21st century and must have two characters
- [ddd] is the day number within the year, counting from 1
- [hh:mm:ss] is defined similarly as in the time format
- [.mmm] is optional and specifies the number of milliseconds
- the EPS software will always ignore the [.mmm] value
"""


# def test_extract_date_eps_format():
"""
        extracts date from an event file input line
        and returns a datetime object.
    """
"""
    eps_line = '1-Feb-1995   SUN_IN_FOV (EXP = OSIRIS ITEM = NAC)'
    time = events.extractTime(eps_line)
    assert time.day == 1
    assert time.month == 2
    assert time.year == 1995

    eps_line = '01-Feb-1995_1:02:03   SUN_IN_FOV (EXP = OSIRIS ITEM = NAC)'
    time = events.extractTime(eps_line)
    assert time.day == 1
    assert time.month == 2
    assert time.year == 1995
    assert time.hour == 1
    assert time.minute == 2
    assert time.second == 3

    eps_line = '1-February-1995_01:02:3   SUN_IN_FOV (EXP = OSIRIS ITEM = NAC)'
    time = events.extractTime(eps_line)
    assert time.day == 1
    assert time.month == 3
    assert time.year == 1995
    assert time.hour == 1
    assert time.minute == 2
    assert time.second == 3
    """

# def test_extract_date_por_format():
"""
        extracts date from an event file input line
        and returns a datetime object.
    """
"""
    por_line = '02-23T01:02:03Z   SUN_IN_FOV (EXP = OSIRIS ITEM = NAC)'
    time = events.extractTime(por_line)
    assert time.year == 2002
    assert time.day == 23
    assert time.month == 1
    assert time.hours == 1
    assert time.minutes == 2
    assert time.seconds == 3
    assert time.microsecond == 0

    por_line = '02-223T01:02:03Z   SUN_IN_FOV (EXP = OSIRIS ITEM = NAC)'
    time = events.extractTime(por_line)
    assert time.year == 2002
    assert time.day == 11
    assert time.month == 8
    assert time.hours == 1
    assert time.minutes == 2
    assert time.seconds == 3
    assert time.microsecond == 0

    por_line = '02-223T01:02:03.125Z   SUN_IN_FOV (EXP = OSIRIS ITEM = NAC)'
    time = events.extractTime(por_line)
    assert time.year == 2002
    assert time.day == 11
    assert time.month == 8
    assert time.hours == 1
    assert time.minutes == 2
    assert time.seconds == 3
    assert time.microsecond == 125000
    """
