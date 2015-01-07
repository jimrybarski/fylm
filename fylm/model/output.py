from collections import defaultdict
from fylm.model.base import BaseTextFile
import logging

log = logging.getLogger("fylm")


class Output(BaseTextFile):
    """
    Models the output file that is used by Matlab to generate figures. No methods for reading the files exist
    as we never use this for anything in fylm_critic - it's just the final results.

    Each file holds data for one channel in one field of view for all timepoints.

    """
    def __init__(self):
        super(Output, self).__init__()
        self.field_of_view = None
        self.channel_number = None
        self.timestamp_set = None  # TimestampSet
        self.annotation = None  # ChannelAnnotationGroup
        self.fluorescence_data = None
        self.time_periods = None  # [<int>]

    @property
    def lines(self):
        for time_period in self.time_periods:
            cell_lengths = self.annotation.get_cell_lengths(time_period)
            # TODO: load fluorescence data here
            for time_index, timestamp in self.timestamp_set.get_data(self.field_of_view, time_period).items():
                length = cell_lengths.get(time_index)
                yield "%s\t%s" % (timestamp, length if length is not None else "NaN")

    @property
    def filename(self):
        return "%s_%s.txt" % (self.field_of_view, self.channel_number)