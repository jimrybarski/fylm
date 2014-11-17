from fylm.service import RotationCorrector


class Activity(object):
    def __init__(self, experiment):
        self._experiment = experiment

    def rotation(self):
        service = RotationCorrector(self._experiment)
        service.save()