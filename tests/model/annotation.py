import unittest
from fylm.model.annotation import Annotation


class AnnotationTests(unittest.TestCase):

    def test_parse(self):
        text_line = "4 12.345,13.222 6.757,4.646"
        self.annotation = Annotation(text_line)
        self.assertEqual(self.annotation.index, 4)
        self.assertEqual(self.annotation.coordinates[0].x, 12.345)
        self.assertEqual(self.annotation.coordinates[0].y, 13.222)
        self.assertEqual(self.annotation.coordinates[1].x, 6.757)
        self.assertEqual(self.annotation.coordinates[1].y, 4.646)