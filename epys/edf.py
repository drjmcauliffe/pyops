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
        self._modules = dict()
        self.MODES = None
        self._modules = dict()
        self.PARAMETERS = None
        self._parameters = dict()
        self.ACTIONS = None
        self._actions = dict()
        self.CONSTRAINTS = None
        self._constraints = dict()

        # Keywords to detect in the filed
        self.keywords = {'FOV': self._read_fov, 'MODULE': self._read_module,
                         'MODE': self._read_mode}

        # Loading the given file
        self.load(fname)

    def load(self, fname):
        # Storing the name of the file for editting purposes
        self.fname = fname

        with open(fname) as f:
            content = f.readlines()
        # Closing the file
        f.close()

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
                    if l[0][-1].upper() in self.keywords:
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

    def _read_metada(self, line):
        if ': ' in line:
            self.meta[line[1:line.index(': ')].strip()] = \
                line[line.index(': ') + 1:-1].strip()

    def _read_data_stores(self, content):
        print "data store detected"
        return 1

    def _read_fov(self, content):
        counter = 0
        line = ""
        for l in content:
            # Concatening lines if '\' found
            if '\\' in l and '#' not in l[0] and \
               '\\' not in l[l.index('\\') + 1]:
                line += l[:l.index('\\')]
                # Continues with the next iteration of the loop
                counter += 1
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

            line = line.split()
            if len(line) > 1:
                if line[0][:-1] in self._fov:
                    if len(line[1:]) == 1:
                        # If another FOV detected we ensure to keep same length
                        # of all the elements in the dictionary
                        if line[0][:-1] == 'FOV':
                            # Adding None value to the empty fields
                            maximum = max(
                                [len(self._fov[x]) for x in self._fov])
                            for x in self._fov:
                                if len(self._fov[x]) < maximum:
                                    self._fov[x].append(None)
                        self._fov[line[0][:-1]].append(line[1])
                    else:
                        self._fov[line[0][:-1]].append(line[1:])
                else:
                    # Adding None value to the empty fields
                    maximum = max([len(self._fov[x]) for x in self._fov])
                    for x in self._fov:
                        if len(self._fov[x]) < maximum:
                            self._fov[x].append(None)
                    break
            counter += 1
            line = ""

        return counter

    def _read_module(self, content):
        print "module detected"
        return 1

    def _read_mode(self, content):
        print "mode detected"
        return 1

    def _convert_dictionaries_into_dataframes(self):
        self.FOV = pd.DataFrame(self._fov)
