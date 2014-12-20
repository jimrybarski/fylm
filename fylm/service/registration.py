from fylm.service.base import BaseSetService
import numpy as np
import nd2reader
import logging
from skimage.feature.phase_correlate import phase_correlate

log = logging.getLogger("fylm")


class RegistrationSet(BaseSetService):
    """
    Determines the rotational skew of an image.

    """
    def __init__(self, experiment):
        super(RegistrationSet, self).__init__()
        self._experiment = experiment
        self._name = "registration offsets"

    def save_action(self, registration_model):
        """
        Calculates the rotation offset for a single field of view and timepoint.

        :type registration_model:   fylm.model.registration.Registration()

        """
        log.debug("Creating registration file %s" % registration_model.filename)
        # This is a pretty naive loop - the same file will get opened 8-12 times
        # There are obvious ways to optimize this but that can be done later if it matters
        # It probably doesn't matter though and I like simple things
        nd2_filename = self._experiment.get_nd2_from_timepoint(registration_model.timepoint)
        nd2 = nd2reader.Nd2(nd2_filename)
        # gets the first out-of-focus image from the first timepoint in the stack
        base_image = nd2.get_image(0, registration_model.field_of_view, "", 0)
        for image_set in nd2.image_sets(field_of_view=registration_model.field_of_view,
                                        channels=[""],
                                        z_levels=[0]):
            image = [i for i in image_set][0]
            dx, dy = self._determine_registration_offset(base_image.data, image.data)
            registration_model.add(dx, dy)

    @staticmethod
    def _determine_registration_offset(base_image, uncorrected_image):
        """
        Finds the translational offset required to align this image with all others in the stack.
        Returns dx, dy adjustments in pixels *but does not change the image!*

        :param base_image:   a 2D numpy array that the other image should be aligned to
        :param uncorrected_image:   a 2D numpy array
        :returns:   float, float

        """
        # Get the dimensions of the images that we're aligning
        base_height, base_width = base_image.shape
        uncorrected_height, uncorrected_width = uncorrected_image.shape

        # We take the area that roughly corresponds to the catch channels. This has two benefits: one, it
        # speeds up the registration significantly (as it scales linearly with image size), and two, if
        # a large amount of debris/yeast/bacteria/whatever shows up in the central trench, the registration
        # algorithm goes bonkers if it's considering that portion of the image.
        # Thus we separately find the registration for the left side and right side, and average them.
        left_base_section = base_image[:, base_width * 0.1: base_width * 0.3]
        left_uncorrected = uncorrected_image[:, uncorrected_width * 0.1: uncorrected_width * 0.3]
        right_base_section = base_image[:, base_width * 0.7: base_width * 0.9]
        right_uncorrected = uncorrected_image[:, uncorrected_width * 0.7: uncorrected_width * 0.9]

        # phase_correlate returns y, x instead of x, y, which is not the convention in scikit-image, so we reverse them
        # it also returns some error bars and other stuff we don't need, so we just take the first two items
        left_dy, left_dx = phase_correlate(left_base_section, left_uncorrected, upsample_factor=20)[:2]
        right_dy, right_dx = phase_correlate(right_base_section, right_uncorrected, upsample_factor=20)[:2]
        #
        # # return the average of the left and right phase correlation corrections
        return (left_dx + right_dx) / 2.0, (left_dy + right_dy) / 2.0
        # dy, dx = phase_correlate(base_image[100:, :], uncorrected_image[100:, :], upsample_factor=20)[:2]
        # return dy, dx