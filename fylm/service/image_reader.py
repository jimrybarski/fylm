from fylm.model.registration import RegistrationSet
from fylm.model.rotation import RotationSet
from fylm.model.timestamp import TimestampSet
from fylm.model.image import ImageSet as FylmImageSet, Image
from itertools import izip
import logging
from nd2reader import Nd2
from fylm.service.base import BaseSetService

log = logging.getLogger(__name__)


class ImageReader(object):
    """
    Gets ImageSet objects from the nd2reader library, sets metadata as appropriate, applies transformations to each image
    to correct for rotational and translational distortion, and yields the ImageSet. Seamlessly gets images from separate
    ND2 files for an unlimited number of time_periods, so the application will behave as if there was only a single acquisition.

    The registration and rotation can be optionally deactivated in case they misbehave, and the start point can also be set.

    """
    def __init__(self, experiment, register_images=True, rotate_images=True):
        self._experiment = experiment
        self._field_of_view = None
        self._register_images = register_images
        self._rotate_images = rotate_images
        self._registration_set = RegistrationSet(experiment)
        self._rotation_set = RotationSet(experiment)
        self._timestamp_set = TimestampSet(experiment)
        self._time_period = None
        self._nd2 = None

        set_service = BaseSetService()
        for model_set in (self._registration_set, self._rotation_set, self._timestamp_set):
            set_service.load_existing_models(model_set)

    def __len__(self):
        return self.nd2.time_index_count

    @property
    def time_period(self):
        return self._time_period

    @time_period.setter
    def time_period(self, value):
        self._time_period = int(value)
        self._nd2 = None

    @property
    def nd2(self):
        if self._nd2 is None:
            filename = self._experiment.get_nd2_from_time_period(self._time_period)
            self._nd2 = Nd2(filename)
        return self._nd2

    def get_image(self, index, channel="", z_level=1):
        rotation_offset = self._rotation_set.existing[index].offset
        dx, dy = next(self._registration_set.get_data(self.field_of_view, self.time_period))
        timestamp = next(self._timestamp_set.get_data(self.field_of_view, self.time_period))
        raw_image = self.nd2.get_image(index, self.field_of_view, channel, z_level)
        return Image(raw_image.data, rotation_offset, dx, dy, timestamp)

    @property
    def channel_names(self):
        return self._nd2.channel_names

    @property
    def field_of_view(self):
        return self._field_of_view

    @field_of_view.setter
    def field_of_view(self, value):
        self._field_of_view = int(value)

    def __iter__(self):
        """
        Provides image sets for a single time_period.

        """
        rotation_offset = self._rotation_set.get_data(self.field_of_view)
        registration_data = self._registration_set.get_data(self.field_of_view, self.time_period)
        timestamp_data = self._timestamp_set.get_data(self.field_of_view, self.time_period)
        for nd2_image_set, registration_offset, (time_index, timestamp) in izip(self.nd2.image_sets(self.field_of_view),
                                                                                registration_data,
                                                                                timestamp_data):
            yield FylmImageSet(nd2_image_set, rotation_offset, registration_offset, time_index - 1, timestamp)