from fylm.service.base import BaseSetService
from fylm.model.timestamp import TimestampSet
from fylm.model.annotation import KymographAnnotationSet
from fylm.service.timestamp import TimestampSet as TimestampService
from fylm.service.annotation import KymographSetService
import logging


log = logging.getLogger("fylm")


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
        self._annotation_set = KymographAnnotationSet(experiment)
        annotation_service = KymographSetService(experiment)
        annotation_service.load_existing_models(self._annotation_set)

    def save_action(self, model):
        model.timestamp_set = self._timestamp_set
        model.annotation = self._annotation_set.get_model(model.field_of_view, model.channel_number)