from skimage import transform
from skimage import img_as_uint


class ImageSet(object):
    def __init__(self, nd2_image_set, rotation_offset, (dx, dy), time_index, timestamp):
        self._nd2_image_set = nd2_image_set
        self._rotation_offset = rotation_offset
        self._dx = dx
        self._dy = dy
        self._time_index = time_index
        self._timestamp = timestamp

    def get_image(self, channel="", z_level=1):
        for image in self._nd2_image_set:
            if image.channel == channel and image.z_level == z_level:
                return self._correct_image(image)

    def _correct_image(self, image):
        """
        Registers and rotates the image and returns the raw image data.

        """
        return Image(image.data, self._rotation_offset, self._dx, self._dy, self._timestamp).data

    @property
    def timestamp(self):
        return self._timestamp

    @property
    def time_index(self):
        return self._time_index

    def __iter__(self):
        for image in self._nd2_image_set:
            yield self._correct_image(image)


class Image(object):
    def __init__(self, raw_image_data, rotation_offset, dx, dy, timestamp):
        self._raw_image_data = raw_image_data
        self._rotation_offset = rotation_offset
        self._corrective_transform = transform.AffineTransform(translation=(dx, dy))
        self._timestamp = timestamp

    @property
    def data(self):
        """
        Returns rotation- and registration-corrected image.

        """
        image_data = transform.rotate(self._raw_image_data, self._rotation_offset)
        image = transform.warp(image_data, self._corrective_transform)
        return image