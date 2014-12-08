from fylm.model.locations import Location
from fylm.model.coordinates import Coordinates
import unittest


class LocationModelTests(unittest.TestCase):
    def setUp(self):
        self.location = Location()

    def test_load(self):
        data = iter(["3.444 7.888 9.888 24.222", "1 skipped", "2 4.444 4.444 8.888 12.222", "3 skipped", "4 skipped"])
        self.location.load(data)
        expected = {1: "skipped",
                    2: (Coordinates(4.444, 4.444), Coordinates(8.888, 12.222)),
                    3: "skipped",
                    4: "skipped"}
        for i in (1, 3, 4):
            self.assertEqual(expected[i], self.location._channels[i])
        self.assertEqual(expected[2][0].x, 4.444)
        self.assertEqual(expected[2][0].y, 4.444)
        self.assertEqual(expected[2][1].x, 8.888)
        self.assertEqual(expected[2][1].y, 12.222)
        self.assertEqual(self.location._top_left.x, 3.444)
        self.assertEqual(self.location._top_left.y, 7.888)
        self.assertEqual(self.location._bottom_right.x, 9.888)
        self.assertEqual(self.location._bottom_right.y, 24.222)

    def test_header_regex(self):
        line = "3.44 12.22 600.66 800.88"
        top_left, bottom_right = self.location._parse_header(line)
        self.assertTupleEqual((top_left.x, top_left.y), (3.44, 12.22))
        self.assertTupleEqual((bottom_right.x, bottom_right.y), (600.66, 800.88))

    def test_line_regex(self):
        line = "15 3.44 12.22 600.66 800.88"
        channel_number, locations = self.location._parse_line(line)
        notch, tube = locations
        self.assertEqual(channel_number, 15)
        self.assertTupleEqual((notch.x, notch.y), (3.44, 12.22))
        self.assertTupleEqual((tube.x, tube.y), (600.66, 800.88))

    def test_skipped_regex(self):
        line = "17 skipped"
        channel_number, skipped = self.location._parse_line(line)
        self.assertEqual(channel_number, 17)
        self.assertEqual(skipped, "skipped")

    def test_lines(self):
        self.location._top_left = Coordinates(1.222, 2.222)
        self.location._bottom_right = Coordinates(4.444, 8.888)
        self.location._channels = {3: "skipped",
                                   4: (Coordinates(4.666, 7.888), Coordinates(9.999, 0.000)),
                                   1: (Coordinates(14.666, 17.888), Coordinates(19.999, 10.000)),
                                   2: (Coordinates(24.666, 27.888), Coordinates(29.999, 20.000))}
        lines = [line for line in self.location.lines]
        self.assertEqual(lines[0], "1.222 2.222 4.444 8.888")
        self.assertEqual(lines[1], "1 14.666 17.888 19.999 10.0")
        self.assertEqual(lines[2], "2 24.666 27.888 29.999 20.0")
        self.assertEqual(lines[3], "3 skipped")
        self.assertEqual(lines[4], "4 4.666 7.888 9.999 0.0")

    def test_data(self):
        self.location._channels = {3: "skipped",
                                   4: (Coordinates(4.666, 7.888), Coordinates(9.999, 0.000)),
                                   1: (Coordinates(14.666, 17.888), Coordinates(19.999, 10.000)),
                                   2: (Coordinates(24.666, 27.888), Coordinates(29.999, 20.000))}
        data = iter(self.location.data)
        header = next(data)
        location_data = [(channel_number, location[0].x, location[0].y, location[1].x, location[1].y) for channel_number, location in data]
        self.assertTupleEqual(location_data[0], (1, 14.666, 17.888, 19.999, 10.000))
        self.assertTupleEqual(location_data[1], (2, 24.666, 27.888, 29.999, 20.000))
        self.assertTupleEqual(location_data[2], (4, 4.666, 7.888, 9.999, 0.000))