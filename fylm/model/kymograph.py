from fylm.model.base import BaseTextFile, BaseSet
from fylm.service.errors import terminal_error
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


class Kymograph(BaseTextFile):
    def __init__(self):
        super(Kymograph, self).__init__()
        self._channel = None
        self._image_data = None
        self._image_slice = None

    def allocate_memory(self, frame_count, channel_width):
        """
        Creates an empty matrix - this is faster and easier than appending rows to an existing matrix every time more
        data comes in.

        :param frame_count:         the number of images in the image stack (corresponds to kymograph height)
        :param channel_width:       the size of the channel (corresponds to kymograph width)

        """
        self._image_data = np.zeros((frame_count, channel_width))

    def add_line(self, image_slice, time_index):
        """
        Takes an image slice, extracts several lines from it, averages them, and appends them to the growing kymograph.

        """
        width = image_slice.image_data.shape[1]
        self._image_data[time_index, 0: width + 1] = image_slice.average_around_center

    def set_location(self, location):
        self._image_slice =

    def load(self, data):
        pass

    @property
    def data(self):
        return None

    @property
    def lines(self):
        return None

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