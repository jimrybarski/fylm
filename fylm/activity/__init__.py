from fylm.service.rotation import RotationCorrector, RotationSet as RotationSetService
from fylm.model.rotation import RotationSet


class Activity(object):
    def __init__(self, experiment):
        self._experiment = experiment

    def calculate_rotation_offset(self):
        rotation_set = RotationSet(self._experiment)
        RotationSetService().find_current_rotations(rotation_set)
        corrector = RotationCorrector(self._experiment)
        corrector.save(rotation_set)