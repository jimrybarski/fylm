from collections import defaultdict
from fylm.model.base import BaseTextFile, BaseSet
from fylm.model.constants import Constants
from fylm.model.coordinates import Coordinates
from fylm.service.errors import terminal_error
from skimage.draw import line
import numpy as np
import logging
import re

log = logging.getLogger("fylm")


class AnnotationLine(object):
    """
    Models a single line added by a human (or machine-learning algorithm) that shows
    where a cell is at a given point in a kymograph.

    """
    index_regex = re.compile(r"""^(?P<time_period>\d+) (?P<index>\d+) .*""")
    coordinate_regex = re.compile(r"""(?P<x>\d+\.\d+),(?P<y>\d+\.\d+)""")

    def __init__(self):
        self._index = None
        self._time_period = None
        self._coodinates = []

    def load_from_text(self, line):
        index = AnnotationLine.index_regex.match(line)
        self.index = index.group("index")
        self.time_period = index.group("time_period")
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
    def time_period(self):
        return self._time_period

    @time_period.setter
    def time_period(self, value):
        self._time_period = int(value)

    @property
    def coordinates(self):
        return self._coodinates


class ChannelAnnotationGroup(BaseTextFile):
    """
    Models all of the lines of an annotation of any number of kymographs for a single field of view and channel.
    That is, all the kymographs over several time_periods.

    """
    states = ["Active", "Empty", "Dies", "Ejected", "Survives"]

    def __init__(self):
        super(ChannelAnnotationGroup, self).__init__()
        self._channel_number = None
        self._lines = defaultdict(dict)
        self._last_state = "Active"
        self._last_state_time_period = 1  # the last time_period to be saved by a human
        self.kymographs = None

    def add_line(self, annotation_line):
        if not self._lines or not self._lines[annotation_line.time_period]:
            index = 0
        else:
            index = max(self._lines[annotation_line.time_period].keys()) + 1
        self._lines[annotation_line.time_period][index] = annotation_line

    def delete_last_line(self, time_period):
        try:
            index = max(self._lines[time_period].keys())
            del(self._lines[time_period][index])
        except (KeyError, ValueError):
            pass

    @property
    def is_finished(self):
        return self._last_state in ("Empty", "Dies", "Ejected", "Survives")

    def _skeleton(self, time_period):
        kymograph = self.get_image(time_period)
        data = np.zeros(kymograph.shape)
        for y_list, x_list in self.points(time_period):
            data[y_list, x_list] = 1
        return data

    def get_cell_bounds(self, time_period):
        """
        Gets the two leftmost white pixels in the skeleton image, which ostensibly are the old pole and new pole of the
        elder sibling cell.

        """
        bounds = {}
        skeleton = self._skeleton(time_period)
        for n, row in enumerate(skeleton):
            # get a list of the indices of the non-zero values in this row
            pole_locations = np.nonzero(row)[0]
            if len(pole_locations) > 1:
                bounds[n] = pole_locations[0], pole_locations[1]
            else:
                bounds[n] = None
        return bounds

    def get_cell_lengths(self, time_period):
        """
        If there are two pole locations (an old pole and a new pole) calculate the distance between them. This gives us
        the cell length at each time index.

        :type time_period:    int
        :rtype:             dict

        """
        lengths = {}
        for time_index, bounds in self.get_cell_bounds(time_period).items():
            if bounds:
                lengths[time_index] = bounds[1] - bounds[0]
            else:
                lengths[time_index] = None
        return lengths

    def points(self, time_period):
        """
        Annotation lines are stored as sets of end points. We take each pair of end points, draw a line between them,
        and record the coordinates of the individual pixels that are in that line. This saves space and lets us add
        and delete lines at will, even if overlapping. We can use these pixels to draw the lines on the screen when the
        user is making annotations, and later we take the two leftmost pixels for each row and consider those to be the
        locations of the cell poles of the elder sibling cell.

        """
        for index, annotation in sorted(self._lines[time_period].items()):
            for n, from_point in enumerate(annotation.coordinates[:-1]):
                to_point = annotation.coordinates[n + 1]
                y_list, x_list = line(int(from_point.y), int(from_point.x), int(to_point.y), int(to_point.x))
                yield y_list, x_list

    def get_image(self, time_period):
        for kymo in self.kymographs:
            if kymo.time_period == time_period:
                return kymo.data
        raise ValueError("The kymograph didn't have any image data!")

    @property
    def state(self):
        return "%s %s" % (self._last_state, self._last_state_time_period)

    @state.setter
    def state(self, value):
        assert value[0] in ChannelAnnotationGroup.states
        assert isinstance(value[1], int)
        self._last_state = value[0]
        self._last_state_time_period = value[1]

    def change_state(self, time_period):
        """
        Cycles through possible states, one at a time. This lets the user press "tab" until they find the state they want.

        """
        self.state = ChannelAnnotationGroup.states[self._get_next_state_index(self._last_state)], time_period

    @staticmethod
    def _get_next_state_index(state):
        current_state_index = ChannelAnnotationGroup.states.index(state)
        return (current_state_index + 1) % len(ChannelAnnotationGroup.states)

    @property
    def lines(self):
        yield self.state
        for time_period in sorted(self._lines.keys()):
            for index, annotation in sorted(self._lines[time_period].items()):
                yield "%s %s " % (time_period, index) + " ".join(["%s,%s" % (coord.x, coord.y) for coord in annotation.coordinates])

    def load(self, data):
        try:
            self._last_state, self._last_state_time_period = self._parse_state(data[0])
            if len(data) > 1:
                # We have some annotations already
                for line in data[1:]:
                    self._parse_line(line)
        except Exception as e:
            terminal_error("Could not parse line for Channel Locator because of: %s" % e)

    def _parse_state(self, line):
        try:
            state, state_time_period = line.strip().split(" ")
        except Exception:
            log.exception("Could not parse state of kymograph annotation")
        else:
            return state, int(state_time_period)

    def _parse_line(self, line):
        try:
            annotation = AnnotationLine()
            annotation.load_from_text(line)
        except Exception as e:
            log.warn(str(e))
            log.warn("Skipping invalid line: %s" % str(line))
        else:
            self._lines[annotation.time_period][annotation.index] = annotation

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
        self._current_time_period = 1
        self._current_model_pointer = 0
        self._max_time_period = experiment.time_period_count
        self._regex = re.compile(r"""fov\d+-channel\d+.txt""")

    def get_model(self, field_of_view, channel_number):
        for model in self._existing:
            if model.field_of_view == field_of_view and model.channel_number == channel_number:
                return model
        raise ValueError("That annotation doesn't exist!")

    def decrement_channel(self):
        self._current_model_pointer -= 1
        if self._current_model_pointer == -1:
            self._current_model_pointer = len(self._unfinished) - 1

    def increment_channel(self):
        self._current_model_pointer += 1
        if self._current_model_pointer == len(self._unfinished):
            self._current_model_pointer = 0

    def increment_time_period(self):
        """
        Actually goes to an earlier time_period so that the key direction corresponds
        with the direction of the kymograph in time.

        """
        self._current_time_period -= 1
        if self._current_time_period == 0:
            self._current_time_period = self.max_time_period

    def decrement_time_period(self):
        """
        Actually goes to a later time_period so that the key direction corresponds
        with the direction of the kymograph in time.

        """
        self._current_time_period += 1
        if self._current_time_period > self.max_time_period:
            self._current_time_period = 1

    @property
    def max_time_period(self):
        return self._max_time_period

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
    def current_time_period(self):
        return self._current_time_period