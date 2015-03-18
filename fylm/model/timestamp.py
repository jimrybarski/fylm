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
        row = self._table.row
        image = [i for i in image_set][0]
        if image.channel == "" and image.z_level == 0:
            row['time_period'] = time_period
            row['field_of_view'] = image_set.field_of_view
            row['time_index'] = self._index
            row['timestamp'] = image.timestamp

            self._table.add(image.timestamp + last_timestamp)
            self._index += 1

    # def add(self, timestamp):
    #     index = 1 if not self._timestamps.keys() else max(self._timestamps.keys()) + 1
    #     self._timestamps[index] = float(timestamp)

    # @property
    # def last(self):
    #     """
    #     Finds the last timestamp for this file.
    #
    #     """
    #     try:
    #         last = max(self._timestamps.keys())
    #     except ValueError as e:
    #         log.error("Tried to get last timestamp, but there are none.")
    #         raise e
    #     else:
    #         return self._timestamps[last]