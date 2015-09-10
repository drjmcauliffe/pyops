import pandas as pd
import os
# from prettytable import PrettyTable


class EDF:

    def __init__(self, fname=None):
        # Variable initialization
        self.WTF = list()
        self.meta = dict()
        self.header = list()
        self.variables = dict()
        self.experiment = "Not said or not in the proper format."
        self.include_files = list()

        # Tables to fill in order as they appear in the file
        self.DATA_BUSES = DataBuses()
        self._global_properties = dict.fromkeys(
            ["Local_memory", "Dataflow", "Dataflow_PID", "Dataflow_aux_PID",
             "Data_volume_data_rate", "HK_data_volume", "TM_frame_overhead",
             "Power_profile_check", "Data_rate_profile_check",
             "Exclusive_subsystems", "Global_actions", "Global_constraints"])
        # For now we just represent the dictionary...
        self.GLOBAL_PROPERTIES = self._global_properties
        self.DATA_STORES = DataStores()
        self.PIDS = PIDs()
        self.FTS = FTS()
        self.FOVS = FOVs()
        self.AREAS = Areas()
        self.MODULES = Modules()
        self.MODES = Modes()
        self.PARAMETERS = Parameters()
        self.ACTIONS = Actions()
        self.CONSTRAINTS = Constraints()

        # Keywords to detect in the filed linked to their reading functions
        self.keywords = {'DATA_BUS': self.DATA_BUSES.read,
                         'DATA_STORE': self.DATA_STORES.read,
                         'PID': self.PIDS.read, 'FTS': self.FTS.read,
                         'AREA': self.AREAS.read,
                         'FOV': self.FOVS.read, 'MODULE': self.MODULES.read,
                         'MODE': self.MODES.read,
                         'PARAMETER': self.PARAMETERS.read,
                         'ACTION': self.ACTIONS.read,
                         'CONSTRAINT': self.CONSTRAINTS.read}

        # Loading the given file
        if fname is not None:
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
            if len(line) > 1:
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

        pos = 0
        while pos < len(content):
            l = content[pos].split()
            if len(l) > 0:
                if '\n' in content[pos][0]:
                    pos += 1
                else:
                    # We have found a variable
                    if ':' in l[0][-1]:
                        # Checking if we have found a global property
                        if l[0][:-1] in self._global_properties:
                            self._global_properties[l[0][:-1]] = \
                                ' '.join(l[1:])
                            pos += 1
                        # Checking if we have found a keyword
                        elif l[0][:-1].upper() not in self.keywords:
                            pos += self._read_variables(l)
                        elif len(l) > 1 and l[0][:-1].upper() in self.keywords:
                            pos += self.keywords[l[0][:-1].upper()](
                                content[pos:])
                        else:
                            pos += 1
                    # We have found a comment
                    elif '#' in l[0][0]:
                        self.WTF.append(line)
                        pos += 1
            else:
                pos += 1

        # Removing the content from memory
        content = None
        # Creating the pandas tables
        self._convert_dictionaries_into_dataframes()

    def check_consistency(self):
        if self.check_if_included_files_exist_in_directory():
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
                output = "***[WARNING]***: "
                output += "It seems as if " + fname + " is not in the same "
                output += "directory as " + os.path.basename(self.fname)
                print (output)
                # Perhaps raising an exception here in the future...

        return files_exist

    def _concatenate_lines(self, content):
        out = list()
        line = ""
        for l in content:
            # Concatening lines if '\' found
            if '\\' in l and '#' not in l[0] and \
               '\\' not in l[l.index('\\') + 1]:
                line += ' ' + l[:l.index('\\')]
                # Continues with the next iteration of the loop
                continue

            # If there was no concatenation of lines
            if len(line) == 0:
                line = l
            # If we were concatenating, we concatenate the last one
            else:
                if '#' in l:
                    line += ' ' + l[:l.index('#')]
                else:
                    line += ' ' + l

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

    def _read_variables(self, line):
        if 'Include_file:' in line or 'Include:' in line:
            self.include_files.append(line[1:])
        elif 'Experiment:' in line:
            self.experiment = ' '.join(line[1:])
        else:
            self.variables[line[0][:-1]] = ' '.join(line[1:])
        return 1

    def _how_many_brackets_following(self, line):
        count = 0
        for words in line:
            if words[0] == '[' and words[-1] == ']':
                count += 1
            else:
                break
        return count

    def _add_none_to_empty_fields(self, dictionary):
        # Adding None value to the empty fields
        maximum = max(
            [len(dictionary[x]) for x in dictionary])
        for x in dictionary:
            if len(dictionary[x]) < maximum:
                dictionary[x].append(None)
        return dictionary

    def _convert_dictionaries_into_dataframes(self):
        self.DATA_BUSES._create_pandas()
        self.DATA_STORES._create_pandas()
        self.PIDS._create_pandas()
        self.FTS._create_pandas()
        self.FOVS._create_pandas()
        self.AREAS._create_pandas()
        self.MODES._create_pandas()
        self.MODULES._create_pandas()
        self.PARAMETERS._create_pandas()
        self.ACTIONS._create_pandas()
        self.CONSTRAINTS._create_pandas()


