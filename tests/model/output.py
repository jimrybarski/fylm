import unittest
from fylm.model.output import Output


class MockAnnotation(object):
    def __init__(self, cell_lengths):
        self._cell_lengths = cell_lengths

    def get_cell_lengths(self, time_period):
        return self._cell_lengths[time_period]


class MockTimestampSet(object):
    def __init__(self, data):
        self._data = data

    def get_data(self, fov, time_period):
        return self._data[time_period]


class OutputTests(unittest.TestCase):
    def setUp(self):
        self.output = Output()

    @unittest.skip("Test out of date")
    def test_lines_no_fluorescence(self):
        self.output.time_periods = [1, 2]
        timestamps = {1: {0: 2.135135, 1: 8.12515, 2: 14.9966, 3: 21.071698},
                      2: {0: 27.23589, 1: 33.46240, 2: 39.909011, 3: 45.41}}
        self.output.timestamp_set = MockTimestampSet(timestamps)
        cell_lengths = {1: {0: None, 1: 15, 2: 19, 3: 27},
                        2: {0: None, 1: None, 2: 99, 3: None}}
        self.output.annotation = MockAnnotation(cell_lengths)
        lines = list(self.output.lines)
        expected = ["2.135135\tNaN",
                    "8.12515\t15",
                    "14.9966\t19",
                    "21.071698\t27",
                    "27.23589\tNaN",
                    "33.4624\tNaN",
                    "39.909011\t99",
                    "45.41\tNaN"]
        self.assertListEqual(lines, expected)