from collections import defaultdict
from fylm.model.base import BaseMovie, BaseSet
from fylm.model.constants import Constants
from fylm.model.location import LocationSet
from fylm.service.location import LocationSet as LocationService
import logging
import numpy as np
import re
from skimage.color import gray2rgb


log = logging.getLogger(__name__)


class MovieSet(BaseSet):
    """
    Models the collection of movies of catch channels.

    """
    def __init__(self, experiment):
        super(MovieSet, self).__init__(experiment, "movie")
        self._regex = re.compile(r"""tp\d+-fov\d+-channel\d+.avi""")
        self._location_set_model = LocationSet(experiment)
        LocationService(experiment).load_existing_models(self._location_set_model)
        self._model = Movie

    @property
    def _expected(self):
        assert self._model is not None
        for time_period in self._time_periods:
            for channel_number in xrange(Constants.NUM_CATCH_CHANNELS):
                for location_model in self._location_set_model.existing:
                    image_slice = location_model.get_image_slice(channel_number)
                    if location_model.get_channel_location(channel_number) and image_slice:
                        model = self._model()
                        model.base_path = self.base_path
                        model.image_slice = image_slice
                        model.time_period = time_period
                        model.field_of_view = location_model.field_of_view
                        model.catch_channel_number = channel_number
                        yield model


class Movie(BaseMovie):
    """
    Models a movie of a catch channel over a single time period. Has a "frame" property which dynamically builds the image.
    For each frame, the service updates the pictures as they're available. So if a fluorescence image isn't there,
    we use the already-existing image by default and thus can use any frequency of FL images.

    """
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
        """
        The height of each distinct area in the movie.

        :return:    int

        """
        return self.image_slice.height * 2

    @property
    def _slot_width(self):
        """
        The width of each distinct area in the movie.

        :return:    int

        """
        return self.image_slice.width

    def get_next_frame(self):
        """
        Combines the image data from each of the slots in a deterministic order and returns the image

        :return:    np.ndarray()

        """
        # Create a black square to use as a blank canvas to add image slices to
        image = np.zeros((self._frame_height, self._frame_width))
        # Go through each slot (one per channel/z-level combination) and assign image data to it
        for n, slot in enumerate(self._slots):
            top, bottom = self._get_slot_bounds(n)
            image[top:bottom, :] = slot[:, :]

        # Convert the grayscale image to RGB. It will still look gray, but we can now add color elements to it
        color_image = (gray2rgb(image) * 255).astype(np.uint8)
        return color_image

    def update_image(self, channel_name, z_level):
        """
        Gets image data for the given filter channel and z-level in the area of the catch channel. Then its updates
        the slot of the current frame to use that image data.

        :type channel_name: str
        :type z_level:  int

        """
        if channel_name not in self.__slots.keys() or z_level not in self.__slots[channel_name].keys():
            self._add_slot(channel_name, z_level)
        self.__slots[channel_name][z_level] = self.image_slice.image_data[:, :]

    @property
    def shape(self):
        """
        numpy-style tuple that describes the size of an image.

        :return:    (int, int)

        """
        return self._frame_height, self._frame_width

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
        """
        The height of the entire frame.

        :return:    int

        """
        slot_count = 0
        if self.__frame_height is None:
            for channel in self.__slots.values():
                slot_count += len(channel)
            self.__frame_height = slot_count * self._slot_height
        return self.__frame_height

    @property
    def _frame_width(self):
        """
        The width of the entire frame.

        :return:    int

        """
        return self._slot_width

    @property
    def _slots(self):
        """
        Yields slots in a deterministic order.

        :returns:    np.ndarray()

        """
        for index, channel in sorted(self._channel_order.items()):
            for slot_index, slot in sorted(self.__slots[channel].items()):
                yield slot