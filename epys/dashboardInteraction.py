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
        """
        This function loads power, data rate, modes and module states
        files from the given directory.

        :param directory: Directory to inspect
        :type directory: string
        :returns: nothing
        """
        if os.path.isdir(directory):
            self.directory = directory
        else:
            print ("I don't think that directory exists...")
            raise NameError('Directory not found')

        # Reading all the files in the given directory
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
        """
        This function loads a powertable object into the Dashboard using
        the given file_name.

        :param file_name: File path
        :type file_name: string
        :returns: nothing
        """
        if os.path.isfile(file_name):
            self.power_avg_file = file_name
            self.powertable = powertable(file_name)
        else:
            print ("I don't think that file exists...")
            raise NameError('File not found')

    def load_data_rate_avg_file(self, file_name):
        """
        This function loads a datatable object into the Dashboard using
        the given file_name.

        :param file_name: File path
        :type file_name: string
        :returns: nothing
        """
        if os.path.isfile(file_name):
            self.data_rate_avg_file = file_name
            self.data_rate = datatable(file_name)
        else:
            print ("I don't think that file exists...")
            raise NameError('File not found')

    def load_modes_file(self, file_name):
        """
        This function loads a Modes object into the Dashboard using
        the given file_name.

        :param file_name: File path
        :type file_name: string
        :returns: nothing
        """
        if os.path.isfile(file_name):
            self.modes_file = file_name
            self.modes = Modes(file_name)
        else:
            print ("I don't think that file exists...")
            raise NameError('File not found')

    def load_module_states_file(self, file_name):
        """
        This function loads a Modes object into the Dashboard using
        the given file_name.

        :param file_name: File path
        :type file_name: string
        :returns: nothing
        """
        if os.path.isfile(file_name):
            self.module_states_file = file_name
            self.module_states = Modes(file_name)
        else:
            print ("I don't think that file exists...")
            raise NameError('File not found')

    def _brewer_power_plot(self, instruments=None, x_range=None):
        """
        This function returns a stacked plot of the power usage for the given
        instruments and linked to a possible x_range.

        :param instruments: list of the instruments to plot
        :type instruments: list of strings
        :param x_range: x_range from another figure to link with
        :type x_range: x_range bokeh format
        :returns: bokeh figure
        """
        return self.powertable.get_brewer_plot(instruments, x_range)

    def _power_plot(self, instruments):
        """
        This function returns a plot of the power usage for the given
        instruments.

        :param instruments: list of the instruments to plot
        :type instruments: list of strings
        :returns: bokeh figure
        """
        return self.powertable.get_power_plot(instruments)

    def _data_plot(self, instruments, parameters=None, x_range=None):
        """
        This function returns a  plot of the data rate for the given
        instruments and linked to a possible x_range. If parameters is not None
        they include the exact parameters to be plotted (Instruement and Value)

        :param instruments: list of the instruments to plot
        :type instruments: list of strings
        :param parameters: list of the exact values to be plotted
        :type parameters: list of tuples of a couple of strings
        :param x_range: x_range from another figure to link with
        :type x_range: x_range bokeh format
        :returns: bokeh figure
        """
        return self.data_rate.get_data_plot(instruments, parameters, x_range)

    def _modes_schedule_plot(self, x_range=None):
        """
        This function returns a plot of the modes timeline, it can be possibly
        linked with some other plot trough the given x_range.

        :param x_range: x_range from another figure to link with
        :type x_range: x_range bokeh format
        :returns: bokeh figure
        """
        return self.modes.get_plot_schedule(x_range)

    def _module_states_schedule_plot(self, x_range=None):
        """
        This function returns a plot of the module states timeline, it can be
        possibly linked with some other plot trough the given x_range.

        :param x_range: x_range from another figure to link with
        :type x_range: x_range bokeh format
        :returns: bokeh figure
        """
        return self.module_states.get_plot_schedule(x_range)

    def _merged_schedule_plot(self, instruments, get_plot=True, x_range=None):
        """
        This function returns a plot of the module states and modes timeline,
        it can be possibly linked with some other plot trough the given x_range
        It is possible to just received the pandas dataframe if we don't want
        to recive the plot throught the get_plot parameter. We can also select
        what instruments to plot through the instruments parameter

        :param instruments: list of the instruments to plot
        :type instruments: list of strings
        :param get_plot: Flag to return a figure or pandas dataframe
        :type get_plot: boolean
        :param x_range: x_range from another figure to link with
        :type x_range: x_range bokeh format
        :returns: if get_plot bokeh figure, else pandas dataframe
        """
        return self.module_states.merge_schedule(self.modes.data, instruments,
                                                 get_plot, x_range)

    def launch(self, instruments=None, parameters=None):
        """
        This function launches the Dashboard with all the plots in the
        aforementioned functions.

        :param instruments: list of the instruments to plot
        :type instruments: list of strings
        :param parameters: list of the exact values to be plotted in the
        data_rate plot
        :type parameters: list of tuples of a couple of strings
        :returns: nothing
        """
        if instruments is None:
            instruments = self.powertable.instruments
        p1 = self._power_plot(instruments)
        p2 = self._data_plot(instruments, parameters, p1.x_range)
        p3 = self._merged_schedule_plot(instruments, True, p1.x_range)

        # Putting all the plots in a VBox
        p = vplot(p1, p2, p3)

        show(p)

    def launch_tab(self, instruments=None):
        """
        This function launches the Dashboard with all the plots in the
        aforementioned functions. In this case tabs are also plotted to select
        between different plots.

        :param instruments: list of the instruments to plot
        :type instruments: list of strings
        :returns: nothing
        """
        if instruments is None:
            instruments = self.powertable.instruments
        top_left = self._brewer_power_plot()
        top_right = self._brewer_power_plot(instruments, top_left.x_range)
        bottom_left = self._merged_schedule_plot(instruments, True)

        # Creating the bottoms at the top for a visual effect. They are not
        # interactive, we would need to launch a bokeh server for that...
        active = [self.powertable.instruments.index(x) for x in instruments]
        checkbox_button_group = CheckboxButtonGroup(
            labels=self.powertable.instruments, active=active)

        # Putting all the plots in the tabs
        p1 = vform(checkbox_button_group, gridplot([[top_left, top_right]]))
        tab2 = Panel(child=p1, title="Power Stacked")
        tab3 = Panel(child=bottom_left, title="Timeline")
        tabs = Tabs(tabs=[tab2, tab3])
        show(tabs)
