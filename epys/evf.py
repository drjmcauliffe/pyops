from epys.utils import is_elapsed_time, parse_time, getMonth
import pandas as pd
from datetime import datetime


class Evf:

    def __init__(self, fname):
        # Variable initialization
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
        aux_dict = dict(raw_time=[], time=[], event=[], experiment=[], item=[])

        # Importing the file
        with open(fname) as f:
            for line in f:
                # Filtering lines with comments
                if '#' in line[0]:
                    self.header.append(line)
                # Storing events
                elif is_elapsed_time(line.split()[0]):
                    aux_dict = self._read_events(line, aux_dict)
                # Useful data from the header
                else:
                    self._read_header_line(line.split())

        self.events = pd.DataFrame(aux_dict)

    def _read_events(self, line, aux_dict):
        # Consecutive whitespace are regarded as a single separator
        l = line.split()
        aux_dict['raw_time'].append(l[0])
        aux_dict['time'].append(self._to_datetime(l[0]))
        aux_dict['event'].append(l[1])

        if 'ITEM' in l:
            # In the file it should be: EXP = <experiment> ITEM = <item>
            aux_dict['experiment'].append(l[l.index('ITEM') - 1])

            # In the file it should be: ITEM = <item>
            aux_dict['item'].append(l[l.index('ITEM') + 2])
            # Removing last parenthesis if exist
            if aux_dict['item'][-1][-1] == ')':
                aux_dict['item'][-1] = aux_dict['item'][-1][:-1]
        else:
            # Storing empty values
            aux_dict['experiment'].append(None)
            aux_dict['item'].append(None)

        return aux_dict

    def _read_header_line(self, line):
        if 'Ref_date:' in line:
            # Storing them in "raw" format
            self.raw_ref_time = line[1]
            # Getting the reference date from the header and transforming it
            # into datetime format
            ref_date = line[1].split('-')[0] + "-" +\
                str(getMonth(line[1].split('-')[1])) + "-" + \
                line[1].split('-')[2]
            self.ref_date = datetime.strptime(ref_date, "%d-%m-%Y")
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
        elif 'Include_file:' in line:
            self.include_files.append(line[1:])

    def _to_datetime(self, element):
        if self.ref_date is None:
            return parse_time(element)
        else:
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
            f.write("#\n# Time         Event\n#\n")
            for index, row in self.events.iterrows():
                output = row['raw_time'] + "   " + row['event']
                if row['experiment'] is not None:
                    output += "  (EXP = " + row['experiment'] + " "
                    output += "ITEM = " + row['item'] + ")"
                output += "\n"
                f.write(output)

            f.write("#\n")

        f.close()