class DataBuses(EDF):

    def __init__(self):
        self.Table = None
        self._data_buses = {"Data_bus": [], "Data_bus_rate_warning": [],
                            "Data_bus_rate_limit": []}

    def read(self, content):
        counter = 0
        for line in content:
            line = line.split()
            if len(line) > 1:
                if line[0][:-1] in self._data_buses:
                    # If another Data Bus detected we ensure to keep same
                    # length of all the elements in the dictionary
                    if line[0] == 'Data_bus:':
                        self._data_buses = \
                            self._add_none_to_empty_fields(self._data_buses)
                        self._data_buses[line[0][:-1]].append(
                            ' '.join(line[1:]))
                elif '#' in line[0][0]:
                    pass
                else:
                    self._data_buses = \
                        self._add_none_to_empty_fields(self._data_buses)
                    break
            counter += 1
        self._data_buses = \
            self._add_none_to_empty_fields(self._data_buses)
        return counter

    def _create_pandas(self):
        self.Table = pd.DataFrame(self._data_buses)


class DataStores(EDF):

    def __init__(self):
        self.Table = None
        self._data_stores = {"Label": [], "Memory size": [],
                             "Packet size": [], "Priority": [],
                             "Identifier": [], "Comment": []}

    def read(self, content):
        counter = 0
        for line in content:
            line = line.split()
            if len(line) > 1:
                if line[0] == 'Data_store:':
                    # If another Data Store detected we ensure to keep same
                    # length of all the elements in the dictionary
                    self._data_stores = \
                        self._add_none_to_empty_fields(self._data_stores)
                    pos = self._how_many_brackets_following(line[2:]) + 2
                    if line[pos].upper() == 'SELECTIVE':
                        pos += 1
                    self._data_stores['Label'].append(' '.join(line[1:pos]))
                    prev_pos, pos = pos, \
                        self._how_many_brackets_following(
                            line[pos + 1:]) + pos + 1
                    self._data_stores['Memory size'].append(
                        ' '.join(line[prev_pos:pos]))
                    prev_pos, pos = pos, \
                        self._how_many_brackets_following(
                            line[pos + 1:]) + pos + 1
                    self._data_stores['Packet size'].append(
                        ' '.join(line[prev_pos:pos]))
                    if len(line) > pos:
                        if '#' in line[pos]:
                            self._data_stores['Comment'].append(
                                ' '.join(line[pos:]))
                            continue
                        else:
                            self._data_stores['Priority'].append(line[pos])
                    if len(line) > pos + 1:
                        if '#' in line[pos + 1]:
                            self._data_stores['Comment'].append(
                                ' '.join(line[pos + 1:]))
                            continue
                        else:
                            self._data_stores['Identifier'].append(
                                line[pos + 1])
                    if len(line) > pos + 2:
                        self._data_stores['Comment'].append(
                            ' '.join(line[pos + 2:]))
                elif '#' in line[0][0]:
                    pass
                else:
                    self._data_stores = \
                        self._add_none_to_empty_fields(self._data_stores)
                    break
            counter += 1
        self._data_stores = \
            self._add_none_to_empty_fields(self._data_stores)
        return counter

    def _create_pandas(self):
        cols = ['Label', 'Memory size', 'Packet size', 'Priority',
                'Identifier', 'Comment']
        self.Table = pd.DataFrame(self._data_stores, columns=cols)


