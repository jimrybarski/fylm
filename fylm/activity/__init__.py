from fylm.service.rotation import RotationSet as RotationSetService
from fylm.model.rotation import RotationSet
from fylm.service.timestamp import TimestampSet as TimestampSetService
from fylm.model.timestamp import TimestampSet
from fylm.service.registration import RegistrationSet as RegistrationSetService
from fylm.model.registration import RegistrationSet
from fylm.service.image_reader import ImageReader
from fylm.service.location import LocationSet as LocationSetService
from fylm.model.location import LocationSet


class Activity(object):
    def __init__(self, experiment):
        self._experiment = experiment

    def _calculate_and_save(self, SetModel, Service):
        set_model = SetModel(self._experiment)
        service = Service(self._experiment)
        service.find_current(set_model)
        service.save(set_model)

    def calculate_rotation_offset(self):
        self._calculate_and_save(RotationSet, RotationSetService)

    def extract_timestamps(self):
        self._calculate_and_save(TimestampSet, TimestampSetService)

    def calculate_registration(self):
        self._calculate_and_save(RegistrationSet, RegistrationSetService)

    def get_image_reader(self):
        return ImageReader(self._experiment)

    def input_channel_locations(self):
        self._calculate_and_save(LocationSet, LocationSetService)