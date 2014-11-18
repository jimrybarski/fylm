from nd2reader import Nd2
from skimage import transform
from fylm.service.utilities import ImageUtilities, FileInteractor
from skimage.morphology import skeletonize
from fylm.model import Constants, Rotation
import numpy as np
import math
import logging

log = logging.getLogger("fylm")


class RotationCorrector(object):
    """
    Determines the rotational skew of an image.

    """
    def __init__(self, experiment):
        self._rotation_model = Rotation()
        self._rotation_model.base_path = experiment.experiment_path
        self._nd2_filename = experiment.nd2_filename
        self._field_of_view = experiment.field_of_view
        self._writer = FileInteractor(self._rotation_model)

    def save(self):
        if self._writer.file_already_exists:
            log.warn("Rotation file already exists, not overwriting.")
        else:
            nd2 = Nd2(self._nd2_filename)
            # gets the first in-focus image from the first timpoint in the stack
            image = nd2.get_image(0, self._field_of_view, "", "0")
            offset = self._determine_rotation_offset(image)
            self._rotation_model.offset = offset
            self._writer.write_text()

    @staticmethod
    def _determine_rotation_offset(image):
        """
        Finds rotational skew so that the sides of the central trench are (nearly) perfectly vertical.

        """
        segmentation = ImageUtilities.create_vertical_segments(image)
        # Draw a line that follows the center of the segments at each point, which should be roughly vertical
        # We should expect this to give us four approximately-vertical lines, possibly with many gaps in each line
        skeletons = skeletonize(segmentation)
        # Use the Hough transform to get the closest lines that approximate those four lines
        hough = transform.hough_line(skeletons, np.arange(-Constants.FIFTEEN_DEGREES_IN_RADIANS,
                                                          Constants.FIFTEEN_DEGREES_IN_RADIANS,
                                                          0.0001))
        # Create a list of the angles (in radians) of all of the lines the Hough transform produced, with 0.0 being
        # completely vertical
        # These angles correspond to the angles of the four sides of the channels, which we need to correct for
        angles = [angle for _, angle, dist in zip(*transform.hough_line_peaks(*hough))]
        if not angles:
            log.warn("Image skew could not be calculated. The image is probably invalid.")
            return 0.0
        else:
            # Get the average angle and convert it to degrees
            offset = sum(angles) / len(angles) * 180.0 / math.pi
            if offset > Constants.ACCEPTABLE_SKEW_THRESHOLD:
                log.warn("Image is heavily skewed. Check that the images are valid.")
            return offset