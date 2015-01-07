"""
%%% FYLM Critic output data:
%%% separate files for each catch channel
%%% no separate files for Time Periods
%%% times are all relative to beginning of experiment
%%% fluorescence data is alphabetical by name in Elements

"""
from collections import defaultdict
from fylm.model.base import BaseTextFile
from fylm.model.constants import Constants
import logging
import re

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
        self.channel = None
        self._data = defaultdict(dict)
        self.timestamp_set = None  # TimestampSet
        self.annotation = None  # ChannelAnnotationGroup
        self.fluorescence_data = None
        self.time_periods = None

    @property
    def lines(self):
        for time_period in self.time_periods:
            cell_lengths = self.annotation.get_cell_lengths(time_period)
            # TODO: load fluorescence data here
            for time_index, timestamp in self.timestamp_set.get_data(self.field_of_view, time_period):
                yield "%s %s" % (timestamp, cell_lengths.get(time_index))

    def add_cell_length(self, time_index, length):
        if length < 10:
            log.warn("Abnormally short cell length! TP:%s FOV:%s Time index:%s" % (self.timepoint,
                                                                                   self.field_of_view,
                                                                                   time_index))
        self._data[time_index] = int(length)