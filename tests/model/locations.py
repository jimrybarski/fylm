from fylm.model.locations import Location
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