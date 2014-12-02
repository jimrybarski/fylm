from fylm.service.rotation import RotationCorrector
from fylm.model.rotation import RotationSet
from fylm.service.timestamp import TimestampExtractor
from fylm.model.timestamp import TimestampSet
from fylm.service.registration import RegistrationCorrector
from fylm.model.registration import RegistrationSet


class Activity(object):
    def __init__(self, experiment):
        self._experiment = experiment

    def _calculate_and_save(self, SetModel, Service):
        set_model = SetModel(self._experiment)
        service = Service(self._experiment)
        service.find_current(set_model)
        service.save(set_model)

    def calculate_rotation_offset(self):
        self._calculate_and_save(RotationSet, RotationCorrector)

    def extract_timestamps(self):
        self._calculate_and_save(TimestampSet, TimestampExtractor)

    def calculate_registration(self):
        self._calculate_and_save(RegistrationSet, RegistrationCorrector)