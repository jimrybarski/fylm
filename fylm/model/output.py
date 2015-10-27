from fylm.model.base import BaseTextFile, BaseSet
from fylm.model.constants import Constants
import logging
import re

#log = logging.getLogger(__name__)


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
        self.fluorescence_set = None
        self.time_periods = None  # [<int>]

    @property
    def lines(self):
        for time_period in self.time_periods:
            # log.debug("Getting new fl model tp %s" % time_period)
            fl_model = self.fluorescence_set.get_model(self.field_of_view, time_period, self.channel_number)
            # log.critical("%s %s" % (self.channel_number, fl_model.channel_number if fl_model else "False"))
            for time_index, timestamp in self.timestamp_set.get_data(self.field_of_view, time_period):
                if self.annotation:
                    length = self.annotation.get_cell_lengths(time_period, time_index - 1)  # fixes off-by-one error
                else:
                    length = None
                line = "%s\t%s" % (timestamp, length if length is not None else "NaN")
                if fl_model and length:

                    for channel_name in sorted(fl_model.channel_names):
                        # log.debug("channel name %s" % channel_name)
                        # log.debug("*** %s %s %s %s" % (time_period, time_index, fl_model.field_of_view, fl_model.channel_number))
                        try:
                            mean, stddev, median, area, centroid = fl_model.get_measurement(time_index, channel_name)
                        except ValueError:
                            line += "\tNaN" * 5
                        else:
                            fl_line = "\t%s\t%s\t%s\t%s\t%s" % (mean, stddev, median, area, centroid)
                            # log.debug(fl_line)
                            line += fl_line
                else:
                    for _ in range(self.fluorescence_set.fl_channel_count):
                        line += "\tNaN\tNaN\tNaN\tNaN\tNaN"
                # log.debug(line)
                yield line

    @property
    def filename(self):
        """
        We increase the channel number by one for compatibility with the Matlab script.

        """
        return "%s_%s.txt" % (str(int(self.field_of_view) + 1),
                              str(int(self.channel_number) + 1))
