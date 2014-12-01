import unittest
from fylm.model.timestamp import Timestamps


class TimestampsTests(unittest.TestCase):
    def test_parse_line(self):
        t = Timestamps()
        index, timestamp = t._parse_line("238 4.5356246")
        self.assertEqual(index, 238)
        self.assertAlmostEqual(timestamp, 4.5356246)