class PIDs(EDF):

    def __init__(self):
        self.Table = None
        self._pids = {"PID number": [], "Status": [], "Data Store ID": [],
                      "Comment": []}

    def read(self, content):
        counter = 0
        for line in content:
            line = line.split()
            if len(line) > 1:
                if line[0] == 'PID:':
                    # If another PID detected we ensure to keep same length
                    # of all the elements in the dictionary
                    self._pids = \
                        self._add_none_to_empty_fields(self._pids)
                    self._pids['PID number'].append(line[1])
                    self._pids['Status'].append(line[2])
                    self._pids['Data Store ID'].append(line[3])
                    if len(line) > 4:
                        self._pids['Comment'].append(' '.join(line[4:]))
                elif '#' in line[0][0]:
                    pass
                else:
                    self._pids = \
                        self._add_none_to_empty_fields(self._pids)
                    break
            counter += 1
        self._pids = \
            self._add_none_to_empty_fields(self._pids)
        return counter

    def _create_pandas(self):
        cols = ['PID number', 'Status', 'Data Store ID', 'Comment']
        self.Table = pd.DataFrame(self._pids, columns=cols)


class FTS(EDF):

    def __init__(self):
        self.Table = None
        self._fts = {"Data Store ID": [], "Status": [], "Data Volume": [],
                     "Comment": []}

    def read(self, content):
        counter = 0
        for line in content:
            line = line.split()
            if len(line) > 1:
                if line[0] == 'FTS:':
                    # If another FTS detected we ensure to keep same length
                    # of all the elements in the dictionary
                    self._fts = \
                        self._add_none_to_empty_fields(self._fts)
                    self._fts['Data Store ID'].append(line[1])
                    self._fts['Status'].append(line[2])
                    if len(line) > 4:
                        self._fts['Data Volume'].append(' '.join(line[3:4]))
                    else:
                        self._fts['Data Volume'].append(line[3])
                    if len(line) > 5:
                        self._fts['Comment'].append(' '.join(line[5:]))
                elif '#' in line[0][0]:
                    pass
                else:
                    self._fts = \
                        self._add_none_to_empty_fields(self._fts)
                    break
            counter += 1
        self._fts = \
            self._add_none_to_empty_fields(self._fts)
        return counter

    def _create_pandas(self):
        cols = ['Data Store ID', 'Status', 'Data Volume', 'Comment']
        self.Table = pd.DataFrame(self._fts, columns=cols)


class FOVs(EDF):

    def __init__(self):
        self.Table = None
        self._fov = {"FOV": [], "FOV_lookat": [], "FOV_upvector": [],
                     "FOV_type": [], "FOV_algorithm": [],
                     "FOV_geometric_angles": [], "FOV_geometric_pixels": [],
                     "FOV_sub_view": [], "FOV_straylight_angles": [],
                     "FOV_straylight_duration": [], "FOV_active": [],
                     "FOV_image_timing": [], "FOV_imaging": [],
                     "FOV_pitch": [], "FOV_yaw": []}

    def read(self, content):
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
                    self._fov[line[0][:-1]].append(' '.join(line[1:]))
                elif '#' in line[0][0]:
                    pass
                else:
                    self._fov = \
                        self._add_none_to_empty_fields(self._fov)
                    break
            counter += 1
        self._fov = \
            self._add_none_to_empty_fields(self._fov)
        return counter

    def _create_pandas(self):
        cols = ["FOV", "FOV_lookat", "FOV_upvector", "FOV_type",
                "FOV_algorithm", "FOV_geometric_angles",
                "FOV_geometric_pixels", "FOV_sub_view",
                "FOV_straylight_angles", "FOV_straylight_duration",
                "FOV_active", "FOV_image_timing", "FOV_imaging",
                "FOV_pitch", "FOV_yaw"]
        self.Table = pd.DataFrame(self._fov, columns=cols)


