from collections import defaultdict
from fylm.model.base import BaseTextFile, BaseSet
from fylm.model.constants import Constants
from fylm.model.location import LocationSet
from fylm.service.location import LocationSet as LocationService
import logging
import re

log = logging.getLogger(__name__)


class FluorescenceSet(BaseSet):
    """
    Models all the fluorescence intensity values for each channel.

    """
    def __init__(self, experiment):
        super(FluorescenceSet, self).__init__(experiment, "fluorescence")
        self._model = Fluorescence
        self._regex = re.compile(r"""tp\d+-fov\d+-channel\d+.txt""")
        self._location_set_model = LocationSet(experiment)
        LocationService(experiment).load_existing_models(self._location_set_model)

    @property
    def _expected(self):
        """
        Yields instantiated children of BaseFile that represent the work we expect to have done.

        """
        assert self._model is not None
        for field_of_view in self._fields_of_view:
            for time_period in self._time_periods:
                for channel_number in xrange(Constants.NUM_CATCH_CHANNELS):
                    for location_model in self._location_set_model.existing:
                        if not location_model.get_channel_location(channel_number):
                            continue
                        model = self._model()
                        model.time_period = time_period
                        model.field_of_view = field_of_view
                        model.base_path = self.base_path
                        model.channel_number = channel_number
                        yield model


class Fluorescence(BaseTextFile):
    def __init__(self):
        super(Fluorescence, self).__init__()
        self._measurements = defaultdict(dict)
        self._line_regex = re.compile(r"""^(?P<index>\d+) (?P<channel_name>[\w\-]+) (?P<mean>\d+\.\d+) (?P<stddev>\d+\.\d+) (?P<median>\d+\.\d+) (?P<area>\d+) (?P<centroid>\d+)""")
        self._channel = None

    @property
    def channel_number(self):
        return self._channel

    @channel_number.setter
    def channel_number(self, value):
        self._channel = int(value)

    @property
    def filename(self):
        return "tp%s-fov%s-channel%s.txt" % (self.time_period, self.field_of_view, self.channel_number)

    @property
    def lines(self):
        for index, channel_name, mean, stddev, median, area, centroid in self._ordered_data:
            yield "%s %s %s %s %s %s %s" % (index, channel_name, mean, stddev, median, area, centroid)

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
        for index, channel_data in sorted(self._measurements.items()):
            for channel_name, (mean, stddev, median, area, centroid) in sorted(channel_data.items()):
                yield index, channel_name, mean, stddev, median, area, centroid

    @property
    def data(self):
        for index, channel_name, mean, stddev, median, area, centroid in self._ordered_data:
            yield mean, stddev, median, area, centroid

    def add(self, time_index, channel_name, mean, stddev, median, area, centroid):
        log.debug("Fluorescence data: %s %s %s %s %s %s %s" % (time_index, channel_name, mean, stddev, median, area, centroid))
        self._measurements[time_index][channel_name] = float(mean), float(stddev), float(median), int(area), int(centroid)