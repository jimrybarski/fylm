from fylm.service.rotation import RotationSet as RotationSetService
from fylm.model.rotation import RotationSet
from fylm.service.timestamp import TimestampSet as TimestampSetService
from fylm.model.timestamp import TimestampSet
from fylm.service.registration import RegistrationSet as RegistrationSetService
from fylm.model.registration import RegistrationSet
from fylm.service.location import LocationSet as LocationSetService
from fylm.model.location import LocationSet


class Activity(object):
    def __init__(self, experiment):
        self._experiment = experiment

    def _calculate_and_save_text(self, SetModel, Service):
        set_model = SetModel(self._experiment)
        service = Service(self._experiment)
        service.find_current(set_model)
        service.save_text(set_model)

    def calculate_rotation_offset(self):
        self._calculate_and_save_text(RotationSet, RotationSetService)

    def extract_timestamps(self):
        self._calculate_and_save_text(TimestampSet, TimestampSetService)

    def calculate_registration(self):
        self._calculate_and_save_text(RegistrationSet, RegistrationSetService)

    def input_channel_locations(self):
        self._calculate_and_save_text(LocationSet, LocationSetService)

    def create_kymographs(self):
        """
        We can't use _calulate_and_save() because it would be inefficient to iterate
        over the entire image stack for each channel.

        """
        pass