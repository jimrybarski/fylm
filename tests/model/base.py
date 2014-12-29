import unittest
from fylm.model.base import BaseSet


class MockModel(object):
    model_id = 1

    def __init__(self):
        self.timepoint = None
        self.field_of_view = None
        self.base_path = None
        self.data = [i * MockModel.model_id for i in range(5)]
        MockModel.model_id += 1

    @property
    def filename(self):
        # This is just the default filename and it won't always be valid.
        return "tp%s-fov%s.txt" % (self.timepoint, self.field_of_view)


class MockExperiment(object):
    def __init__(self):
        self.data_dir = None
        self.fields_of_view = None
        self.timepoints = None
        self.base_path = None
        self.field_of_view_count = None


class BaseSetTests(unittest.TestCase):
    def setUp(self):
        experiment = MockExperiment()
        experiment.data_dir = "/home/lulz/"
        experiment.field_of_view_count = 4
        experiment.timepoints = [1, 2, 3, 4]
        self.bs = BaseSet(experiment, "/tmp/")
        self.bs._model = MockModel

    def test_get_current(self):
        self.bs._current_filenames = ["tp2-fov1.txt", "tp3-fov1.txt", "tp4-fov1.txt", "tp1-fov1.txt",
                                      "tp1-fov2.txt", "tp2-fov2.txt", "tp3-fov2.txt", "tp4-fov2.txt",
                                      "tp1-fov3.txt", "tp2-fov3.txt", "tp3-fov3.txt", "tp4-fov3.txt",
                                      "tp1-fov4.txt", "tp2-fov4.txt", "tp3-fov4.txt", "tp4-fov4.txt"]
        models = list(self.bs._get_current(1))
        self.assertEqual(len(models), 4)
        for n, model in enumerate(models):
            self.assertEqual(n + 1, model.timepoint)
        for model in models:
            self.assertEqual(model.field_of_view, 1)

    def test_get_data(self):
        # reset model id number
        MockModel.model_id = 1
        self.bs._current_filenames = ["tp2-fov0.txt", "tp3-fov0.txt", "tp4-fov0.txt", "tp1-fov0.txt"]
        expected = [0, 1, 2, 3, 4, 0, 2, 4, 6, 8, 0, 3, 6, 9, 12, 0, 4, 8, 12, 16]
        actual = list(self.bs.get_data(0, 1))
        self.assertListEqual(expected, actual)