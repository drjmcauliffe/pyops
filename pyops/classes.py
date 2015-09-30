class edf:

    content = []
    size = 0

    def __init__(self, fname):
        print("reading edf...")
        with open(fname, 'r') as fh:
            for line in fh:
                self.content.append(line)
        self.content = self.content[1:]
        self.size = len(self.content)

    def __str__(self):
        return self.content[0]


class erf:

    def __init__(self, fname):
        print("reading erf...")
        with open(fname, 'r') as fh:
            for line in fh:
                print line


class evf:

    def __init__(self, fname):
        print("reading evf...")
        with open(fname, 'r') as fh:
            for line in fh:
                print line


class itl:

    def __init__(self, fname):
        print("reading itl...")
        with open(fname, 'r') as fh:
            for line in fh:
                print line
