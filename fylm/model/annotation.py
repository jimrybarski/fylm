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
        self._image_data = {}
        self._annotations = {}  # index == timepoint
        self._state = "active"
        self._state_timepoint = 0

    @property
    def state(self):
        return "%s %s" % (self._state, self._state_timepoint)

    @state.setter
    def state(self, value):
        assert value[0] in ("active", "dies")
        assert isinstance(value[1], int)
        self._state = value[0]
        self._state_timepoint = value[1]

    @property
    def lines(self):
        yield self.state
        for index, annotation in sorted(self._annotations.items()):
            for coodinates in annotation.coordinates:
                yield "%s " % index + " ".join(["%s,%s" % (coord.x, coord.y) for coord in coordinates])

    def load(self, data):
        try:
            self._state = self._parse_state(data[0])
            if len(data) > 1:
                # We have some annotations already
                for line in data[1:]:
                    self._parse_line(line)
        except Exception as e:
            terminal_error("Could not parse line for Channel Locator because of: %s" % e)

    def _parse_state(self, line):
        try:
            state, state_timepoint = line.strip().split(" ")


    def _parse_line(self, line):
        try:
            annotation = Annotation()
            annotation.load_from_text(line)
        except:
            log.warn("Skipping invalid line: %s" % str(line))
        else:
            self._annotations[annotation.index] = annotation.coordinates

    def add_line(self, coordinates):
        """
        Saves a line to the model when the user feels it's complete.

        :param coordinates:     the points of an annotation line
        :type coordinates:      list of fylm.model.coordinates.Coordinates()

        """
        if not self._annotations:
            index = 0
        else:
            index = max(self._annotations.keys()) + 1
        self._annotations[index] = coordinates

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
        return "fov%s-channel%s.png" % (self.field_of_view, self.channel_number)