from epys.utils import is_elapsed_time, parse_time, getMonth
import pandas as pd
from datetime import datetime, time
import os
from epys.plots import modes_schedule


class ITL:

    def __init__(self, fname, ref_date=None):
        # Variable initialization
        self.WTF = list()
        self.meta = dict()
        self.header = list()
        self.end_time = None
        self.ref_date = ref_date
        self.start_time = None
        self.init_values = list()
        self.merged_events = None
        self.include_files = list()
        self.propagation_delay = None

        # Loading the given file
        self.load(fname)

    def load(self, fname):
        # Storing the name of the file for editting purposes
        self.fname = fname

        # Auxiliary dictionary to speed up the data convertion into pandas
        aux_dict = dict(raw_time=[], time=[], experiment=[], mode=[],
                        action=[], parameters=[], comment=[])

        # Importing the file
        out_ouf_metadata = False
        with open(fname) as f:
            line = ""
            line_comments = list()
            for l in f:
                # Formatting just in case there is no space between parenthesis
                l = l.replace('(', ' ( ').replace(')', ' ) ')
                # Concatening lines if '\' found
                if '\\' in l and '#' not in l[0] and \
                   '\\' not in l[l.index('\\') + 1]:
                    line += l[:l.index('\\')]
                    line_comments.append(l[l.index('\\') + 1: - 1])
                    # Continues with the next iteration of the loop
                    continue
                # If there was no concatenation of lines
                if len(line) == 0:
                    line = l
                # If we were concatenating, we concatenate the last one
                else:
                    line += l[:l.index(')') + 1]
                    line_comments.append(l[l.index(')'):])

                if '\n' in line[0]:
                    pass
                elif 'Comment:' in line:
                    pass
                # Filtering lines with comments
                elif '#' in line[0]:
                    if not out_ouf_metadata:
                        self.header.append(line)
                        self._read_metada(line)
                    else:
                        self.WTF.append(line)
                # Storing events
                elif len(line.split()) > 0 and \
                        is_elapsed_time(line.split()[0]):
                    aux_dict = \
                        self._read_events(line, aux_dict, line_comments)
                # Useful data from the header
                else:
                    # We can say we are out of the metadate here because
                    # start_time and end_time are mandatory in the files
                    out_ouf_metadata = True
                    self._read_header_line(line.split())
                # Preparing values for next iteration
                line = ""
                line_comments = list()
        # Closing the file
        f.close()
        # Creating the pandas dataframe
        self.events = pd.DataFrame(aux_dict)
        self.events = self.order_colums_in_dataframe(self.events)

    def _read_metada(self, line):
        if ': ' in line:
            self.meta[line[1:line.index(': ')].strip()] = \
                line[line.index(': ') + 1:-1].strip()

    def _read_events(self, line, aux_dict, line_comments):
        # Consecutive whitespace are regarded as a single separator
        l = line.split()

        # Special case of include:
        # 000_22:30:00 INCLUDE "SA-SFT_FM__-ORB_LOAD-TC_-GEN01A.itl"
        if 'INCLUDE' in l[1].upper():
            if '#' in l:
                index = l.index('#')
                comment = ' '.join(l[index:])
                self.include_files.append(
                    [l[2], l[0]] + l[3:index] + [comment])
            else:
                self.include_files.append([l[2], l[0]] + l[3:])
        else:
            # Storing comments
            if '#' in line:
                index = line.index('#')
                aux_dict['comment'].append(line[index + 1:-1])
            elif len(line_comments) > 0 and len(line_comments[0]) > 0:
                index = line_comments[0].index('#')
                aux_dict['comment'].append(line_comments[0][index + 1:])
            else:
                aux_dict['comment'].append(None)

            aux_dict['raw_time'].append(l[0])
            aux_dict['time'].append(self._to_datetime(l[0]))
            aux_dict['experiment'].append(l[1])
            # If SOC as experiment and PTR isn't the mode then there is no mode
            if 'SOC' in l[1].upper() and 'PTR' not in l[2]:
                aux_dict['mode'].append(None)
            else:
                aux_dict['mode'].append(l[2])

            # If the next element in the line doesn't contain a hash, then
            # there is an action
            if '#' not in l[3]:
                aux_dict['action'].append(l[3])
                # If there are parameters we store them
                if len(l) > 4:
                    if '(' in l[4]:
                        aux_dict['parameters'].append(
                            self._read_parameters(l[5:], line_comments[1:]))
                    else:
                        aux_dict['parameters'].append(None)
                else:
                    aux_dict['parameters'].append(None)
            else:
                aux_dict['action'].append(None)
                aux_dict['parameters'].append(None)

        return aux_dict

    def _read_parameters(self, parameters, line_comments):
        output = list()
        # Selecting the indexes of every '=' in the line which implies a new
        # parameter exist
        indexes = [i for i, val in enumerate(parameters) if val == '=']
        for index in indexes:
            param = list()
            param.append(parameters[index - 1])
            # If it is the last element we take all but the last expected ')'
            if indexes[-1] == index:
                last_index = -1
            else:
                last_index = indexes[indexes.index(index) + 1] - 1

            # We avoid '=', that's why index + 1
            for element in parameters[index + 1:last_index]:
                param.append(element)

            # Adding comments. line_comments & indexes should have same length
            if indexes.index(index) + 1 <= len(line_comments):
                comment = line_comments[indexes.index(index)]
                if '#' in comment:
                    param.append((comment[comment.index('#') + 1:]))
                else:
                    param.append(comment)
            else:
                param.append(None)
            # Adding new parameter tuple
            output.append(param)

        return output

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
            # Only hh:mm:ss case
            if len(element) == 8:
                elements = [int(e) for e in element.split(':')]
                return time(elements[0], elements[1], elements[2])
            return parse_time(element)
        else:
            # Only hh:mm:ss case
            if len(element) == 8:
                return parse_time("000_" + element, self.ref_date)
            elif '-' in element:
                date = self._ref_date_to_datetime(element.split('_')[0])
                return parse_time("000_" + element.split('_')[1], date)
            return parse_time(element, self.ref_date)

    # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # This method has to be adapted!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
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

    def order_colums_in_dataframe(self, df):
        # Sorting by the time
        df = df.sort(['time'])
        # Sorting the columns in the dataframe
        cols = ['raw_time', 'time', 'experiment', 'mode', 'action',
                'parameters', 'comment']
        return df[cols]

    def check_consistency(self):
        if self.start_time is not None and \
           self.events['time'].min() < self.start_time:
            print ("There is an time event before the official start_time")
            print (self.events['time'].min() + " is before than "
                   + self.start_time)
            raise NameError('Events before start_time')
        elif self.end_time is not None and \
                self.events['time'].max() > self.end_time:
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

    def merge_includes(self):
        self.merged_events = self.events
        # Getting the path to load correctly the files
        path = os.path.dirname(os.path.abspath(self.fname))
        for f in self.include_files:
            print ("Reading " + f[0] + "...")
            fname = os.path.join(path, f[0].strip('"'))
            # There is an existing time
            if len(f) > 1 and is_elapsed_time(f[1]):
                ref_date = self._to_datetime(f[1])
                itl = ITL(fname, ref_date=ref_date)
            else:
                itl = ITL(fname)

            itl.check_consistency()
            # Recursing over the itl files
            itl.merge_includes()
            # Merging the dataframes
            self.merged_events = \
                pd.concat([self.merged_events, itl.merged_events],
                          ignore_index=True)
        self.merged_events = self.order_colums_in_dataframe(self.merged_events)

    def plot(self):
        # If the includes are still not merged, we merge them
        if self.merged_events is None:
            self.merge_includes()

        df = self._convert_df_to_mode_plot_table_format(
            self.merged_events, 'mode')
        df = df.set_index(['time'])
        df.index.names = ['Time']

        modes_schedule(df)

    def _convert_df_to_mode_plot_table_format(self, df, attribute):
        df = df[['time', 'experiment', attribute]]
        experiments_unique = df['experiment'].unique()

        # Initializating the output table
        # We create a new dictionary and convert it to a df because working
        # with the dataframe has a high computational cost
        output = dict()
        for exp in experiments_unique:
            output[exp] = list()

        # Adding the times
        output['time'] = pd.to_datetime(df['time'].values).tolist()
        experiments = df['experiment'].values.tolist()
        modes = df[attribute].values.tolist()
        # Creating the new table
        for experiment, mode in zip(experiments, modes):
            for exp in experiments_unique:
                if exp == experiment:
                    output[exp].append(mode)
                else:
                    output[exp].append(None)

        # Merging entries with the same time
        pos_to_delete = list()
        for pos in range(len(output['time']) - 1):
            if output['time'][pos + 1] == output['time'][pos]:
                for exp in experiments_unique:
                    if output[exp][pos] is not None and \
                       output[exp][pos + 1] is None:
                        output[exp][pos + 1] = output[exp][pos]
                pos_to_delete.append(pos)

        # Starting from the end to avoid keys shifting
        pos_to_delete.reverse()
        for pos in pos_to_delete:
            for key in output:
                del output[key][pos]

        out_df = pd.DataFrame(output)
        # Filling the NaN fields with the last not NaN value in the column
        out_df.fillna(method='ffill', inplace=True)

        return out_df
