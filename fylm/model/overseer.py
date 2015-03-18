"""
Coordinates all quantification.

Creates an ND2Reader and an ImageReader as needed.
Determines dependencies and doesn't create ImageReader until necessary.
Passes objects to each other as needed (so Fluorescence can get the Location and Annotation models it needs)

"""
import nd2reader
from fylm.service.image_reader import ImageReader


class Overseer(object):
    def __init__(self):
        self._work_units = []
        self._nd2 = None
        self._image_reader = None

    def add_work_unit(self, work_unit):
        self._work_units.append(work_unit)