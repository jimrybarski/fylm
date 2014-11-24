from fylm.service.rotation import RotationCorrector
from fylm.model.rotation import RotationSet


class Activity(object):
    def __init__(self, experiment):
        self._experiment = experiment

    def calculate_rotation_offset(self):
        rotation_set = RotationSet(self._experiment)
        corrector = RotationCorrector(self._experiment)
        corrector.save(rotation_set)