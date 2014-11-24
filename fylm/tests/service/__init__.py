import unittest
from fylm.service.experiment import Experiment as ExperimentService
from fylm.model.experiment import Experiment as ExperimentModel
import logging

log = logging.getLogger("fylm")
log.disabled = True


class MockOS(object):
    def __init__(self):
        self._listdir = None

    def listdir(self, directory):
        for filename in self._listdir:
            yield filename


class ExperimentServiceTests(unittest.TestCase):
    def setUp(self):
        self.service = ExperimentService()
        self.service._os = MockOS()

    def test_find_nd2s_none_found(self):
        self.service._os._listdir = ["lulz.txt", "nothing.csv"]
        model = ExperimentModel()
        model.base_dir = "/home/lulz"
        model.start_date = "140909"
        self.service.find_nd2s(model)
        self.assertListEqual([], [nd2 for nd2 in model.nd2s])

    def test_find_nd2s_3_found(self):
        self.service._os._listdir = ["lulz.txt", "FYLM-140909-001.nd2", "FYLM-140909-003.nd2",
                                     "nothing.csv", "FYLM-140909-002.nd2"]
        model = ExperimentModel()
        model.base_dir = "/home/lulz"
        model.start_date = "140909"
        self.service.find_nd2s(model)
        self.assertListEqual(["/home/lulz/FYLM-140909-001.nd2",
                              "/home/lulz/FYLM-140909-002.nd2",
                              "/home/lulz/FYLM-140909-003.nd2"], sorted([nd2 for nd2 in model.nd2s]))