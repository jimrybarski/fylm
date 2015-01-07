import numpy as np
import unittest
from fylm.model.annotation import AnnotationLine, ChannelAnnotationGroup


class AnnotationTests(unittest.TestCase):
    def setUp(self):
        self.annotation = AnnotationLine()

    def test_parse(self):
        text_line = "2 4 12.345,13.222 6.757,4.646"
        self.annotation.load_from_text(text_line)
        self.assertEqual(self.annotation.time_period, 2)
        self.assertEqual(self.annotation.index, 4)
        self.assertEqual(self.annotation.coordinates[0].x, 12.345)
        self.assertEqual(self.annotation.coordinates[0].y, 13.222)
        self.assertEqual(self.annotation.coordinates[1].x, 6.757)
        self.assertEqual(self.annotation.coordinates[1].y, 4.646)

    def test_get_next_state_index(self):
        ChannelAnnotationGroup.states = ["empty", "dies", "ejected", "survives"]
        self.assertEqual(ChannelAnnotationGroup._get_next_state_index("empty"), 1)
        self.assertEqual(ChannelAnnotationGroup._get_next_state_index("dies"), 2)
        self.assertEqual(ChannelAnnotationGroup._get_next_state_index("ejected"), 3)
        self.assertEqual(ChannelAnnotationGroup._get_next_state_index("survives"), 0)


class ChannelAnnotationGroupTests(unittest.TestCase):
    def setUp(self):
        self.cag = ChannelAnnotationGroup()

    def mock_cell_bounds(self, *args):
        return {0: None, 1: None, 2: (15, 66), 3: (17, 34), 4: None}

    def mock_skeleton(self, *args):
        return np.array([[0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                         [0, 1, 0, 0, 0, 0, 0, 1, 0, 1],
                         [0, 1, 0, 0, 0, 0, 0, 0, 1, 0],
                         [0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
                         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                         [0, 0, 0, 1, 0, 1, 0, 0, 0, 0],
                         [0, 0, 0, 0, 1, 1, 0, 0, 0, 0],
                         [0, 1, 0, 1, 0, 1, 0, 0, 0, 0]])

    def test_get_cell_lengths(self):
        self.cag.get_cell_bounds = self.mock_cell_bounds
        expected_dict = {0: None, 1: None, 2: 51, 3: 17, 4: None}
        self.assertDictEqual(expected_dict, self.cag.get_cell_lengths(1))

    def test_get_cell_bounds(self):
        self.cag._skeleton = self.mock_skeleton
        bounds = self.cag.get_cell_bounds(1)
        expected = {0: None, 1: (1, 7), 2: (1, 8), 3: None, 4: None, 5: (3, 5), 6: (4, 5), 7: (1, 3)}
        self.assertDictEqual(bounds, expected)

    def test_cell_lengths_and_bounds(self):
        self.cag._skeleton = self.mock_skeleton
        expected = {0: None, 1: 6, 2: 7, 3: None, 4: None, 5: 2, 6: 1, 7: 2}
        self.assertDictEqual(expected, self.cag.get_cell_lengths(1))