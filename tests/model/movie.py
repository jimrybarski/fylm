import numpy as np
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
        self.assertEqual(self.movie._frame_height, 500)

    def test_frame_height_again(self):
        self.movie.add_slot("", 0)

    def test_get_slot_bounds(self):
        start, stop = self.movie._get_slot_bounds(0)
        self.assertEqual(start, 0)
        self.assertEqual(stop, 100)
        start, stop = self.movie._get_slot_bounds(1)
        self.assertEqual(start, 100)
        self.assertEqual(stop, 200)

    def test_slots(self):
        movie = Movie(2, 3)
        movie.add_slot("", 0)
        movie.add_slot("", 1)
        movie.add_slot("", 2)
        movie.add_slot("GFP", 1)
        movie.add_slot("dsRed", 1)
        movie.update_image("", 0, np.array([[0, 0, 0], [0, 0, 0]]))
        movie.update_image("", 1, np.array([[1, 1, 1], [1, 1, 1]]))
        movie.update_image("", 2, np.array([[2, 2, 2], [2, 2, 2]]))
        movie.update_image("GFP", 1, np.array([[3, 3, 3], [3, 3, 3]]))
        movie.update_image("dsRed", 1, np.array([[4, 4, 4], [4, 4, 4]]))
        slots = [slot for slot in movie._slots]
        self.assertTrue((slots[0] == np.array([[0, 0, 0], [0, 0, 0]])).all())
        self.assertTrue((slots[1] == np.array([[1, 1, 1], [1, 1, 1]])).all())
        self.assertTrue((slots[2] == np.array([[2, 2, 2], [2, 2, 2]])).all())
        self.assertTrue((slots[3] == np.array([[3, 3, 3], [3, 3, 3]])).all())
        self.assertTrue((slots[4] == np.array([[4, 4, 4], [4, 4, 4]])).all())
        
    def test_frame(self):
        movie = Movie(2, 3)
        movie.add_slot("", 0)
        movie.add_slot("", 1)
        movie.add_slot("", 2)
        movie.add_slot("GFP", 1)
        movie.add_slot("dsRed", 1)
        movie.update_image("", 0, np.array([[0, 0, 0], [0, 0, 0]]))
        movie.update_image("", 1, np.array([[1, 1, 1], [1, 1, 1]]))
        movie.update_image("", 2, np.array([[2, 2, 2], [2, 2, 2]]))
        movie.update_image("GFP", 1, np.array([[3, 3, 3], [3, 3, 3]]))
        movie.update_image("dsRed", 1, np.array([[4, 4, 4], [4, 4, 4]]))
        frame = movie.frame
        self.assertTupleEqual(frame.shape, (10, 3, 3))
        expected_frame = np.array([[[0, 0, 0],
                                   [0, 0, 0],
                                   [0, 0, 0]],
                                   [[0, 0, 0],
                                   [0, 0, 0],
                                   [0, 0, 0]],
                                   [[1, 1, 1],
                                   [1, 1, 1],
                                   [1, 1, 1]],
                                   [[1, 1, 1],
                                   [1, 1, 1],
                                   [1, 1, 1]],
                                   [[2, 2, 2],
                                   [2, 2, 2],
                                   [2, 2, 2]],
                                   [[2, 2, 2],
                                   [2, 2, 2],
                                   [2, 2, 2]],
                                   [[3, 3, 3],
                                   [3, 3, 3],
                                   [3, 3, 3]],
                                   [[3, 3, 3],
                                   [3, 3, 3],
                                   [3, 3, 3]],
                                   [[4, 4, 4],
                                   [4, 4, 4],
                                   [4, 4, 4]],
                                   [[4, 4, 4],
                                   [4, 4, 4],
                                   [4, 4, 4]]])
        self.assertTrue((frame == expected_frame).all())