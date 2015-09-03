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
        self.PIDS = None
        self.FTS = None
        self.FOV = None
        self.AREA = None
        self.MODULES = None
        self.MODES = None
        self.PARAMETERS = None
        self.ACTIONS = None
        self.CONSTRAINTS = None

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
                    self.variables[l[0][:-1]] = l[1:]
                # We have found a comment
                elif '#' in l[0][0]:
                    self.WTF.append(line)
                else:
                    break
            # Removing the line from content
            lines_to_remove += 1
        content = content[lines_to_remove:]

    """

        lines_to_remove = 0
        # Read Data Stores
        for line in content:

            # Removing the line from content
            lines_to_remove += 1
        content = content[lines_to_remove:]
        # Read PIDS


        # Read FTS


        # Read FOV


        # Read AREA


        # Read MODULES


        # Read MODES


        # Read PARAMETERES


        # Read ACTIONS


        # Read CONSTRAINTS

    """

    def _read_metada(self, line):
        if ': ' in line:
            self.meta[line[1:line.index(': ')].strip()] = \
                line[line.index(': ') + 1:-1].strip()

    def _read_data_stores(self):
        pass
