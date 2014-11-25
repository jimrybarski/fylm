from fylm.model.base import BaseFile, BaseSet
import logging
import re

log = logging.getLogger("fylm")


class TimestampSet(BaseSet):
    """
    Models all the timestamps for every set of images.

    """
    def __init__(self, experiment):
        super(TimestampSet, self).__init__(experiment, "timestamps")


class Timestamps(BaseFile):
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
                self._timestamps.float(timestamp)

    def _parse_line(self, line):
        match = self._line_regex.match(line)
        return match.group("index"), match.group("timestamp")

    @property
    def lines(self):
        for index, timestamp in enumerate(sorted(self._timestamps)):
            yield "%s %s" % (index, timestamp)

    def add(self, timestamp):
        self._timestamps.append(float(timestamp))

    @property
    def last(self):
        """
        Finds the last timestamp for this file.

        """
        return max(self._timestamps)