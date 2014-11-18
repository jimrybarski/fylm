from fylm.model.experiment import StartDate, Experiment
import unittest
import logging

log = logging.getLogger("fylm")
log.disabled = True


class ExperimentTests(unittest.TestCase):
    def setUp(self):
        self.ex = Experiment()

    def test_start_date_setter(self):
        self.ex.start_date = StartDate("140914")
        self.assertEqual(self.ex._start_date.clean_date, "140914")

    def test_start_date_getter(self):
        self.ex._start_date = StartDate("140914")
        self.assertEqual(self.ex.start_date, "140914")

    def test_base_dir_setter(self):
        self.ex.base_dir = "/home/lulz"
        self.assertEqual(self.ex._base_dir, "/home/lulz")

    def test_base_dir_setter_trailing_slash(self):
        self.ex.base_dir = "/home/lulz/"
        self.assertEqual(self.ex._base_dir, "/home/lulz")

    def test_nd2_base_filename(self):
        self.ex.start_date = StartDate("140914")
        self.ex.base_dir = "/home/lulz"
        self.assertEqual(self.ex.nd2_base_filename, "/home/lulz/FYLM-140914-00")


class StartDateTests(unittest.TestCase):
    def test_clean_date(self):
        sd = StartDate(" 140913 \n")
        self.assertEqual(sd.clean_date, "140913")

    def test_is_valid(self):
        sd = StartDate(" 140913 \n")
        self.assertTrue(sd.is_valid)

    def test_is_valid_missing_day(self):
        sd = StartDate("1409")
        self.assertFalse(sd.is_valid)

    def test_is_valid_invalid_year(self):
        sd = StartDate("310914")
        self.assertFalse(sd.is_valid)

    def test_is_valid_invalid_month(self):
        sd = StartDate("141302")
        self.assertFalse(sd.is_valid)

    def test_is_valid_invalid_day(self):
        sd = StartDate("141335")
        self.assertFalse(sd.is_valid)

    def test_is_valid_stupid_date(self):
        sd = StartDate("14-09-21")
        self.assertFalse(sd.is_valid)