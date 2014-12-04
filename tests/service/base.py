import unittest
from fylm.service.base import BaseModelService
from fylm.model.registration import Registration
from fylm.model.rotation import Rotation
from fylm.model.timestamp import Timestamps
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
        mo.return_value = BytesIO("13.4236\n43.999\n")
        model = MockModel()
        self.bms.read(model)
        self.assertListEqual(model.data, ["13.4236", "43.999"])

    @patch('__builtin__.open')
    def test_read_bad_data(self, mo):
        mo.return_value = None
        model = MockModel()
        with self.assertRaises(SystemExit):
            self.bms.read(model)

    @patch('__builtin__.open')
    def test_read_registration(self, mo):
        mo.return_value = BytesIO("1 2.125 -2.95\n2 2.45 -1.4\n3 2.25 -1.775")
        registration = Registration()
        self.bms.read(registration)
        self.assertListEqual(list(registration.data), [(2.125, -2.95), (2.45, -1.4), (2.25, -1.775)])

    @patch('__builtin__.open')
    def test_read_rotation(self, mo):
        mo.return_value = BytesIO("0.0943695191964\n")
        rotation = Rotation()
        self.bms.read(rotation)
        self.assertEqual(rotation.data, 0.0943695191964)

    @patch('__builtin__.open')
    def test_read_timestamps(self, mo):
        mo.return_value = BytesIO("1 2.53743594082\n2 123.396288891\n3 244.143293866\n")
        timestamps = Timestamps()
        self.bms.read(timestamps)
        self.assertListEqual(list(timestamps.data), [2.53743594082, 123.396288891, 244.143293866])