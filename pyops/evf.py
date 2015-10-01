from pyops.utils import is_elapsed_time, parse_time, getMonth
import pandas as pd
from datetime import datetime
import os


class EVF:

    def __init__(self, fname):
        # Variable initialization
        self.WTF = list()
        self.meta = dict()
        self.header = list()
        self.ref_date = None
        self.init_values = list()
        self.include_files = list()
        self.propagation_delay = None

        # Loading the given file
        self.load(fname)

    def load(self, fname):
        # Storing the name of the file for editting purposes
        self.fname = fname
        # Auxiliary dictionary to speed up the data convertion into pandas
        aux_dict = dict(raw_time=[], time=[], event=[], experiment=[], item=[],
                        count=[], comment=[])

        # Importing the file
        out_ouf_metadata = False
        with open(fname) as f:
            for line in f:

                if '\n' in line[0]:
                    pass
                # Filtering lines with comments
                elif '#' in line[0]:
                    if not out_ouf_metadata:
                        self.header.append(line)
                        self._read_metada(line)
                    else:
                        self.WTF.append(line)
                # Storing events
                elif is_elapsed_time(line.split()[0]):
                    aux_dict = self._read_events(line, aux_dict)
                # Useful data from the header
                else:
                    # We can say we are out of the metadate here because
                    # start_time and end_time are mandatory in the files
                    out_ouf_metadata = True
                    self._read_header_line(line.split())
        # Closing the file
        f.close()
        # Creating the pandas dataframe
        self.events = pd.DataFrame(aux_dict)
        # Sorting by the time
        self.events = self.events.sort(['time'])
        # Sorting the columns in the dataframe
        cols = ['raw_time', 'time', 'event', 'experiment', 'item', 'count',
                'comment']
        self.events = self.events[cols]

    def _read_metada(self, line):
        if ': ' in line:
            self.meta[line[1:line.index(': ')].strip()] = \
                line[line.index(': ') + 1:-1].strip()

    def _read_events(self, line, aux_dict):
        # Storing comments
        if '#' in line:
            index = line.index('#')
            aux_dict['comment'].append(line[index:-1])
        else:
            aux_dict['comment'].append(None)
        # Consecutive whitespace are regarded as a single separator
        l = line.split()
        aux_dict['raw_time'].append(l[0])
        aux_dict['time'].append(self._to_datetime(l[0]))
        aux_dict['event'].append(l[1])

        l = [e.upper() for e in line.split()]

        if 'ITEM' in l:
            # In the file it should be: EXP = <experiment> ITEM = <item>
            aux_dict['experiment'].append(l[l.index('ITEM') - 1])

            # In the file it should be: ITEM = <item>
            aux_dict['item'].append(l[l.index('ITEM') + 2])
            # Removing last parenthesis if exist
            if aux_dict['item'][-1][-1] == ')':
                aux_dict['item'][-1] = aux_dict['item'][-1][:-1]
            if '#' in aux_dict['item'][-1]:
                aux_dict['item'][-1] = \
                    aux_dict['item'][-1][:aux_dict['item'][-1].index('#') - 1]
        else:
            # Storing empty values
            aux_dict['experiment'].append(None)
            aux_dict['item'].append(None)

        if 'COUNT' in l or '(COUNT' in l:
            if 'COUNT' in l:
                # In the file it should be: COUNT = <count>
                aux_dict['count'].append(l[l.index('COUNT') + 2])
            else:
                # In the file it should be: (COUNT = <count>)
                aux_dict['count'].append(l[l.index('(COUNT') + 2])
            # Removing useless characters at the end
            if aux_dict['count'][-1][-1] == ')':
                aux_dict['count'][-1] = aux_dict['count'][-1][:-1]
            if '#' in aux_dict['count'][-1]:
                aux_dict['count'][-1] = \
                    aux_dict[
                        'count'][-1][:aux_dict['count'][-1].index('#') - 1]
        else:
            aux_dict['count'].append(None)

        return aux_dict

    def _read_header_line(self, line):
        if 'Ref_date:' in line:
            # Storing them in "raw" format
            self.raw_ref_time = line[1]
            # Getting the reference date from the header and transforming it
            # into datetime format
            self.ref_date = self._ref_date_to_datetime(line[1])
        elif 'Start_time:' in line:
            # Storing them in "raw" format
            self.raw_start_time = line[1]
            # Storing them in datetime format
            self.start_time = self._to_datetime(line[1])
        elif 'End_time:' in line:
            # Storing them in "raw" format
            self.raw_end_time = line[1]
            # Storing them in datetime format
            self.end_time = self._to_datetime(line[1])
        elif 'Propagation_delay:' in line:
            self.propagation_delay = line[1:]
        elif 'Init_value:' in line:
            # Storing them in "raw" format
            self.init_values.append(line[1:])
        # Sometimes it appears as Include instead of Include_file
        elif 'Include_file:' in line or 'Include:' in line:
            self.include_files.append(line[1:])

    def _ref_date_to_datetime(self, ref_date):
        ref_date = ref_date.split('-')[0] + "-" +\
            str(getMonth(ref_date.split('-')[1])) + "-" + \
            ref_date.split('-')[2]
        return datetime.strptime(ref_date, "%d-%m-%Y")

    def _to_datetime(self, element):
        if self.ref_date is None and '-' not in element:
            return parse_time(element)
        else:
            if '-' in element:
                date = self._ref_date_to_datetime(element.split('_')[0])
                return parse_time("000_" + element.split('_')[1], date)
            return parse_time(element, self.ref_date)

    def to_file(self, fname):
        # Creating file if the file doesn't exist and truncating it if exists
        with open(fname, 'w') as f:
            # Copying the header
            [f.write(line) for line in self.header]

            # Copying the useful data in the header
            # Reg_date
            if self.ref_date is not None:
                f.write("Ref_date: " + self.raw_ref_time + "\n#\n")

            # Start and End time
            f.write("Start_time: " + self.raw_start_time + "\n")
            f.write("End_time: " + self.raw_end_time + "\n#\n")

            # Propagation delay
            if self.propagation_delay is not None:
                output = ""
                for element in self.propagation_delay:
                    output += " " + element
                f.write("Propagation_delay: " + output + "\n#\n")

            # Init values
            if len(self.init_values) > 0:
                for value in self.init_values:
                    output = ""
                    for element in value:
                        output += " " + element
                    f.write("Init_value: " + output + "\n")
                f.write("#\n")

            # Include files
            if len(self.include_files) > 0:
                for include in self.include_files:
                    output = ""
                    for element in include:
                        output += " " + element
                    f.write("Include_file: " + output + "\n")
                f.write("#\n")

            # Copying events
            f.write("# Events_in_list: " + str(len(self.events.index))
                    + "\n#\n")
            f.write("# Time                 Event\n#\n")
            for index, row in self.events.iterrows():
                output = row['raw_time'] + "   " + row['event']
                if row['experiment'] is not None:
                    output += "  (EXP = " + row['experiment'] + " "
                    output += "ITEM = " + row['item'] + ")"
                if row['count'] is not None:
                    output += " (COUNT = " + row['count'] + ")"
                if row['comment'] is not None:
                    output += " # " + row['comment']
                output += "\n"
                f.write(output)

            f.write("#\n")

        f.close()

    def check_consistency(self):
        if self.events['time'].min() < self.start_time:
            print ("There is an time event before the official start_time")
            print (self.events['time'].min() + " is before than "
                   + self.start_time)
            raise NameError('Events before start_time')
        elif self.events['time'].max() > self.end_time:
            print ("There is an time event after the official end_time")
            print (self.events['time'].max() + " is after than "
                   + self.end_time)
            raise NameError('Events after end_time')
        elif self.check_if_included_files_exist_in_directory():
            print ("Everything seems to be ok, congratulations! :)")

    def check_if_included_files_exist_in_directory(self):
        files_exist = True
        # Getting the path of the directory where we are working
        path = os.path.dirname(os.path.abspath(self.fname))

        for fname in self.include_files:
            # Removing possible problematic characters
            fname = fname[0].strip('"')

            if not os.path.isfile(os.path.join(path, fname)):
                files_exist = False
                output = "It seems as if " + fname + "is not in the same "
                output += "directory as " + os.path.basename(self.fname)
                print (output)
                # Perhaps raising an exception here in the future...

        return files_exist
