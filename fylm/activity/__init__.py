from fylm.service.rotation import RotationSet as RotationSetService
from fylm.model.rotation import RotationSet
from fylm.service.timestamp import TimestampSet as TimestampSetService
from fylm.model.timestamp import TimestampSet
from fylm.service.registration import RegistrationSet as RegistrationSetService
from fylm.model.registration import RegistrationSet
from fylm.service.location import LocationSet as LocationSetService
from fylm.model.location import LocationSet
from fylm.service.kymograph import KymographSet as KymographSetService
from fylm.model.kymograph import KymographSet
from fylm.service.annotation import AnnotationSet
from fylm.model.annotation import KymographAnnotationSet
from fylm.service.movie import MovieSet as MovieSetService
from fylm.model.movie import MovieSet
from fylm.service.output import OutputSet as OutputSetService
from fylm.model.output import OutputSet
from fylm.service.summary import Summary as SummaryService
from fylm.model.summary import SummarySet
from fylm.service.fluorescence import FluorescenceSet as FluorescenceService
from fylm.model.fluorescence import FluorescenceSet


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

    def quantify_fluorescence(self):
        if self._experiment.has_fluorescent_channels:
            self._calculate_and_save_text(FluorescenceSet, FluorescenceService)

    def create_kymographs(self):
        """
        We can't use _calculate_and_save() because it would be inefficient to iterate
        over the entire image stack for each channel.

        """
        kymograph_service = KymographSetService(self._experiment)
        kymograph_set = KymographSet(self._experiment)
        kymograph_service.save(kymograph_set)

    def annotate_kymographs(self):
        annotation_service = AnnotationSet(self._experiment)
        annotation_set = KymographAnnotationSet(self._experiment)
        annotation_service.save(annotation_set)

    def make_movies(self, field_of_view):
        movie_service = MovieSetService(self._experiment)
        movie_set = MovieSet(self._experiment, field_of_view)
        movie_service.save(movie_set)

    def generate_output(self):
        self._calculate_and_save_text(OutputSet, OutputSetService)

    def generate_summary(self):
        self._calculate_and_save_text(SummarySet, SummaryService)

    def analyze_puncta(self, time_period, fov, channel):
        pass
    #     p = PunctaSet(self._experiment)
    #     p.save(time_period, fov, channel)