from fylm.service import RotationCorrector


class Activity(object):
    def __init__(self, experiment):
        self._experiment = experiment

    def calculate_rotation_offset(self):
        corrector = RotationCorrector(self._experiment)
        corrector.save()