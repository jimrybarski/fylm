from fylm.model.base import BaseImage, BaseSet
from fylm.model.image_slice import ImageSlice
import logging
import numpy as np
import re

log = logging.getLogger("fylm")


class KymographSet(BaseSet):
    """
    Models all kymograph images for a given experiment.

    """
    def __init__(self, experiment):
        super(KymographSet, self).__init__(experiment, "kymograph")
        self._model = Kymograph
        self._regex = re.compile(r"""tp\d+-fov\d+-channel\d+.txt""")


class Kymograph(BaseImage):
    def __init__(self):
        super(Kymograph, self).__init__()
        self._channel = None
        self._image_data = None
        self._image_slice = None

    def allocate_memory(self, frame_count):
        """
        Creates an empty matrix - this is faster and easier than appending rows to an existing matrix every time more
        data comes in.

        :param frame_count:         the number of images in the image stack (corresponds to kymograph height)

        """
        self._image_data = np.zeros((frame_count, self.width))

    @property
    def width(self):
        """
        The width of the kymograph image in pixels. Should be the length of the channel from the notch to the end of the catch channel.

        """
        return self._image_slice.width

    def add_line(self, time_index):
        """
        Takes an image slice, extracts several lines from it, averages them, and appends them to the growing kymograph.

        """
        width = self._image_slice.image_data.shape[1]
        self._image_data[time_index, 0: width + 1] = self._image_slice.average_around_center

    def set_location(self, notch, tube):
        """
        Takes the human-provided locations of the notch and tube of a catch channel and instantiates an ImageSlice object,
        which will allow us to capture images of the channel in each frame of the image data.

        :param notch:   fylm.model.coordinates.Coordinates()
        :param tube:    fylm.model.coordinates.Coordinates()

        """
        width = tube.x - notch.x
        height = notch.y - tube.y
        fliplr = width < 0
        top_left_y = tube.y
        if not fliplr:
            top_left_x = notch.x
        else:
            top_left_x = tube.x
        self._image_slice = ImageSlice(top_left_x, top_left_y, width, height, fliplr)

    @property
    def data(self):
        return self._image_data

    @property
    def channel(self):
        return self._channel

    @channel.setter
    def channel(self, value):
        self._channel = int(value)

    @property
    def filename(self):
        # This is just the default filename and it won't always be valid.
        return "tp%s-fov%s-channel%s.txt" % (self.timepoint, self.field_of_view, self.channel)