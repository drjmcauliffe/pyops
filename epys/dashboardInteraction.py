import os
from epys.read import Modes, powertable
from bokeh.plotting import show, output_notebook, gridplot


class Dashboard():

    def __init__(self):
        # Hidding anoying warnings on the top of the plot
        output_notebook(hide_banner=True)

    def load_directory(self, directory):
        if os.path.isdir(directory):
            self.directory = directory
        else:
            print ("I don't think that directory exists...")
            raise NameError('Directory not found')

        files = [os.path.join(directory, f) for f in os.listdir(directory)
                 if os.path.isfile(os.path.join(directory, f))]

        for f in files:
            if "power_avg_csv" in f:
                self.load_power_avg_file(f)
            if "modes_csv" in f:
                self.load_modes_file(f)
            if "module_states_csv" in f:
                self.load_module_states_file(f)

    def load_power_avg_file(self, file_name):
        if os.path.isfile(file_name):
            self.power_avg_file = file_name
            self.powertable = powertable(file_name)
        else:
            print ("I don't think that file exists...")
            raise NameError('File not found')

    def load_data_rate_avg_file(self, file_name):
        if os.path.isfile(file_name):
            self.data_rate_avg_file = file_name
        else:
            print ("I don't think that file exists...")
            raise NameError('File not found')

    def load_modes_file(self, file_name):
        if os.path.isfile(file_name):
            self.modes_file = file_name
            self.modes = Modes(file_name)
        else:
            print ("I don't think that file exists...")
            raise NameError('File not found')

    def load_module_states_file(self, file_name):
        if os.path.isfile(file_name):
            self.module_states_file = file_name
            self.module_states = Modes(file_name)
        else:
            print ("I don't think that file exists...")
            raise NameError('File not found')

    def _brewer_power_plot(self, instruments=None, x_range=None):
        return self.powertable.get_brewer_plot(instruments, x_range)

    def _modes_schedule_plot(self, x_range=None):
        return self.modes.get_plot_schedule(x_range)

    def _module_states_schedule_plot(self, x_range=None):
        return self.module_states.get_plot_schedule(x_range)

    def launch(self):
        top_left = self._brewer_power_plot()
        top_right = self._brewer_power_plot(['MERTIS', 'BELA'], top_left.x_range)
        bottom_left = self._modes_schedule_plot(top_left.x_range)
        bottom_right = self._module_states_schedule_plot(top_left.x_range)

        p = gridplot([[top_left, top_right], [bottom_left, bottom_right]])

        show(p)
