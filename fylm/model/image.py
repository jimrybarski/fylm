from skimage import transform
from skimage import img_as_uint


class ImageSet(object):
    def __init__(self, nd2_image_set, rotation_offset, (dx, dy), timestamp):
        self._nd2_image_set = nd2_image_set
        self._rotation_offset = rotation_offset
        self._dx = dx
        self._dy = dy
        self._timestamp = timestamp

    @property
    def timestamp(self):
        return self._timestamp

    def __iter__(self):
        for i in self._nd2_image_set:
            image = Image(i, self._rotation_offset, self._dx, self._dy, self._timestamp)
            yield image.data


class Image(object):
    def __init__(self, raw_image_data, rotation_offset, dx, dy, timestamp):
        self._raw_image_data = raw_image_data
        self._rotation_offset = rotation_offset
        self._corrective_transform = transform.AffineTransform(translation=(-dx, -dy))
        self._timestamp = timestamp

    @property
    def data(self):
        """
        Returns rotation- and registration-corrected image.

        """
        image_data = transform.rotate(self._raw_image_data, self._rotation_offset)
        return img_as_uint(transform.warp(image_data, self._corrective_transform))