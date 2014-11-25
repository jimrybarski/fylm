import unittest
from fylm.model.timestamp import Timestamps


class TimestampsTests(unittest.TestCase):
    def test_regex_good(self):
        t = Timestamps()
        t.