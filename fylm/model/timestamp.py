from tables import IsDescription, UInt8Col, UInt16Col, Float64Col
from fylm.model.base import BaseModel
import logging

log = logging.getLogger(__name__)


class Timestamps(BaseModel):
    class Table(IsDescription):
        time_period = UInt8Col()
        field_of_view = UInt8Col()
        time_index = UInt16Col()
        timestamp = Float64Col()

    def __init__(self, table, experiment):
        super(Timestamps, self).__init__(required_data_source="nd2")
        self._table = table
        self._nd2_metadata = experiment.nd2_metadata
        self._index = 0
        self._needed = None
        self._current_time_period = None
        self._last_timestamps = None

    @property
    def time_periods_needed(self):
        if self._needed is None:
            self._needed = []
            for time_period, fields_of_view, length, shape in self._nd2_metadata:
                # see how many timestamps we have for each time period
                record_count = len([row for row in self._table.iterrows() if row['time_period'] == time_period])
                # each field of view should have one timestamp per cycle
                if record_count != fields_of_view * length:
                    log.debug("Expected %s timestamps, found %s for time period %s. Need to get timestamps for this TP." % (fields_of_view * length, record_count, time_period))
                    self._needed.append(time_period)
        return self._needed

    @property
    def name(self):
        return "timestamps"

    def extract_data(self, time_period, image_set):
        if time_period != self._current_time_period:
            self._update_last_timestamp(time_period)
        row = self._table.row
        image = [i for i in image_set][0]
        if image.channel == "" and image.z_level == 0:
            row['time_period'] = time_period
            row['field_of_view'] = image_set.field_of_view
            row['time_index'] = self._index
            row['timestamp'] = image.timestamp + self._last_timestamps[image_set.field_of_view]
            row.append()
            self._index += 1

    def _update_last_timestamp(self, time_period):
        if time_period - 1 in self.time_periods_needed:
            raise ValueError("Attempted to get last timestamps from unfinished time period! Probably iterated over nd2s out of order")
        for field_of_view in xrange(self._nd2_metadata.fields_of_view):
            self._last_timestamps[field_of_view] = max([r['timestamp'] for r in self._table.iterrows() if r['time_period'] == time_period - 1 and r['field_of_view'] == field_of_view])
        log.debug("Updated last timestamps: %s" % self._last_timestamps)