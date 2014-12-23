import unittest
from fylm.model.annotation import AnnotationLine, KymographAnnotation
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


class KymographAnnotationTests(unittest.TestCase):

    def setUp(self):
        self.ka = KymographAnnotation()

    def test_lines(self):
        a0 = AnnotationLine()
        a0.set_coordinates([Coordinates(x=1.2, y=3.4), Coordinates(x=1.4, y=3.5), Coordinates(6.7, 5.5)])
        a1 = AnnotationLine()
        a1.set_coordinates([Coordinates(x=1.0, y=9.9), Coordinates(x=1.2, y=7.5), Coordinates(1.3, 4.5)])
        self.ka._annotations = {0: a0,
                                1: a1}
        lines = list(self.ka.lines)
        self.assertEqual(lines[0], "active 1")
        self.assertEqual(lines[1], "0 1.2,3.4 1.4,3.5 6.7,5.5")
        self.assertEqual(lines[2], "1 1.0,9.9 1.2,7.5 1.3,4.5")

    def test_load(self):
        data = ["dying 2", "1 0 1.2,3.4 1.4,3.5 6.7,5.5", "1 1 1.0,9.9 1.2,7.5 1.3,4.5"]
        self.ka.load(data)
        # self.assertEqual(self.ka.state, "dying 2")
        self.assertEqual(self.ka._last_state, "dying")
        self.assertEqual(self.ka._last_state_timepoint, 2)
        self.assertListEqual(self.ka._annotations[1][0], [Coordinates(1.2, 3.4),
                                                          Coordinates(1.4, 3.5),
                                                          Coordinates(6.7, 5.5)])

    def test_load_different_timepoint(self):
        data = ["active 4", "2 0 1.2,3.4 1.4,3.5 6.7,5.5", "2 1 1.0,9.9 1.2,7.5 1.3,4.5"]
        self.ka.load(data)
        self.assertEqual(self.ka._last_state, "active")
        self.assertEqual(self.ka._last_state_timepoint, 4)
        self.assertListEqual(self.ka._annotations[2][0], [Coordinates(1.2, 3.4),
                                                          Coordinates(1.4, 3.5),
                                                          Coordinates(6.7, 5.5)])
        self.assertListEqual(self.ka._annotations[2][1], [Coordinates(1.0, 9.9),
                                                          Coordinates(1.2, 7.5),
                                                          Coordinates(1.3, 4.5)])