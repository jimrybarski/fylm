from fylm.model.registration import RegistrationSet
from fylm.model.rotation import RotationSet
from fylm.model.timestamp import TimestampSet
from fylm.model.image import ImageSet as FylmImageSet, Image
from itertools import izip
import logging
from nd2reader import Nd2
from fylm.service.base import BaseSetService

log = logging.getLogger("fylm")


class ImageReader(object):
    """
    Gets ImageSet objects from the nd2reader library, sets metadata as appropriate, applies transformations to each image
    to correct for rotational and translational distortion, and yields the ImageSet. Seamlessly gets images from separate
    ND2 files for an unlimited number of timepoints, so the application will behave as if there was only a single acquisition.

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
        self._timepoint = None
        self._nd2 = None

        set_service = BaseSetService()
        for model_set in (self._registration_set, self._rotation_set, self._timestamp_set):
            set_service.load_existing_models(model_set)

    def __len__(self):
        return self.nd2.timepoint_count

    @property
    def timepoint(self):
        return self._timepoint

    @timepoint.setter
    def timepoint(self, value):
        self._timepoint = int(value)
        self._nd2 = None

    @property
    def nd2(self):
        if self._nd2 is None:
            filename = self._experiment.get_nd2_from_timepoint(self._timepoint)
            self._nd2 = Nd2(filename)
        return self._nd2

    def get_image(self, index, channel="", z_level=1):
        rotation_offset = self._rotation_set.existing[index].offset
        dx, dy = next(self._registration_set.get_data(self.field_of_view))
        timestamp = next(self._timestamp_set.get_data(self.field_of_view))
        raw_image = self.nd2.get_image(index, self.field_of_view, channel, z_level)
        return Image(raw_image.data, rotation_offset, dx, dy, timestamp)


    @property
    def field_of_view(self):
        return self._field_of_view

    @field_of_view.setter
    def field_of_view(self, value):
        self._field_of_view = int(value)

    def __iter__(self):
        """
        Provides image sets for a single timepoint.

        """
        # TODO: Implement get_data on the rotation set
        for ro in self._rotation_set.existing:
            if ro.field_of_view == self.field_of_view:
                rotation_offset = ro
                break
        registration_data = self._registration_set.get_data(self.field_of_view)
        timestamp_data = self._timestamp_set.get_data(self.field_of_view)
        for nd2_image_set, registration_offset, (time_index, timestamp) in izip(self.nd2.image_sets(self.field_of_view),
                                                                                registration_data,
                                                                                timestamp_data):
            yield FylmImageSet(nd2_image_set, rotation_offset.offset, registration_offset, time_index - 1, timestamp)