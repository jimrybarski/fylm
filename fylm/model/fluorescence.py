from fylm.model.base import BaseTextFile
import logging
import re

log = logging.getLogger("fylm")


class Fluorescence(BaseTextFile):
    def __init__(self):
        super(Fluorescence, self).__init__()
        self._measurements = {}
        self._line_regex = re.compile(r"""^(?P<index>\d+) (?P<mean>\d+\.\d+) (?P<stddev>\d+\.\d+) (?P<median>\d+\.\d+) (?P<area>\d+) (?P<centroid>\d+)""")
        self._channel = None

    @property
    def channel_number(self):
        return self._channel

    @channel_number.setter
    def channel_number(self, value):
        self._channel = int(value)

    @property
    def filename(self):
        return "tp%s-fov%s-channel%s.png" % (self.timepoint, self.field_of_view, self.channel_number)

    def lines(self):
        for index, mean, stddev, median, area, centroid in self._ordered_data:
            yield "%s %s %s %s %s %s" % (index, mean, stddev, median, area, centroid)

    def _parse_line(self, line):
        match = self._line_regex.match(line)
        return int(match.group("index")), float(match.group("mean")), float(match.group("stddev")), float(match.group("median")), int(match.group("area")), int(match.group("centroid"))

    def load(self, data):
        for line in data:
            try:
                index, mean, stddev, median, area, centroid = self._parse_line(line)
            except Exception as e:
                log.error("Could not parse line: '%s' because of: %s" % (line, e))
            else:
                self._measurements[index] = mean, stddev, median, area, centroid

    @property
    def _ordered_data(self):
        for index, (mean, stddev, median, area, centroid) in sorted(self._measurements.items()):
            yield index, mean, stddev, median, area, centroid

    @property
    def data(self):
        for index, mean, stddev, median, area, centroid in self._ordered_data:
            yield mean, stddev, median, area, centroid

    def add(self, mean, stddev, median, area, centroid):
        index = 1 if not self._measurements.keys() else max(self._measurements.keys()) + 1
        log.debug("Fluorescence data: %s %s %s %s %s" % (mean, stddev, median, area, centroid))
        self._measurements[index] = float(mean), float(stddev), float(median), int(area), int(centroid)