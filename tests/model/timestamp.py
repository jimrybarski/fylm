import unittest
from fylm.model.timestamp import Timestamps
from fylm.model.timestamp import TimestampSet


class MockExperiment(object):
    def __init__(self):
        self.data_dir = "/tmp/"
        self.fields_of_view = [1, 2]
        self.timepoints = [1, 2]
        self.base_path = None
        self.field_of_view_count = 2


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

    def test_load(self):
        data = ["1 2.222", "2 4.444", "3 8.888"]
        self.t.load(data)
        expected = {1: 2.222, 2: 4.444, 3: 8.888}
        self.assertDictEqual(self.t._timestamps, expected)

    def test_load_one_bad(self):
        data = ["1 2.222", "2 4.444", "Horrendous Surprise!", "3 8.888"]
        self.t.load(data)
        expected = {1: 2.222, 2: 4.444, 3: 8.888}
        self.assertDictEqual(self.t._timestamps, expected)

    def test_load_one_invalid_type(self):
        data = ["1 2.222", "2 Fourpointfourseconds", "3 8.888"]
        self.t.load(data)
        expected = {1: 2.222, 3: 8.888}
        self.assertDictEqual(self.t._timestamps, expected)

    def test_lines(self):
        self.t._timestamps = {3: 8.888, 1: 2.222, 2: 4.444}
        lines = sorted(list(self.t.lines))
        self.assertListEqual(["1 2.222", "2 4.444", "3 8.888"], lines)

    def test_add(self):
        self.t.add("2.222")
        self.t.add("4.444")
        self.t.add("8.888")
        expected = {1: 2.222, 2: 4.444, 3: 8.888}
        self.assertDictEqual(self.t._timestamps, expected)
        self.t.add("12.222")
        expected = {1: 2.222, 2: 4.444, 3: 8.888, 4: 12.222}
        self.assertDictEqual(self.t._timestamps, expected)

    def test_last(self):
        self.t._timestamps = {3: 8.888, 1: 2.222, 2: 4.444}
        self.assertEqual(self.t.last, (3, 8.888))

    def test_last_none(self):
        self.t._timestamps = {}
        with self.assertRaises(ValueError):
            last = self.t.last