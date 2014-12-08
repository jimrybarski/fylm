from fylm.model.locations import Location
from fylm.model.coordinates import Coordinates
import unittest


class LocationModelTests(unittest.TestCase):
    def setUp(self):
        self.location = Location()

    def test_header_regex(self):
        line = "3.44 12.22 600.66 800.88"
        top_left, bottom_right = self.location._parse_header(line)
        self.assertTupleEqual((top_left.x, top_left.y), (3.44, 12.22))
        self.assertTupleEqual((bottom_right.x, bottom_right.y), (600.66, 800.88))

    def test_line_regex(self):
        line = "15 3.44 12.22 600.66 800.88"
        channel_number, notch, tube = self.location._parse_line(line)
        self.assertEqual(channel_number, 15)
        self.assertTupleEqual((notch.x, notch.y), (3.44, 12.22))
        self.assertTupleEqual((tube.x, tube.y), (600.66, 800.88))

    def test_lines(self):
        self.location._top_left = Coordinates(1.222, 2.222)
        self.location._bottom_right = Coordinates(4.444, 8.888)
        self.location._channels = {3: (Coordinates(4.666, 7.888), Coordinates(9.999, 0.000)),
                                   1: (Coordinates(14.666, 17.888), Coordinates(19.999, 10.000)),
                                   2: (Coordinates(24.666, 27.888), Coordinates(29.999, 20.000))}
        lines = [line for line in self.location.lines]
        self.assertEqual(lines[0], "1.222 2.222 4.444 8.888")