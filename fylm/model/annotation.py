from fylm.model.base import BaseTextFile, BaseSet
from fylm.model.constants import Constants
from fylm.model.coordinates import Coordinates
from fylm.service.errors import terminal_error
import logging
import re

log = logging.getLogger("fylm")


class Annotation(object):
    """
    Models a single line added by a human (or machine-learning algorithm) that shows
    where a cell is at a given point in a kymograph.

    """
    index_regex = re.compile(r"""^(?P<index>\d+)\s.*""")
    coordinate_regex = re.compile(r"""(?P<x>\d+\.\d+),(?P<y>\d+\.\d+)""")

    def __init__(self):
        self._index = None
        self._coodinates = []

    def load_from_text(self, line):
        index = Annotation.index_regex.match(line)
        self._index = int(index.group("index"))
        raw_coodinates = Annotation.coordinate_regex.findall(line)
        # raw_coordinates is a list of tuples like ('1.123', '4.536')
        for pair in raw_coodinates:
            self._coodinates.append(Coordinates(x=float(pair[0]), y=float(pair[1])))

    def set_coordinates(self, coordinates):
        self._coodinates = coordinates

    @property
    def index(self):
        return self._index

    @index.setter
    def index(self, value):
        if self._index is not None:
            raise Exception("Attempted to set the kymograph annotation index when it already existed")
        self._index = int(value)

    @property
    def coordinates(self):
        return self._coodinates


class KymographAnnotationSet(BaseSet):
    """
    Models all kymograph images for a given experiment.

    """
    def __init__(self, experiment):
        super(KymographAnnotationSet, self).__init__(experiment, "annotation")
        self._model = KymographAnnotation
        self._regex = re.compile(r"""tp\d+-fov\d+-channel\d+.txt""")

    def get_annotation_group(self, channel_number):
        group = []
        for model in self.existing:
            if model.channel_number == channel_number:
                group.append(model)
        if not group:
            log.warn("Empty kymograph annotation group!")
        return group

    @property
    def _expected(self):
        """
        Yields instantiated children of BaseFile that represent the work we expect to have done.

        """
        assert self._model is not None
        for field_of_view in self._fields_of_view:
            for timepoint in self._timepoints:
                for channel_number in xrange(Constants.NUM_CATCH_CHANNELS):
                    model = self._model()
                    model.timepoint = timepoint
                    model.field_of_view = field_of_view
                    model.channel_number = channel_number
                    model.base_path = self.base_path
                    yield model


class KymographAnnotation(BaseTextFile):
    """
    Models all of the lines of an annotation of a kymograph.

    """
    def __init__(self):
        super(KymographAnnotation, self).__init__()
        self._channel_number = None
        self._image_data = None
        self._lines = {}
        self._state = None

    def load(self, data):
        try:
            self._state = data[0]
            if len(data) > 1:
                # We have some annotations already
                for line in data[1:]:
                    self._parse_line(line)
        except Exception:
            terminal_error("Could not parse line for Channel Locator because of: %s" % e)

    def _parse_line(self, line):
        try:
            annotation = Annotation()
            annotation.load_from_text(line)
        except:
            log.warn("Skipping invalid line: %s" % str(line))
        else:
            self._lines[annotation.index] = annotation.coordinates

    def add_line(self, coordinates):
        """
        Saves a line to the model when the user feels it's complete.

        :param coordinates:     the points of an annotation line
        :type coordinates:      list of fylm.model.coordinates.Coordinates()

        """
        if not self._lines:
            index = 0
        else:
            index = max(self._lines.keys()) + 1
        self._lines[index] = coordinates

    @property
    def data(self):
        return None

    @property
    def channel_number(self):
        return self._channel_number

    @channel_number.setter
    def channel_number(self, value):
        self._channel_number = int(value)

    @property
    def filename(self):
        return "tp%s-fov%s-channel%s.png" % (self.timepoint, self.field_of_view, self.channel_number)