from skimage import transform


class ImageSet(object):
    def __init__(self, nd2_image_set, rotation_offset, (dx, dy)):
        self._nd2_image_set = nd2_image_set
        self._rotation_offset = rotation_offset
        self._corrective_transform = transform.AffineTransform(translation=(-dx, -dy))

    # def __iter__(self):
    #     for image in self._nd2_image_set:
    #         image_data = transform.rotate(image.data, self._rotation_offset)
    #         image_data = transform.warp(image_data, self._corrective_transform)
    #         yield image_data