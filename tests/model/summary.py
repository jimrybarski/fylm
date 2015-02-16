import unittest
from fylm.model.summary import FinalState


class FinalStateTests(unittest.TestCase):
    def setUp(self):
        self.final = FinalState()

    def test_lines(self):
        self.final._data = {1: {0: "Survives", 1: "Dies", 2: "Dies", 3: "Empty"},
                            2: {0: "Ejected", 1: "Ejected", 2: "Survives", 3: "Dies"}}
        lines = [line for line in self.final.lines]
        self.assertEqual(lines[0], "2 1 1 0")
        self.assertEqual(lines[1], "-1 -1 2 1")