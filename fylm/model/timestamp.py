from fylm.model.base import BaseTextFile, BaseSet
import logging
import re

log = logging.getLogger("fylm")


class TimestampSet(BaseSet):
    """
    Models all the timestamps for every set of images.

    """
    def __init__(self, experiment):
        super(TimestampSet, self).__init__(experiment, "timestamp")
        self._model = Timestamps


class Timestamps(BaseTextFile):
    def __init__(self):
        super(Timestamps, self).__init__()
        self.timepoint = None
        self.field_of_view = None
        self._timestamps = {}
        self._line_regex = re.compile(r"""^(?P<index>\d+) (?P<timestamp>\d+\.\d+)""")

    def load(self, data):
        for line in data:
            try:
                index, timestamp = self._parse_line(line)
            except Exception as e:
                log.error("Could not parse line: '%s' because of: %s" % (line, e))
            else:
                self._timestamps[index] = timestamp

    def _parse_line(self, line):
        match = self._line_regex.match(line)
        return int(match.group("index")), float(match.group("timestamp"))

    @property
    def _ordered_data(self):
        for index, timestamp in sorted(self._timestamps.items()):
            yield index, timestamp

    @property
    def data(self):
        for index, timestamp in self._ordered_data:
            yield timestamp

    @property
    def lines(self):
        for index, timestamp in self._ordered_data:
            yield "%s %s" % (index, timestamp)

    def add(self, timestamp):
        index = 1 if not self._timestamps.keys() else max(self._timestamps.keys()) + 1
        self._timestamps[index] = float(timestamp)

    @property
    def last(self):
        """
        Finds the last timestamp for this file.

        """
        try:
            last = max(self._timestamps.keys())
        except ValueError as e:
            log.error("Tried to get last timestamp, but there are none.")
            raise e
        else:
            return self._timestamps[last]