class Areas(EDF):

    def __init__(self):
        self.Table = None
        self._areas = {"Area": [], "Area_orientation": [],
                       "Area_lighting_angle": [], "Area_lighting_duration": []}

    def read(self, content):
        counter = 0
        for line in content:
            line = line.split()
            if len(line) > 1:
                if line[0][:-1] in self._areas:
                    # If another AREA detected we ensure to keep same length
                    # of all the elements in the dictionary
                    if line[0] == 'Area:':
                        self._areas = \
                            self._add_none_to_empty_fields(self._areas)
                    self._areas[line[0][:-1]].append(' '.join(line[1:]))
                elif '#' in line[0][0]:
                    pass
                else:
                    self._areas = \
                        self._add_none_to_empty_fields(self._areas)
                    break
            counter += 1
        self._areas = \
            self._add_none_to_empty_fields(self._areas)
        return counter

    def _create_pandas(self):
        cols = ["Area", "Area_orientation", "Area_lighting_angle",
                "Area_lighting_duration"]
        self.Table = pd.DataFrame(self._areas, columns=cols)


class Modes(EDF):

    def __init__(self):
        self.Table = None
        self._modes = {"Mode": [], "Mode_class": [], "Module_states": [],
                       "Internal_clock": [], "PID_enable_flags": [],
                       "Nominal_power": [], "Power_parameter": [],
                       "Nominal_data_rate": [], "Data_rate_parameter": [],
                       "Mode_aux_data_rate": [], "Equivalent_power": [],
                       "Equivalent_data_rate": [], "Mode_transitions": [],
                       "Mode_actions": [], "Mode_constraints": []}

    def read(self, content):
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
                    self._modes[line[0][:-1]].append(' '.join(line[1:]))
                elif '#' in line[0][0]:
                    pass
                else:
                    self._modes = \
                        self._add_none_to_empty_fields(self._modes)
                    break
            counter += 1
        self._modes = \
            self._add_none_to_empty_fields(self._modes)
        return counter

    def _create_pandas(self):
        cols = ["Mode", "Mode_class", "Module_states", "Internal_clock",
                "PID_enable_flags", "Nominal_power", "Power_parameter",
                "Nominal_data_rate", "Data_rate_parameter",
                "Mode_aux_data_rate", "Equivalent_power",
                "Equivalent_data_rate", "Mode_transitions", "Mode_actions",
                "Mode_constraints"]
        self.Table = pd.DataFrame(self._modes, columns=cols)


class Modules(EDF):

    def __init__(self):
        self.Table = None
        self._modules = {"Module": [], "Module_level": [],
                         "Module_dataflow": [], "Module_PID": [],
                         "Module_aux_PID": [], "Sub_modules": [],
                         "Nr_of_module_states": []}
        self._module_states = {"Module_state": [], "MS_PID": [],
                               "MS_aux_PID": [], "MS_power": [],
                               "MS_power_parameter": [], "MS_data_rate": [],
                               "MS_data_rate_parameter": [],
                               "MS_aux_data_rate": [], "MS_constraints": [],
                               "Repeat_action": [], "MS_pitch": [],
                               "MS_yaw": []}

    def read(self, content):
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
                    self._modules[line[0][:-1]].append(' '.join(line[1:]))
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
                    self._module_states[line[0][:-1]].append(
                        ' '.join(line[1:]))
                elif '#' in line[0][0]:
                    pass
                else:
                    self._modules = \
                        self._add_none_to_empty_fields(self._modules)
                    self._module_states = \
                        self._add_none_to_empty_fields(self._module_states)
                    break
            counter += 1

        self._modules = \
            self._add_none_to_empty_fields(self._modules)
        self._module_states = \
            self._add_none_to_empty_fields(self._module_states)
        return counter

    def _create_pandas(self):
        cols = ["Module", "Module_level", "Module_dataflow", "Module_PID",
                "Module_aux_PID", "Sub_modules", "Nr_of_module_states"]
        self.Table = pd.DataFrame(self._modules, columns=cols)
        cols = ["Module_state", "MS_PID", "MS_aux_PID", "MS_power",
                "MS_power_parameter", "MS_data_rate",
                "MS_data_rate_parameter", "MS_aux_data_rate",
                "MS_constraints", "Repeat_action", "MS_pitch", "MS_yaw"]
        self.Module_states_Table = pd.DataFrame(
            self._module_states, columns=cols)


