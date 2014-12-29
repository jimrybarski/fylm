from collections import defaultdict
from fylm.model.base import BaseTextFile, BaseSet
from fylm.model.constants import Constants
from fylm.model.coordinates import Coordinates
from fylm.service.errors import terminal_error
from skimage.draw import line
import logging
import re

log = logging.getLogger("fylm")


class AnnotationLine(object):
    """
    Models a single line added by a human (or machine-learning algorithm) that shows
    where a cell is at a given point in a kymograph.

    """
    index_regex = re.compile(r"""^(?P<timepoint>\d+) (?P<index>\d+) .*""")
    coordinate_regex = re.compile(r"""(?P<x>\d+\.\d+),(?P<y>\d+\.\d+)""")

    def __init__(self):
        self._index = None
        self._timepoint = None
        self._coodinates = []

    def load_from_text(self, line):
        index = AnnotationLine.index_regex.match(line)
        self.index = index.group("index")
        self.timepoint = index.group("timepoint")
        raw_coodinates = AnnotationLine.coordinate_regex.findall(line)
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
    def timepoint(self):
        return self._timepoint

    @timepoint.setter
    def timepoint(self, value):
        self._timepoint = int(value)

    @property
    def coordinates(self):
        return self._coodinates


class ChannelAnnotationGroup(BaseTextFile):
    """
    Models all of the lines of an annotation of any number of kymographs for a single field of view and channel.
    That is, all the kymographs over several timepoints.

    """
    def __init__(self):
        super(ChannelAnnotationGroup, self).__init__()
        self._channel_number = None
        self._lines = defaultdict(dict)
        self._last_state = "active"
        self._last_state_timepoint = 1  # the last timepoint to be saved by a human
        self.kymographs = None

    @property
    def is_finished(self):
        return self._last_state in ("dies", "finished")

    def points(self, timepoint):
        for index, annotation in sorted(self._lines[timepoint].items()):
            for n, from_point in enumerate(annotation.coordinates[:-1]):
                to_point = annotation.coordinates[n + 1]
                y_list, x_list = line(int(from_point.y), int(from_point.x), int(to_point.y), int(to_point.x))
                yield y_list, x_list

#     def add_images(self, kymographs):
#         for kymograph in kymographs:
#             self._images[kymograph.timepoint] = kymograph.data
#
#
#     @property
#     def current_timepoint(self):
#         return self._current_timepoint
#
#     @property
#     def work_complete(self):
#         return self._last_state_timepoint == max(self._images.keys())

    def get_image(self, timepoint):
        for kymo in self.kymographs:
            if kymo.timepoint == timepoint:
                return kymo.data
        raise ValueError("The kymograph didn't have any image data!")

    @property
    def state(self):
        return "%s %s" % (self._last_state, self._last_state_timepoint)

    @state.setter
    def state(self, value):
        assert value[0] in ("active", "dies", "finished")
        assert isinstance(value[1], int)
        self._last_state = value[0]
        self._last_state_timepoint = value[1]

    @property
    def lines(self):
        yield self.state
        for index, annotation in sorted(self._lines.items()):
            yield "%s " % index + " ".join(["%s,%s" % (coord.x, coord.y) for coord in annotation.coordinates])

    def load(self, data):
        try:
            self._last_state, self._last_state_timepoint = self._parse_state(data[0])
            if len(data) > 1:
                # We have some annotations already
                for line in data[1:]:
                    self._parse_line(line)
        except Exception as e:
            terminal_error("Could not parse line for Channel Locator because of: %s" % e)

    def _parse_state(self, line):
        try:
            state, state_timepoint = line.strip().split(" ")
        except Exception:
            log.exception("Could not parse state of kymograph annotation")
        else:
            return state, int(state_timepoint)

    def _parse_line(self, line):
        try:
            annotation = AnnotationLine()
            annotation.load_from_text(line)
        except:
            log.warn("Skipping invalid line: %s" % str(line))
        else:
            self._lines[annotation.timepoint][annotation.index] = annotation

#     def add_line(self, annotation_line):
#         """
#         Saves a line to the model when the user feels it's complete.
#         Even though it is not currently implemented, we have indices on the data so that in the future we'll have the option
#         of deleting lines based on which one the user has clicked on.
#
#         :param annotation_line:     the points of an annotation line
#         :type annotation_line:      list of fylm.model.annotation.AnnotationLine()
#
#         """
#         if not self._annotations[self._current_timepoint]:
#             # first time to add data for this timepoint
#             index = 0
#         else:
#             # we already have data for this timepoint, so use the next available index
#             index = max(self._annotations[self._current_timepoint].keys()) + 1
#         self._annotations[self._current_timepoint][index] = annotation_line
#
#     @property
#     def data(self):
#         return None
#
    @property
    def channel_number(self):
        return self._channel_number

    @channel_number.setter
    def channel_number(self, value):
        self._channel_number = int(value)

    @property
    def filename(self):
        return "fov%s-channel%s.txt" % (self.field_of_view, self.channel_number)


class KymographAnnotationSet(BaseSet):
    """
    Models all kymograph images for a given experiment.

    """
    def __init__(self, experiment):
        super(KymographAnnotationSet, self).__init__(experiment, "annotation")
        self._model = ChannelAnnotationGroup
        self.kymograph_set = None
        self._unfinished = None
        self._current_timepoint = 1
        self._current_model_pointer = 0
        self._max_timepoint = experiment.timepoint_count

    def decrement_channel(self):
        self._current_model_pointer -= 1
        if self._current_model_pointer == -1:
            self._current_model_pointer = len(self._unfinished) - 1

    def increment_channel(self):
        self._current_model_pointer += 1
        if self._current_model_pointer == len(self._unfinished):
            self._current_model_pointer = 0

    def increment_timepoint(self):
        """
        Actually goes to an earlier timepoint so that the key direction corresponds
        with the direction of the kymograph in time.

        """
        self._current_timepoint -= 1
        if self._current_timepoint == 0:
            self._current_timepoint = self.max_timepoint

    def decrement_timepoint(self):
        """
        Actually goes to a later timepoint so that the key direction corresponds
        with the direction of the kymograph in time.

        """
        self._current_timepoint += 1
        if self._current_timepoint > self.max_timepoint:
            self._current_timepoint = 1

    @property
    def max_timepoint(self):
        return self._max_timepoint

    @property
    def current_model(self):
        return self.unfinished[self._current_model_pointer]

    @property
    def _expected(self):
        """
        Yields instantiated children of BaseFile that represent the work we expect to have done.

        """
        assert self._model is not None
        for channel_number in xrange(Constants.NUM_CATCH_CHANNELS):
            for field_of_view in self._fields_of_view:
                kymographs = self.kymograph_set.get_kymographs(field_of_view, channel_number)
                if kymographs:
                    model = self._model()
                    model.kymographs = kymographs
                    model.channel_number = channel_number
                    model.field_of_view = field_of_view
                    model.base_path = self.base_path
                    yield model

    @property
    def unfinished(self):
        """
        We define this in addition to self.remaining. This is because annotations can be
        incomplete - a file can be saved even though more work can be done.
        A user can declare a channel to be finished, which will prevent it from showing
        up here.

        """
        if self._unfinished is None:
            self._unfinished = []
            for model in self.remaining:
                self._unfinished.append(model)
            for model in self.existing:
                if not model.is_finished:
                    self._unfinished.append(model)
        return self._unfinished

    @property
    def work_remains(self):
        return len(self.unfinished) > 0

    @property
    def current_timepoint(self):
        return self._current_timepoint