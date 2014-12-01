from fylm.model.base import BaseFile, BaseSet
import logging
import re

log = logging.getLogger("fylm")


class TimestampSet(BaseSet):
    """
    Models all the timestamps for every set of images.

    """
    def __init__(self, experiment):
        super(TimestampSet, self).__init__(experiment)


class Timestamps(BaseFile):
    def __init__(self):
        super(Timestamps, self).__init__("timestamps")
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
    def lines(self):
        for index, timestamp in sorted(self._timestamps.items()):
            yield "%s %s" % (index, timestamp)

    def add(self, timestamp):
        index = max(self._timestamps.keys())
        self._timestamps[index] = float(timestamp)

    @property
    def last(self):
        """
        Finds the last timestamp for this file.

        """
        return max(self._timestamps)