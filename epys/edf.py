import pandas as pd


class EDF:

    def __init__(self, fname):
        # Variable initialization
        self.WTF = list()
        self.meta = dict()
        self.header = list()
        self.variables = dict()
        self.include_files = list()

        # Tables to fill in order as they appear in the file
        self.DATA_STORES = None
        self._data_stores = dict()
        self.PIDS = None
        self._pids = dict()
        self.FTS = None
        self._fts = dict()
        self.FOV = None
        self._fov = {"FOV": [], "FOV_lookat": [], "FOV_upvector": [],
                     "FOV_type": [], "FOV_algorithm": [],
                     "FOV_geometric_angles": [], "FOV_geometric_pixels": [],
                     "FOV_sub_view": [], "FOV_straylight_angles": [],
                     "FOV_straylight_duration": [], "FOV_active": [],
                     "FOV_image_timing": [], "FOV_imaging": [],
                     "FOV_pitch": [], "FOV_yaw": []}
        self.AREA = None
        self._area = dict()
        self.MODULES = None
        self._modules = {"Module": [], "Module_level": [],
                         "Module_dataflow": [], "Module_PID": [],
                         "Module_aux_PID": [], "Sub_modules": [],
                         "Nr_of_module_states": []}
        self.MODULE_STATES = None
        self._module_states = {"Module_state": [], "MS_PID": [],
                               "MS_aux_PID": [], "MS_power": [],
                               "MS_power_parameter": [], "MS_data_rate": [],
                               "MS_data_rate_parameter": [],
                               "MS_aux_data_rate": [], "MS_constraints": [],
                               "Repeat_action": [], "MS_pitch": [],
                               "MS_yaw": []}
        self.MODES = None
        self._modes = {"Mode": [], "Mode_class": [], "Module_states": [],
                       "Internal_clock": [], "PID_enable_flags": [],
                       "Nominal_power": [], "Power_parameter": [],
                       "Nominal_data_rate": [], "Data_rate_parameter": [],
                       "Mode_aux_data_rate": [], "Equivalent_power": [],
                       "Equivalent_data_rate": [], "Mode_transitions": [],
                       "Mode_actions": [], "Mode_constraints": []}
        self.PARAMETERS = None
        self._parameters = {"Parameter": [], "Parameter_alias": [],
                            "State_parameter": [], "Parameter_action": [],
                            "Raw_type": [], "Eng_type": [],
                            "Default_value": [], "Unit": [], "Raw_limits": [],
                            "Eng_limits": [], "Resource": [],
                            "Value_alias": [], "Nr_of_parameter_values": []}
        self.PARAMETER_VALUES = None
        self._parameter_values = {"Parameter_value": [], "Parameter_uas": [],
                                  "Parameter_uwr": [], "Parameter_run": []}
        self.ACTIONS = None
        self._actions = {"Action": [], "Action_alias": [], "Action_level": [],
                         "Action_type": [], "Action_subsystem": [],
                         "Action_parameters": [], "Internal_variables": [],
                         "Computed_parameters": [], "Duration": [],
                         "Minimum_duration": [], "Compression": [],
                         "Separation": [], "Action_dataflow": [],
                         "Action_PID": [], "Power_increase": [],
                         "Data_rate_increase": [], "Data_volume": [],
                         "Power_profile": [], "Data_rate_profile": [],
                         "Write_to_Z_record": [], "Action_power_check": [],
                         "Action_data_rate_check": [], "Obs_ID": [],
                         "Update_at_start": [], "Update_when_ready": [],
                         "Action_constraints": [], "Run_type": [],
                         "Run_start_time": [], "Run_actions": []}
        self.CONSTRAINTS = None
        self._constraints = dict()

        # Keywords to detect in the filed linked to their reading functions
        self.keywords = {'FOV': self._read_fov, 'MODULE': self._read_module,
                         'MODE': self._read_mode,
                         'PARAMETER': self._read_parameter,
                         'ACTION': self._read_action}

        # Loading the given file
        self.load(fname)

    def load(self, fname):
        # Storing the name of the file for editting purposes
        self.fname = fname

        with open(fname) as f:
            content = f.readlines()
            # Closing the file
            f.close()
            content = self._concatenate_lines(content)

        lines_to_remove = 0
        # Read Header
        for line in content:
            if '\n' in line[0]:
                pass
            elif '#' in line.split()[0][0]:
                self.header.append(line)
                self._read_metada(line)
            else:
                break
            # Removing the line from content
            lines_to_remove += 1
        content = content[lines_to_remove:]

        lines_to_remove = 0
        # Read other entries
        for line in content:
            if '\n' in line[0]:
                pass
            else:
                l = line.split()
                # We have found a variable
                if ':' in l[0][-1]:
                    # Checking if we have already found a keyword
                    if l[0][:-1].upper() in self.keywords:
                        break
                    else:
                        self.variables[l[0][:-1]] = l[1:]
                # We have found a comment
                elif '#' in l[0][0]:
                    self.WTF.append(line)
                else:
                    break
            # Removing the line from content
            lines_to_remove += 1
        content = content[lines_to_remove:]

        pos = 0
        while pos < len(content):
            l = content[pos].split()
            if len(l) > 1 and l[0][:-1].upper() in self.keywords:
                pos += self.keywords[l[0][:-1].upper()](content[pos:])
            else:
                pos += 1

        # Creating the pandas tables
        self._convert_dictionaries_into_dataframes()

    def _concatenate_lines(self, content):
        out = list()
        line = ""
        for l in content:
            # Concatening lines if '\' found
            if '\\' in l and '#' not in l[0] and \
               '\\' not in l[l.index('\\') + 1]:
                line += l[:l.index('\\')]
                # Continues with the next iteration of the loop
                continue

            # If there was no concatenation of lines
            if len(line) == 0:
                line = l
            # If we were concatenating, we concatenate the last one
            else:
                if '#' in l:
                    line += l[:l.index('#')]
                else:
                    line += l

            if line[0] == '\n':
                out.append(line)
            else:
                out.append(' '.join(line.split()))
            line = ""
        return out

    def _read_metada(self, line):
        if ': ' in line:
            self.meta[line[1:line.index(': ')].strip()] = \
                line[line.index(': ') + 1:-1].strip()

    def _read_data_stores(self, content):
        print ("data store detected")
        return 1

    def _read_fov(self, content):
        counter = 0
        for line in content:
            line = line.split()
            if len(line) > 1:
                if line[0][:-1] in self._fov:
                    # If another FOV detected we ensure to keep same length
                    # of all the elements in the dictionary
                    if line[0] == 'FOV:':
                        self._fov = \
                            self._add_none_to_empty_fields(self._fov)
                    if len(line[1:]) == 1:
                        self._fov[line[0][:-1]].append(line[1])
                    else:
                        self._fov[line[0][:-1]].append(line[1:])
                elif '#' in line[0][0]:
                    pass
                else:
                    self._fov = \
                        self._add_none_to_empty_fields(self._fov)
                    break
            counter += 1

        return counter

    def _read_module(self, content):
        counter = 0
        for line in content:
            line = line.split()
            if len(line) > 1:
                if line[0][:-1] in self._modules:
                    # If another MODULE detected we ensure to keep same
                    # length of all the elements in the dictionary
                    if line[0][:-1].upper() == 'MODULE':
                        self._modules = \
                            self._add_none_to_empty_fields(self._modules)
                    if len(line[1:]) == 1:
                        self._modules[line[0][:-1]].append(line[1])
                    else:
                        self._modules[line[0][:-1]].append(line[1:])
                elif line[0][:-1] in self._module_states:
                    # If another MODULE_STATE detected we ensure to keep
                    # same length of all the elements in the dictionary
                    if line[0][:-1].upper() == 'MODULE_STATE':
                        # Adding module name for every module state
                        if isinstance(self._modules['Module'][-1], list):
                            line[1] = self._modules['Module'][-1][0] \
                                + " - " + line[1]
                        else:
                            line[1] = self._modules['Module'][-1] \
                                + " - " + line[1]
                        self._module_states = \
                            self._add_none_to_empty_fields(self._module_states)
                    if len(line[1:]) == 1:
                        self._module_states[line[0][:-1]].append(line[1])
                    else:
                        self._module_states[line[0][:-1]].append(line[1:])
                elif '#' in line[0][0]:
                    pass
                else:
                    self._modules = \
                        self._add_none_to_empty_fields(self._modules)
                    self._module_states = \
                        self._add_none_to_empty_fields(self._module_states)
                    break
            counter += 1

        return counter

    def _read_mode(self, content):
        counter = 0
        for line in content:
            line = line.split()
            if len(line) > 1:
                if line[0][:-1] in self._modes:
                    # If another MODE detected we ensure to keep same
                    # length of all the elements in the dictionary
                    if line[0][:-1].upper() == 'MODE':
                        self._modes = \
                            self._add_none_to_empty_fields(self._modes)
                    if len(line[1:]) == 1:
                        self._modes[line[0][:-1]].append(line[1])
                    else:
                        self._modes[line[0][:-1]].append(line[1:])
                elif '#' in line[0][0]:
                    pass
                else:
                    self._modes = \
                        self._add_none_to_empty_fields(self._modes)
                    break
            counter += 1

        return counter

    def _read_parameter(self, content):
        counter = 0
        for line in content:
            line = line.split()
            if len(line) > 1:
                if line[0][:-1] in self._parameters:
                    # If another PARAMETER detected we ensure to keep same
                    # length of all the elements in the dictionary
                    if line[0][:-1].upper() == 'PARAMETER':
                        self._parameters = \
                            self._add_none_to_empty_fields(self._parameters)
                    if len(line[1:]) == 1:
                        self._parameters[line[0][:-1]].append(line[1])
                    else:
                        self._parameters[line[0][:-1]].append(line[1:])
                elif line[0][:-1] in self._parameter_values:
                    # If another PARAMETER VALUE detected we ensure to keep
                    # same length of all the elements in the dictionary
                    if line[0][:-1].upper() == 'PARAMETER_VALUE':
                        # Adding module name for every module state
                        if isinstance(self._parameters['Parameter'][-1], list):
                            line[1] = self._parameters['Parameter'][-1][0] \
                                + " - " + line[1]
                        else:
                            line[1] = self._parameters['Parameter'][-1] \
                                + " - " + line[1]
                        self._parameter_values = \
                            self._add_none_to_empty_fields(
                                self._parameter_values)
                    if len(line[1:]) == 1:
                        self._parameter_values[line[0][:-1]].append(line[1])
                    else:
                        self._parameter_values[line[0][:-1]].append(line[1:])
                elif '#' in line[0][0]:
                    pass
                else:
                    self._parameters = \
                        self._add_none_to_empty_fields(self._parameters)
                    self._parameter_values = \
                        self._add_none_to_empty_fields(self._parameter_values)
                    break
            counter += 1

        return counter

    def _read_action(self, content):
        counter = 0
        for line in content:
            line = line.split()
            if len(line) > 1:
                if line[0][:-1] in self._actions:
                    # If another ACTION detected we ensure to keep same
                    # length of all the elements in the dictionary
                    if line[0][:-1].upper() == 'ACTION':
                        self._actions = \
                            self._add_none_to_empty_fields(self._actions)
                    if len(line[1:]) == 1:
                        self._actions[line[0][:-1]].append(line[1])
                    else:
                        self._actions[line[0][:-1]].append(line[1:])
                elif '#' in line[0][0]:
                    pass
                else:
                    self._actions = \
                        self._add_none_to_empty_fields(self._actions)
                    break
            counter += 1

        return counter

    def _add_none_to_empty_fields(self, dictionary):
        # Adding None value to the empty fields
        maximum = max(
            [len(dictionary[x]) for x in dictionary])
        for x in dictionary:
            if len(dictionary[x]) < maximum:
                dictionary[x].append(None)
        return dictionary

    def _convert_dictionaries_into_dataframes(self):
        self.FOV = pd.DataFrame(self._fov)
        self.MODES = pd.DataFrame(self._modes)
        self.MODULES = pd.DataFrame(self._modules)
        self.MODULE_STATES = pd.DataFrame(self._module_states)
        self.PARAMETERS = pd.DataFrame(self._parameters)
        self.PARAMETER_VALUES = pd.DataFrame(self._parameter_values)
        self.ACTIONS = pd.DataFrame(self._actions)
