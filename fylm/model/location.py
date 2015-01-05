from fylm.model.base import BaseTextFile, BaseSet
from fylm.model.coordinates import Coordinates
from fylm.model.constants import Constants
from fylm.service.errors import terminal_error
import logging
import re

log = logging.getLogger("fylm")


class LocationSet(BaseSet):
    """
    Models all the translational offsets needed to align every image in a given field of view.

    """
    def __init__(self, experiment):
        super(LocationSet, self).__init__(experiment, "location")
        self._model = Location
        self._regex = re.compile(r"""fov\d+.txt""")

    @property
    def _expected(self):
        """
        Yields instantiated children of BaseFile that represent the work we expect to have done.

        """
        assert self._model is not None
        for field_of_view in self._fields_of_view:
            model = self._model()
            model.field_of_view = field_of_view
            model.base_path = self.base_path
            yield model


class Location(BaseTextFile):
    """
    Models the output file that contains the translational adjustments needed for all images in a stack.

    The first line of the file contains the locations of the top left and bottom right channel notches. All
    subsequent lines contain information about a particular channel, numbered 1-28.

    All coordinates are given as (x,y) tuples using the scikit-image convention (x increases from left to right,
    y increases from top to bottom).

    """
    def __init__(self):
        super(Location, self).__init__()
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
        self._skipped_regex = re.compile(r"""^(?P<channel_number>\d+) skipped""")

    def skip_remaining(self):
        for channel_number in range(Constants.NUM_CATCH_CHANNELS):
            if channel_number not in self._channels.keys():
                self.skip_channel(channel_number)

    @property
    def filename(self):
        # This is just the default filename and it won't always be valid.
        return "fov%s.txt" % self.field_of_view

    @property
    def top_left(self):
        return self._top_left

    @property
    def bottom_right(self):
        return self._bottom_right

    def load(self, data):
        try:
            header = data[0]
            self._top_left, self._bottom_right = self._parse_header(header)

            for line in data[1:]:
                channel_number, locations = self._parse_line(line)
                self._channels[channel_number] = locations
        except Exception as e:
            terminal_error("Could not parse line for Channel Locator because of: %s" % e)

    def _parse_header(self, line):
        match = self._header_regex.match(line)
        if not match:
            raise Exception("Invalid channel location line: %s" % line)
        top_left = Coordinates(x=match.group("top_left_x"),
                               y=match.group("top_left_y"))
        bottom_right = Coordinates(x=match.group("bottom_right_x"),
                                   y=match.group("bottom_right_y"))
        return top_left, bottom_right

    def _parse_line(self, line):
        match = self._line_regex.match(line)
        if match:
            channel_number = int(match.group("channel_number"))
            notch = Coordinates(x=match.group("notch_x"),
                                y=match.group("notch_y"))
            tube = Coordinates(x=match.group("tube_x"),
                               y=match.group("tube_y"))
            return channel_number, (notch, tube)
        match = self._skipped_regex.match(line)
        if match:
            return int(match.group("channel_number")), "skipped"
        raise Exception("Invalid channel location line: %s" % line)

    @property
    def _ordered_channels(self):
        for channel_number, locations in sorted(self._channels.items()):
            yield channel_number, locations

    @property
    def data(self):
        yield self._top_left, self._bottom_right
        for channel_number, locations in self._ordered_channels:
            if not locations == "skipped":
                yield channel_number, locations

    def get_channel_data(self, channel_number):
        return self._channels[channel_number]

    @property
    def lines(self):
        if len(self._channels) != Constants.NUM_CATCH_CHANNELS:
            log.warn("Invalid number of channels: %s" % len(self._channels))
        data = iter(self.data)
        top_left, bottom_right = next(data)
        yield "%s %s %s %s" % (top_left.x, top_left.y, bottom_right.x, bottom_right.y)
        for channel_number, locations in self._ordered_channels:
            try:
                notch, tube = locations
                yield "%s %s %s %s %s" % (channel_number, notch.x, notch.y, tube.x, tube.y)
            except ValueError:
                # the human declared this channel invalid
                yield "%s skipped" % channel_number

    def set_header(self, top_left_x, top_left_y, bottom_right_x, bottom_right_y):
        """
        Saves the *approximate* coordinates of the notches of the top left and bottom right catch channels.

        """
        self._top_left = Coordinates(x=top_left_x, y=top_left_y)
        self._bottom_right = Coordinates(x=bottom_right_x, y=bottom_right_y)

    def set_channel_location(self, channel_number, notch_x, notch_y, tube_x, tube_y):
        """
        Saves the coordinates of a single catch channel.

        :param channel_number: identifier of the channel, an integer from 1 to 28
        :param notch_x: number of pixels from the left where the notch of the catch channel is located
        :param notch_y: number of pixels from the top where the notch of the catch channel is located
        :param tube_x: number of pixels from the left where the end of the catch channel is located
        :param tube_y: number of pixels from the top where the end of the catch channel is located

        """
        self._channels[channel_number] = (Coordinates(x=notch_x, y=notch_y),
                                          Coordinates(x=tube_x, y=tube_y))

    def get_channel_location(self, channel_number):
        try:
            return self._channels[channel_number]
        except KeyError:
            return None

    def skip_channel(self, channel_number):
        self._channels[channel_number] = "skipped"