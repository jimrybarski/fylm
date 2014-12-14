import unittest


class RegistrationTests(unittest.TestCase):
    def test_has_phase_correlate(self):
        """
        Determines if the correct version of scikit-image was installed.
        This is tricky since we're currently using a custom branch outside of the
        official repo.

        """
        has_phase_correlate = False
        try:
            has_phase_correlate = __import__("skimage.feature.phase_correlate",
                                             fromlist=["skimage.feature.phase_correlate"])
        except ImportError:
            pass
        self.assertTrue(has_phase_correlate)