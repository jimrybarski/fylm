from fylm.model.base import BaseFile, BaseSet
from fylm.model.coordinates import Coordinates
from fylm.service.errors import terminal_error
import logging
import re

log = logging.getLogger("fylm")


class LocationSet(BaseSet):
    """
    Models all the translational offsets needed to align every image in a given field of view.

    """
    def __init__(self, experiment):
        super(LocationSet, self).__init__(experiment, "registration")
        self._model = Location


class Location(BaseFile):
    """
    Models the output file that contains the translational adjustments needed for all images in a stack.

    The first line of the file contains the locations of the top left and bottom right channel notches. All
    subsequent lines contain information about a particular channel, numbered 1-28.

    All coordinates are given as (x,y) tuples using the scikit-image convention (x increases from left to right,
    y increases from top to bottom).

    """
    def __init__(self):
        super(Location, self).__init__()
        self.timepoint = None
        self.field_of_view = None
        self._top_left = None
        self._bottom_right = None
        self._channels = {}
        self._header_regex = re.compile(r"""^(?P<top_left_x>-?\d+\.\d+)\s
                                             (?P<top_left_y>-?\d+\.\d+)\s
                                             (?P<bottom_right_x>\d+\.\d+)\s
                                             (?P<bottom_right_y>\d+\.\d+)""", re.VERBOSE)
        self._line_regex = re.compile(r"""^(?P<channel_number>\d+)\s
                                           (?P<notch_x>\d+\.\d+)\s
                                           (?P<notch_y>\d+\.\d+)\s
                                           (?P<tube_x>\d+\.\d+)\s
                                           (?P<tube_y>\d+\.\d+)""", re.VERBOSE)

    def load(self, data):
        try:
            header = next(data)
            self._top_left, self._bottom_right = self._parse_header(header)
            for line in data:
                channel_number, notch, tube = self._parse_line(line)
                self._channels[channel_number] = notch, tube
        except Exception as e:
            terminal_error("Could not parse line for Channel Locator because of: %s" % e)

    def _parse_header(self, line):
        match = self._header_regex.match(line)
        top_left = Coordinates(x=match.group("top_left_x"),
                               y=match.group("top_left_y"))
        bottom_right = Coordinates(x=match.group("bottom_right_x"),
                                   y=match.group("bottom_right_y"))
        return top_left, bottom_right

    def _parse_line(self, line):
        match = self._line_regex.match(line)
        channel_number = float(match.group("channel_number"))
        notch = Coordinates(x=match.group("notch_x"),
                            y=match.group("notch_y"))
        tube = Coordinates(x=match.group("tube_x"),
                           y=match.group("tube_y"))
        return channel_number, notch, tube

    @property
    def data(self):
        pass

    @property
    def lines(self):
        yield self._top_left

    def add(self, dx, dy):
        pass