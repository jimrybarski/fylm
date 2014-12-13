from fylm.model.coordinates import Coordinates
import numpy as np


class ImageSlice(object):
    """
    A subset of an image. Helps figure out where coordinates in the subimage would be in the parent image.

    """
    def __init__(self, x, y, width, height, fliplr=False):
        """
        :param width:       how wide the slice should be, in pixels
        :type width:        int
        :param height:      how high the slice should be, in pixels
        :type height:       int
        :param x:           the x-coordinate of the TOP LEFT CORNER of the desired image slice
        :type x:            int
        :param y:           the y-coordinate of the TOP LEFT CORNER of the desired image slice
        :type y:            int
        :param fliplr:      whether the image should be inverted on the horizontal axis
        :type fliplr:       bool

        """
        self._top_left = Coordinates(x=x, y=y)
        self._width = width
        self._height = height
        self._image_data = None
        self._fliplr = fliplr
        self._y_margin = 0

    def set_image(self, image_data, y_margin=0):
        """
        Slices out image data from the parent image.

        :param image_data:       2D numpy array
        :param y_margin:        number of pixels above and below the channel to add to the slice
        :type y_margin:         int

        """
        self._y_margin = y_margin
        parent_height = image_data.shape[0]
        parent_width = image_data.shape[1]

        y_slice_coords = max(self._top_left.y - y_margin, 0), min(self._top_left.y + self._height + y_margin, parent_height)
        x_slice_coords = max(self._top_left.x, 0), min(self._top_left.x + self._width, parent_width)
        image_data_slice = image_data[y_slice_coords[0]:y_slice_coords[1], min(x_slice_coords):max(x_slice_coords)]
        if self._fliplr:
            self._image_data = np.fliplr(image_data_slice)
        else:
            self._image_data = image_data_slice

    def get_parent_coordinates(self, local_coordinates):
        """
        Takes an x,y coordinate in the image slice and determines where that coodinate is in the parent image.

        """
        return Coordinates(x=local_coordinates.x + self._top_left.x,
                           y=local_coordinates.y + self._top_left.y - self._y_margin)

    def get_child_coordinates(self, parent_coordinates):
        """
        Take coordinates from a superset of this image and figure out where they belong on the image slice image.

        """
        return Coordinates(x=parent_coordinates.x - self._top_left.x,
                           y=parent_coordinates.y - self._top_left.y + self._y_margin)

    @property
    def average_around_center(self):
        """
        Returns the average of the center row and the two rows above and below it

        """
        top_row, bottom_row = self._central_rows
        middle_section = self._image_data[top_row:bottom_row, :]
        return np.mean(middle_section, axis=0)

    @property
    def _central_rows(self):
        """
        Returns a tuple representing the boundaries of the rows surrounding the center of the image.

        """
        row_count = self._image_data.shape[0]
        odd_adjustment = row_count % 2  # we only want integers so we make odd numbers even temporarily
        center_row = (row_count - odd_adjustment) / 2
        return center_row, center_row + 1

    @property
    def image_data(self):
        return self._image_data

    @property
    def top_left_coordinates(self):
        return self._top_left

    @property
    def fliplr(self):
        return self._fliplr

    @property
    def width(self):
        return abs(self._width)