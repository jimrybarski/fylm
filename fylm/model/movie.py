from fylm.model.constants import Constants
from fylm.model.base import BaseMovie, BaseSet
from fylm.model.location import LocationSet
from fylm.service.location import LocationSet as LocationService
from fylm.model.image_slice import ImageSlice
from collections import defaultdict
import numpy as np
from skimage import draw
from skimage.color import gray2rgb
import logging
import re

log = logging.getLogger(__name__)


class MovieSet(BaseSet):
    def __init__(self, experiment):
        super(MovieSet, self).__init__(experiment, "movie")
        self._regex = re.compile(r"""tp\d+-fov\d+-channel\d+.avi""")
        self._location_set_model = LocationSet(experiment)
        LocationService(experiment).load_existing_models(self._location_set_model)
        self._model = Movie

    @property
    def _expected(self):
        assert self._model is not None
        for location_model in self._location_set_model.existing:
            for channel_number in xrange(Constants.NUM_CATCH_CHANNELS):
                if location_model.get_channel_location(channel_number):
                    model = self._model()
                    model.catch_channel_number = channel_number
                    model.time_period = location_model.time_period
                    model.field_of_view = location_model.field_of_view
                    model.base_path = self.base_path
                    image_slice = self._get_image_slice(location_model, channel_number)
                    if image_slice:
                        log.debug("Added image slice")
                        model.image_slice = image_slice
                    log.debug("Need to make a movie: %s %s %s" % (model.time_period,
                                                                  model.field_of_view,
                                                                  model.catch_channel_number))
                    yield model

    def _get_image_slice(self, location_model, channel_number):
        try:
            notch, tube = location_model.get_channel_location(channel_number)
        except ValueError:
            return None
        if notch.x < tube.x:
            x = notch.x
            fliplr = False
        else:
            x = tube.x
            fliplr = True
        y = tube.y
        width = int(abs(notch.x - tube.x))
        height = int(notch.y - tube.y)
        return ImageSlice(x, y, width, height, fliplr=fliplr)


