import os
from epys.read import Modes, powertable, datatable
from bokeh.plotting import show, output_notebook, vplot, gridplot
from bokeh.io import vform
from bokeh.models.widgets import Panel, Tabs
from bokeh.models.widgets import CheckboxButtonGroup


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
            if "power_avg2_csv" in f:
                self.load_power_avg_file(f)
            if "modes2_csv" in f:
                self.load_modes_file(f)
            if "module_states2_csv" in f:
                self.load_module_states_file(f)
            if "data_rate_avg2_csv" in f:
                self.load_data_rate_avg_file(f)

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
            self.data_rate = datatable(file_name)
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

    def _power_plot(self, instruments):
        return self.powertable.get_power_plot(instruments)

    def _data_plot(self, instruments, parameters, x_range=None):
        return self.data_rate.get_data_plot(instruments, parameters, x_range)

    def _modes_schedule_plot(self, x_range=None):
        return self.modes.get_plot_schedule(x_range)

    def _module_states_schedule_plot(self, x_range=None):
        return self.module_states.get_plot_schedule(x_range)

    def _merged_schedule_plot(self, instruments, get_plot, x_range=None):
        return self.module_states.merge_schedule(self.modes.data, instruments,
                                                 get_plot, x_range)

    def launch(self, instruments=None, parameters=None):
        if instruments is None:
            instruments = self.powertable.instruments
        p1 = self._power_plot(instruments)
        p2 = self._data_plot(instruments, parameters, p1.x_range)
        p3 = self._merged_schedule_plot(instruments, True, p1.x_range)
        # bottom_right = self._module_states_schedule_plot(top_left.x_range)

        # put all the plots in a VBox
        p = vplot(p1, p2, p3)

        show(p)

    def launch_tab(self, instruments=None):
        if instruments is None:
            instruments = self.powertable.instruments
        top_left = self._brewer_power_plot()
        top_right = self._brewer_power_plot(instruments, top_left.x_range)
        bottom_left = self._merged_schedule_plot(instruments, True)

        active = [self.powertable.instruments.index(x) for x in instruments]
        checkbox_button_group = CheckboxButtonGroup(
            labels=self.powertable.instruments, active=active)

        p1 = vform(checkbox_button_group, gridplot([[top_left, top_right]]))
        tab2 = Panel(child=p1, title="Power Stacked")
        tab3 = Panel(child=bottom_left, title="Timeline")
        tabs = Tabs(tabs=[tab2, tab3])
        show(tabs)
