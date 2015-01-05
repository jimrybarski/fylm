import unittest
from fylm.model.annotation import AnnotationLine, ChannelAnnotationGroup
from fylm.model.coordinates import Coordinates


class AnnotationTests(unittest.TestCase):
    def setUp(self):
        self.annotation = AnnotationLine()

    def test_parse(self):
        text_line = "2 4 12.345,13.222 6.757,4.646"
        self.annotation.load_from_text(text_line)
        self.assertEqual(self.annotation.timepoint, 2)
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