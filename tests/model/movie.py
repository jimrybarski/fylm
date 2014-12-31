import unittest
from fylm.model.movie import Movie


class MovieTests(unittest.TestCase):
    def setUp(self):
        self.movie = Movie(100, 300)

    def test_trim_zero(self):
        start, stop = self.movie._get_triangle_boundaries(0)
        self.assertEqual(start, 0)
        self.assertEqual(stop, 11)

    def test_trim_right(self):
        start, stop = self.movie._get_triangle_boundaries(-3)
        self.assertEqual(start, 0)
        self.assertEqual(stop, 8)

    def test_trim_left(self):
        start, stop = self.movie._get_triangle_boundaries(3)
        self.assertEqual(start, 3)
        self.assertEqual(stop, 11)

    def test_frame_height(self):
        self.movie.add_slot("", 0)
        self.movie.add_slot("", 1)
        self.movie.add_slot("", 2)
        self.movie.add_slot("GFP", 1)
        self.movie.add_slot("dsRed", 1)
        self.assertEqual(self.movie.frame_height, 500)

    def test_frame_height_again(self):
        self.movie.add_slot("", 0)