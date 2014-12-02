import unittest
from fylm.model.registration import Registration


class RegistrationTests(unittest.TestCase):
    def setUp(self):
        self.r = Registration()

    def test_parse_line(self):
        index, dx, dy = self.r._parse_line("15 -1.33453 246.23235263")
        self.assertEqual(index, 15)
        self.assertAlmostEqual(dx, -1.33453)
        self.assertAlmostEqual(dy, 246.23235263)

    def test_parse_line_invalid(self):
        with self.assertRaises(AttributeError):
            index, dx, dy = self.r._parse_line("238")

    def test_parse_line_empty(self):
        with self.assertRaises(AttributeError):
            index, dx, dy = self.r._parse_line("")

    def test_load(self):
        data = ["1 -2.222 0.002", "2 4.444 -3.222", "3 8.888 6.666"]
        self.r.load(data)
        expected = {1: (-2.222, 0.002), 2: (4.444, -3.222), 3: (8.888, 6.666)}
        self.assertDictEqual(self.r._offsets, expected)

    def test_load_one_bad(self):
        data = ["1 -2.222 0.002", "2 4.444", "3 8.888 6.666"]
        self.r.load(data)
        expected = {1: (-2.222, 0.002), 3: (8.888, 6.666)}
        self.assertDictEqual(self.r._offsets, expected)

    def test_lines(self):
        self.r._offsets = {1: (-2.222, 0.002), 2: (4.444, -3.222), 3: (8.888, 6.666)}
        lines = sorted(list(self.r.lines))
        self.assertListEqual(["1 -2.222 0.002", "2 4.444 -3.222", "3 8.888 6.666"], lines)

    def test_add(self):
        self.r.add(-2.222, 0.002)
        self.r.add(4.444, -3.222)
        self.r.add(8.888, 6.666)
        expected = {1: (-2.222, 0.002), 2: (4.444, -3.222), 3: (8.888, 6.666)}
        self.assertDictEqual(self.r._offsets, expected)
        self.r.add(12.222, 12.222)
        expected = {1: (-2.222, 0.002), 2: (4.444, -3.222), 3: (8.888, 6.666), 4: (12.222, 12.222)}
        self.assertDictEqual(self.r._offsets, expected)