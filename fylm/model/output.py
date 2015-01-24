from fylm.model.base import BaseTextFile, BaseSet
from fylm.model.constants import Constants
import logging
import re

log = logging.getLogger("fylm")


class OutputSet(BaseSet):
    def __init__(self, experiment):
        super(OutputSet, self).__init__(experiment, "output")
        self._model = Output
        self._regex = re.compile(r"""\d_\d+.txt""")

    @property
    def _expected(self):
        """
        Yields instantiated children of BaseFile that represent the work we expect to have done.

        """
        assert self._model is not None
        for field_of_view in self._fields_of_view:
            for channel_number in xrange(Constants.NUM_CATCH_CHANNELS):
                model = self._model()
                model.time_period = 0  # output files are for every time period
                model.field_of_view = field_of_view
                model.channel_number = channel_number
                model.base_path = self.base_path
                model.time_periods = self._time_periods
                yield model


class Output(BaseTextFile):
    """
    Models the output file that is used by Matlab to generate figures. No methods for reading the files exist
    as we never use this for anything in fylm_critic - it's just the final results.

    Each file holds data for one channel in one field of view for all time periods.

    """
    def __init__(self):
        super(Output, self).__init__()
        self.field_of_view = None
        self.channel_number = None
        self.timestamp_set = None  # TimestampSet
        self.annotation = None  # ChannelAnnotationGroup or None
        self.fluorescence_data = None
        self.time_periods = None  # [<int>]

    @property
    def lines(self):
        for time_period in self.time_periods:
            if self.annotation:
                cell_lengths = self.annotation.get_cell_lengths(time_period)
            # TODO: load fluorescence data here
            for time_index, timestamp in self.timestamp_set.get_data(self.field_of_view, time_period):
                if self.annotation:
                    length = cell_lengths.get(time_index)
                else:
                    length = None
                yield "%s\t%s" % (timestamp, length if length is not None else "NaN")

    @property
    def filename(self):
        """
        We increase the channel number by one for compatibility with the Matlab script.

        """
        return "%s_%s.txt" % (str(int(self.field_of_view) + 1),
                              str(int(self.channel_number) + 1))