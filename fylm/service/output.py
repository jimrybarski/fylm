from fylm.service.base import BaseSetService
from fylm.model.timestamp import TimestampSet
from fylm.model.annotation import KymographAnnotationSet
from fylm.service.timestamp import TimestampSet as TimestampService
from fylm.service.annotation import AnnotationSet
from fylm.model.kymograph import KymographSet
from fylm.service.kymograph import KymographSet as KymographSetService
from fylm.model.fluorescence import FluorescenceSet
from fylm.service.fluorescence import FluorescenceSet as FluorescenceService
import logging


log = logging.getLogger(__name__)


class OutputSet(BaseSetService):
    """
    Determines the rotational skew of an image.

    """
    def __init__(self, experiment):
        super(OutputSet, self).__init__()
        self._name = "output"
        self._experiment = experiment
        self._timestamp_set = TimestampSet(experiment)
        timestamp_service = TimestampService(experiment)
        timestamp_service.load_existing_models(self._timestamp_set)
        kymograph_set = KymographSet(experiment)
        kymograph_service = KymographSetService(experiment)
        kymograph_service.load_existing_models(kymograph_set)
        self._annotation_set = KymographAnnotationSet(experiment)
        self._annotation_set.kymograph_set = kymograph_set
        annotation_service = AnnotationSet(experiment)
        annotation_service.load_existing_models(self._annotation_set)
        self._fluorescence_set = FluorescenceSet(experiment)
        fl_service = FluorescenceService(experiment)
        fl_service.load_existing_models(self._fluorescence_set)

    def save_action(self, model):
        model.timestamp_set = self._timestamp_set
        model.fluorescence_set = self._fluorescence_set
        model.annotation = self._annotation_set.get_model(model.field_of_view, model.channel_number)