from collections import defaultdict
from fylm.model.base import BaseTextFile, BaseSet
from fylm.model.annotation import KymographAnnotationSet
from fylm.service.annotation import KymographSetService
from fylm.model.kymograph import KymographSet
from fylm.service.kymograph import KymographSet as KymographService
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
        kymograph_set = KymographSet(experiment)
        KymographService(experiment).load_existing_models(kymograph_set)
        self._annotation_set_model = KymographAnnotationSet(experiment, ignore_kymographs=True)
        self._annotation_set_model.kymograph_set = kymograph_set
        KymographSetService(experiment).load_existing_models(self._annotation_set_model)

    def get_model(self, field_of_view, time_period, channel_number):
        for model in self.existing:
            if model.field_of_view == field_of_view and model.time_period == time_period and model.channel_number == channel_number:
                return model
        return False

    @property
    def fl_channel_count(self):
        """ Needed so we can write the correct number of NaNs in the output file even when we don't have a Fluorescence object to work with """
        counts = defaultdict(int)
        for model in self._existing:
            counts[model.field_of_view] += 1
        values, keys = list(counts.values()), list(counts.keys())
        return keys[values.index(max(values))]

    @property
    def _expected(self):
        """
        Yields instantiated children of BaseFile that represent the work we expect to have done.

        """
        assert self._model is not None
        # It's only possible to quantify fluorescence data if we know where the cell bounds are
        # In some cases, it might be possible to use image analysis to determine the cell borders without a list of cell bounds
        # However, the majority of cells have very low contrast and are difficult to precisely locate
        for annotation_model in self._annotation_set_model.existing:
            for time_period in self._time_periods:
                if annotation_model.last_state in ("Empty", "Active"):
                    continue
                model = self._model()
                model.time_period = time_period
                model.field_of_view = annotation_model.field_of_view
                model.base_path = self.base_path
                model.channel_number = annotation_model.channel_number
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
    def channel_names(self):
        names = set()
        for index, data in self._measurements.items():
            for name, channel_data in data.items():
                names.add(name)
        for name in names:
            yield name

    @property
    def filename(self):
        return "tp%s-fov%s-channel%s.txt" % (self.time_period, self.field_of_view, self.channel_number)

    @property
    def lines(self):
        for index, channel_name, mean, stddev, median, area, centroid in self._ordered_data:
            yield "%s %s %s %s %s %s %s" % (index, channel_name, mean, stddev, median, area, centroid)

    def _parse_line(self, line):
        match = self._line_regex.match(line)
        return int(match.group("index")), str(match.group("channel_name")), float(match.group("mean")), float(match.group("stddev")), float(match.group("median")), int(match.group("area")), int(match.group("centroid"))

    def load(self, data):
        for line in data:
            try:
                index, channel_name, mean, stddev, median, area, centroid = self._parse_line(line)
            except Exception as e:
                log.error("Could not parse line: '%s' because of: %s" % (line, e))
            else:
                self._measurements[index][channel_name] = mean, stddev, median, area, centroid

    @property
    def _ordered_data(self):
        for index, channel_data in sorted(self._measurements.items()):
            for channel_name, line_data in sorted(channel_data.items()):
                mean, stddev, median, area, centroid = line_data
                yield index, channel_name, mean, stddev, median, area, centroid

    def get_measurement(self, time_index, channel_name):
        # for tindex in map(int, (time_index, time_index - 1)):
        if time_index in self._measurements.keys():
            mean, stddev, median, area, centroid = self._measurements[time_index][channel_name]
            return mean, stddev, median, area, centroid
        raise ValueError("Could not get fluorescence measurement for given time index or the one before that.")

    @property
    def data(self):
        for index, channel_name, mean, stddev, median, area, centroid in self._ordered_data:
            yield channel_name, mean, stddev, median, area, centroid

    def add(self, time_index, channel_name, mean, stddev, median, area, centroid):
        log.debug("Fluorescence data: %s %s %s %s %s %s %s" % (time_index, channel_name, mean, stddev, median, area, centroid))
        self._measurements[time_index][channel_name] = float(mean), float(stddev), float(median), int(area), int(centroid)