class Movie(BaseMovie):
    """
    has a "frame" property which dynamically builds the image
    for each frame, the service updates the pictures as they're available
    so if a fluorescence image isn't there, we use the already-existing image by default and thus can use any frequency of FL images

    """
    # We create a single triangle once to save time
    triangle_width = 11  # must be odd
    triangle_height = 12
    triangle_x_coords = np.array([0, triangle_width, (triangle_width - 1) / 2])
    triangle_y_coords = np.array([0, 0, triangle_height])
    rr, cc = draw.polygon(triangle_y_coords, triangle_x_coords)
    triangle = np.zeros((triangle_height, triangle_width, 3), dtype=np.uint16)
    triangle[rr, cc] = 177, 89, 0

    def __init__(self):
        super(Movie, self).__init__()
        self.catch_channel_number = None
        self._channel_order = {0: ""}
        self.__frame_height = None
        self.image_slice = None
        self.__slots = defaultdict(dict)
        self._triangles = {}

    @property
    def filename(self):
        return "tp%s-fov%s-channel%s.avi" % (self.time_period, self.field_of_view, self.catch_channel_number)

    @property
    def _slot_height(self):
        return self.image_slice.height * 2

    @property
    def _slot_width(self):
        return self.image_slice.width

    def get_next_frame(self):
        """
        Combines the image data from each of the slots in a deterministic order, adds arrows if needed,
        and returns the image

        :return:    np.ndarray()

        """
        image = np.zeros((self._frame_height, self._frame_width))
        log.debug("Movie frame HxW: %sx%s" % (self._frame_height, self._frame_width))
        for n, slot in enumerate(self._slots):
            top, bottom = self._get_slot_bounds(n)
            log.debug("Top, Bottom: %s, %s" % (top, bottom))
            image[top:bottom, :] = slot[:, :]

        # Convert the grayscale image to RGB. It will still look gray, but we can now add color elements to it
        color_image = (gray2rgb(image) * 255).astype(np.uint8)

        # TODO: We shouldn't do this every frame. WTF is it doing here?
        # for x, triangle in self._triangles.items():
        #     if x >= 5 and x <= self._slot_width - 5:
        #         xx, yy, zz = np.where(triangle != (0, 0, 0))
        #         for x_coord, y_coord in zip(xx, yy):
        #             color_image[0:12, x-5:x+6][x_coord, y_coord] = 177, 89, 0
        # self._triangles = {}
        return color_image

    def update_image(self, channel_name, z_level, image_data):
        if channel_name not in self.__slots.keys() or z_level not in self.__slots[channel_name].keys():
            self._add_slot(channel_name, z_level)
        self.__slots[channel_name][z_level] = image_data[:, :]

    @property
    def shape(self):
        return self._frame_height, self._frame_width

    def add_triangle(self, x):
        trim = self._calculate_trim(x, self._frame_width)
        self._triangles[x] = self._get_triangle("down", trim)

    def _add_slot(self, channel_name, z_level):
        """
        Allocates space for a slot in the movie frame.

        :type channel_name:     str
        :type z_level:          int

        """
        # Images are placed from top to bottom in order of channel, in the order that the channels are added
        # Here we add the channel to the list of channels to yield if we don't have it yet.
        # The brightfield channel always comes first, however. It's called "" (empty string)
        if channel_name not in self._channel_order.values():
            index = max(self._channel_order.keys()) + 1
            self._channel_order[index] = channel_name
        # Now allocate some space for the image. We start with zeros (i.e. a black image) in case this particular channel
        # doesn't have image data for the first frame. This occurs for fluorescent channels sometimes since we only take
        # those images every four minutes instead of every two, in order to minimize the amount of blue light that the cells
        # are exposed to (there's evidence that it's phototoxic).
        self.__slots[channel_name][z_level] = np.zeros((self._slot_height, self._slot_width, 3))

    def _get_slot_bounds(self, position):
        """
        Determines the row where the slot starts in the overall image, and the row where it ends.

        :param position:    the order of the slot
        :type position:     int
        :return:            (int, int)

        """
        start = self._slot_height * position
        return start, start + self._slot_height

    @property
    def _frame_height(self):
        slot_count = 0
        if self.__frame_height is None:
            for channel in self.__slots.values():
                slot_count += len(channel)
            self.__frame_height = slot_count * self._slot_height
        return self.__frame_height

    @property
    def _frame_width(self):
        return self._slot_width

    @property
    def _slots(self):
        """
        Yields slots in a deterministic order.

        :return:    np.ndarray()

        """
        for index, channel in sorted(self._channel_order.items()):
            for slot_index, slot in sorted(self.__slots[channel].items()):
                yield slot

    def _calculate_trim(self, x, width):
        if x < 5:
            return 5 - x
        if x > (width - 5):
            return x - width
        return 0

    def _get_triangle(self, pointing, trim=0):
        assert pointing in ("up", "down")
        if pointing == "down":
            triangle = Movie.triangle
        if pointing == "up":
            triangle = np.flipud(Movie.triangle)
        x_start, x_stop = self._get_triangle_boundaries(trim)
        return np.copy(triangle[:, x_start:x_stop, :])

    @staticmethod
    def _get_triangle_boundaries(trim):
        """
        Finds the boundaries needed if the triangle goes partially out of the frame. The point will always be within the limits
        of the frame as its location is determined by the kymograph annotation, which guarantees bounds won't be violated.

        :param trim:    the number of pixels to trim from the edge. Positive numbers trim the left, negative trim the right
        :type trim:     int
        :return:        (int, int)

        """
        x_start = 0 if trim < 0 else trim
        x_stop = Movie.triangle_width if trim >= 0 else Movie.triangle_width + trim
        return x_start, x_stop