class Parameters(EDF):

    def __init__(self):
        self.Table = None
        self._parameters = {"Parameter": [], "Parameter_alias": [],
                            "State_parameter": [], "Parameter_action": [],
                            "Raw_type": [], "Eng_type": [],
                            "Default_value": [], "Unit": [], "Raw_limits": [],
                            "Eng_limits": [], "Resource": [],
                            "Value_alias": [], "Nr_of_parameter_values": []}
        self._parameter_values = {"Parameter_value": [], "Parameter_uas": [],
                                  "Parameter_uwr": [], "Parameter_run": []}

    def read(self, content):
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
                    self._parameters[line[0][:-1]].append(' '.join(line[1:]))
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
                    self._parameter_values[line[0][:-1]].append(
                        ' '.join(line[1:]))
                elif '#' in line[0][0]:
                    pass
                else:
                    self._parameters = \
                        self._add_none_to_empty_fields(self._parameters)
                    self._parameter_values = \
                        self._add_none_to_empty_fields(self._parameter_values)
                    break
            counter += 1

        self._parameters = \
            self._add_none_to_empty_fields(self._parameters)
        self._parameter_values = \
            self._add_none_to_empty_fields(self._parameter_values)
        return counter

    def _create_pandas(self):
        cols = ["Parameter", "Parameter_alias", "State_parameter",
                "Parameter_action", "Raw_type", "Eng_type", "Default_value",
                "Unit", "Raw_limits", "Eng_limits", "Resource",
                "Value_alias", "Nr_of_parameter_values"]
        self.Table = pd.DataFrame(self._parameters, columns=cols)
        cols = ["Parameter_value", "Parameter_uas", "Parameter_uwr",
                "Parameter_run"]
        self.Parameter_values_Table = pd.DataFrame(
            self._parameter_values, columns=cols)


class Actions(EDF):

    def __init__(self):
        self.Table = None
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

    def read(self, content):
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
                    self._actions[line[0][:-1]].append(' '.join(line[1:]))
                elif '#' in line[0][0]:
                    pass
                else:
                    self._actions = \
                        self._add_none_to_empty_fields(self._actions)
                    break
            counter += 1

        self._actions = \
            self._add_none_to_empty_fields(self._actions)

        return counter

    def _create_pandas(self):
        cols = ["Action", "Action_alias", "Action_level", "Action_type",
                "Action_subsystem", "Action_parameters", "Internal_variables",
                "Computed_parameters", "Duration", "Minimum_duration",
                "Compression", "Separation", "Action_dataflow", "Action_PID",
                "Power_increase", "Data_rate_increase", "Data_volume",
                "Power_profile", "Data_rate_profile", "Write_to_Z_record",
                "Action_power_check", "Action_data_rate_check", "Obs_ID",
                "Update_at_start", "Update_when_ready", "Action_constraints",
                "Run_type", "Run_start_time", "Run_actions"]
        self.Table = pd.DataFrame(self._actions, columns=cols)


class Constraints(EDF):

    def __init__(self):
        self.Table = None
        self._constraints = {"Constraint": [], "Constraint_type": [],
                             "Severity": [], "Constraint_group": [],
                             "Condition": [], "Resource_constraint": [],
                             "Resource_mass_memory": [],
                             "Parameter_constraint": [],
                             "Condition_experiment": [], "Expression": []}

    def read(self, content):
        counter = 0
        for line in content:
            line = line.split()
            if len(line) > 1:
                if line[0][:-1] in self._constraints:
                    # If another CONSTRAINT detected we ensure to keep same
                    # length of all the elements in the dictionary
                    if line[0][:-1].upper() == 'CONSTRAINT':
                        self._constraints = \
                            self._add_none_to_empty_fields(self._constraints)
                    self._constraints[line[0][:-1]].append(' '.join(line[1:]))
                elif '#' in line[0][0]:
                    pass
                else:
                    self._constraints = \
                        self._add_none_to_empty_fields(self._constraints)
                    break
            counter += 1
        self._constraints = \
            self._add_none_to_empty_fields(self._constraints)
        return counter

    def _create_pandas(self):
        cols = ["Constraint", "Constraint_type", "Severity",
                "Constraint_group", "Condition", "Resource_constraint",
                "Resource_mass_memory", "Parameter_constraint",
                "Condition_experiment", "Expression"]
        self.Table = pd.DataFrame(self._constraints, columns=cols)
