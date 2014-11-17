from fylm.model.rotation import Rotation
import unittest


class MockExperiment(object):
    def __init__(self):
        self.experiment_path = None


class RotationTests(unittest.TestCase):
    def setUp(self):
        experiment = MockExperiment()
        experiment.experiment_path = "/home/lulz/141117"
        self.rotation = Rotation()
        self.rotation.base_path = experiment.experiment_path

    def test_path(self):
        self.assertEqual(self.rotation.path, "/home/lulz/141117/rotation.txt")

    def test_line(self):
        self.rotation._offset = 5.6363
        self.assertEqual("\n".join(self.rotation.lines), "5.6363")

    def test_set_offset(self):
        self.rotation.offset = "5.6363"
        self.assertAlmostEqual(self.rotation.offset, 5.6363)