import unittest
from fylm.model.movie import Movie


class MovieTests(unittest.TestCase):
    def setUp(self):
        self.movie = Movie()

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

