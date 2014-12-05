from nd2reader import Nd2


class ImageReader(object):
    """
    Gets ImageSet objects from the nd2reader library, sets metadata as appropriate, applies transformations to each image
    to correct for rotational and translational distortion, and yields the ImageSet. Seamlessly gets images from separate
    ND2 files for an unlimited number of timepoints, so the application will behave as if there was only a single acquisition.

    The registration and rotation can be optionally deactivated in case they misbehave, and the start point can also be set.

    """
    def __init__(self, field_of_view, register_images=True, rotate_images=True, start=1):
        self._field_of_view = field_of_view
        self._register_images = register_images
        self._rotate_images = rotate_images
        self._start = start

    def set_models(self, timestamp_set, rotation_set, registration_set):
        pass