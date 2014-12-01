import unittest
from fylm.model.timestamp import Timestamps


class TimestampsTests(unittest.TestCase):
    def setUp(self):
        self.t = Timestamps()

    def test_parse_line(self):
        index, timestamp = self.t._parse_line("238 4.5356246")
        self.assertEqual(index, 238)
        self.assertAlmostEqual(timestamp, 4.5356246)

    def test_parse_line_invalid(self):
        with self.assertRaises(AttributeError):
            index, timestamp = self.t._parse_line("238")

    def test_parse_line_empty(self):
        with self.assertRaises(AttributeError):
            index, timestamp = self.t._parse_line("")