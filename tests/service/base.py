import unittest
from fylm.service.base import BaseModelService
from io import BytesIO
from mock import patch


class MockModel(object):
    def __init__(self):
        self.data = []
        self.path = "/tmp/file.txt"

    def load(self, data):
        for datapoint in data:
            self.data.append(datapoint)


class BaseModelServiceTests(unittest.TestCase):
    def setUp(self):
        self.bms = BaseModelService()

    @patch('__builtin__.open')
    def test_read(self, mo):
        mo.return_value = BytesIO("13.4236\n43.999")
        model = MockModel()
        self.bms.read(model)
        self.assertListEqual(model.data, ["13.4236", "43.999"])