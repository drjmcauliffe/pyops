#!/usr/bin/env python
# -*- coding: utf-8 -*-


from __future__ import print_function
from datetime import datetime, timedelta


# Classes
class line():
    """
        a class to hold information from a line from an
        EPS event file.
    """
    def __init__(self, string):
        self.vars = string.split('  ')
        self.time = extractTime(self.vars[0])
        self.tag = self.vars[1]
        self.count = tagnum(self.vars[2])

    def tagHas(self, *args):
        tagsplit = self.tag.split('_')
        for t in args:
            if t not in tagsplit:
                return False
        return True


class window():
    """
        a simple class that has a start time, stop time and duration
    """

    def __init__(self, start=0, stop=0):
        self.start = start
        self.stop = stop

    def duration(self):
        return self.stop - self.start


# class test_class():
#     """
#         a class to test functionality
#     """

#     def __init__(self,  **kwargs):
#         self.properties = kwargs

#     def set_kwp(self, k, v):
#         self.properties[k] = v

#     def get_kwv(self, key):
#         return self.properties.get(key, None)

#     def len(self):
#         return __len__(self)


class parameter():
    """
        an eps parameter class
    """

    def __init__(self, parameter, description, raw_type='', eng_type='',
                 default_value='', unit='', raw_limits=[], eng_limits=[],
                 parameter_values=[]):
        self.parameter = parameter
        self.description = description
        self.raw_type = raw_type
        self.eng_type = eng_type
        self.default_value = default_value
        self.unit = unit
        if len(raw_limits) in [0, 2]:
            self.raw_limits = raw_limits
        else:
            print("Limits can only have 2 values.")
        if len(eng_limits) in [0, 2]:
            self.eng_limits = eng_limits
        else:
            print("Limits can only have 2 values.")
        self.parameter_values = parameter_values

    # def len(self):
    #     return __len__(self)


# Time functions
def getMonth(month):
    """
        returns the number of the month if given a string
        and returns the name of the month if given and int
    """
    # months = ['January', 'February', 'March', 'April', 'May', 'June',
    #           'July', 'August', 'September', 'October' 'November',
    #           'December']
    mons = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug',
            'Sep', 'Oct', 'Nov', 'Dec']
    if type(month) == str:
        month = month[0:3]
        try:
            return mons.index(month) + 1
        except ValueError as err:
            print('Shall we list the months: {}'.format(err))
    if type(month) == int:
        try:
            return mons[month - 1]
        except IndexError as err:
            print('How many months are there in the year: {}'.format(err))


def extractTime(line):
    """
        extracts time from an event file input line
        and returns a datetime object.
    """
    dt = line.split(None, 1)[0]
    if len(dt) > 20:
        print(dt, 'Invalid dateTime string')
        return
    #print('extractTime : ', line )
    d, t = dt.split('_')
    day, month, year = d.split('-')
    month = getMonth(month)
    hour, minute, second = t.split(':')
    return datetime(int(year), int(month), int(day),
                    int(hour), int(minute), int(second))


def insertTime(line, time):
    """
        inserts a new time into an event file line.
    """
    dt = line[0:line.find(' ')]
    return line.replace(dt, time)


def constructTime(dt):
    """
        reconstructs an event file line time element
        from a datetime object.
    """
    if type(dt) != datetime:
        print('Invalid datetime object')
        return
    return (str(dt.day).zfill(2) + '-' + getMonth(dt.month) + '-'
            + str(dt.year) + '_' + str(dt.hour).zfill(2) + ':'
            + str(dt.minute).zfill(2) + ':' + str(dt.second).zfill(2))


def adjustTime(line, toChange, by):
    """
        adjusts the datetime element 'toChange' of an
        event line by 'by'.
    """
    adj = timedelta(**{toChange: by})
    dt = extractTime(line)
    new_dt = dt + adj
    return constructTime(new_dt)


# Line editor functions
def adjustLine(line, timeChange, timeBy, tagChange=None):
    """
        adjusts the datetime element of an event line and,
        if given, change the event tag element to 'tagChange'.
    """
    dt, tag, cntstr = line.split(None, 2)
    if tagChange is not None:
        tag = tagChange
    dt = adjustTime(dt, timeChange, timeBy)
    return '{}  {}  {}'.format(dt, tag, cntstr)


# Content test functions
def containsAll(line, *args):
    """
        tests to see if 'line' contains ALL of the
        tags in 'args'
    """
    #print('Line : {}Tags : {}'.format(line, args))
    for tag in args:
        #print('Search Tag : {}'.format(tag))
        # If any of the tags are not found 'line.find(tag)' will be -1.
        if (line.find(tag) < 0):
            #print('{} does not contain {}'.format(line.strip('\n'), tag))
            return (line.find(tag) > 0)
        #else:
            #print('{} contains {}'.format(line.strip('\n'), tag))
    return (line.find(tag) > -1)


def containsAny(line, *args):
    """
        tests to see if 'line' contains ANY of the
        tags in 'args'
    """
    for tag in args:
        if line.find(tag) > -1:
            return line.find(tag) > -1
    return line.find(tag) > -1


def containsNone(line, *args):
    """
        tests to see if 'line' contains 'NONE' of the
        tags in 'args'
    """
    return (not containsAny(line, *args))


# Event count function
def tagnum(line):
    """
        returns the current event count
    """
    return int(line[line.find('=') + 1:line.find(')')])


# Is line in the header?
def isHeader(line):
    """
        tests to see if 'line' is in the event file
        header
    """
    if containsAny(line, 'EVF Filename:', 'Generation Time:', 'Start_time:',
                   'End_time:', 'events in list)', '#', 'Include:',
                   'Init_value:'):
        return True
    elif len(line) < 3:
        return True
    else:
        return False


# Text wrapped output
def wrap(text, width):
    """
    A word-wrap function that preserves existing line breaks
    and most spaces in the text. Expects that existing line
    breaks are posix newlines (\n).
    """
    return reduce(lambda line, word, width=width: '%s%s%s' %
                  (line,
                   ' \n'[(len(line) - line.rfind('\n') - 1
                         + len(word.split('\n', 1)[0]
                               ) >= width)],
                   word
                   ),
                  text.split(' ')
                  )


# Main function
def main():
    """
        does nothing for now...
    """
    print('This is a random collection of functions... TBS - to be sorted.')


if __name__ == "__main__":
    main()
