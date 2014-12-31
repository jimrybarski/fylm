import numpy as np
from skimage import draw


class Movie(object):
    """
    has a "frame" property which dynamically builds the image
    for each frame, the service updates the pictures as they're available
    so if a fluorescence image isn't there, we use the already-existing image by default and thus can use any frequency of FL images
    slots are labelled by channel and zoom level, they need a deterministic order
    write orange triangles, deal with overflow

    """
    # We create a single triangle once to save time
    triangle_width = 11  # must be odd
    triangle_height = 12
    triangle_x_coords = np.array([0, triangle_width, (triangle_width - 1) / 2])
    triangle_y_coords = np.array([0, 0, triangle_height])
    rr, cc = draw.polygon(triangle_y_coords, triangle_x_coords)
    triangle = np.zeros((triangle_height, triangle_width, 3), dtype=np.uint16)
    triangle[rr, cc] = 45536, 23000, 0

    def get_triangle(self, pointing, trim=0):
        assert pointing in ("up", "down")
        if pointing == "down":
            triangle = Movie.triangle
        if pointing == "up":
            triangle = np.flipud(Movie.triangle)
        x_start, x_stop = self._get_triangle_boundaries(trim)
        return np.copy(triangle[:, x_start:x_stop, :])

    @staticmethod
    def _get_triangle_boundaries(trim):
        """
        Finds the boundaries needed if the triangle goes partially out of the frame. The point will always be within the limits
        of the frame as its location is determined by the kymograph annotation, which guarantees bounds won't be violated.

        :param trim:    the number of pixels to trim from the edge. Positive numbers trim the left, negative trim the right
        :type trim:     int
        :return:        (int, int)

        """
        x_start = 0 if trim < 0 else trim
        x_stop = Movie.triangle_width if trim >= 0 else Movie.triangle_width + trim
        return x_start, x_stop