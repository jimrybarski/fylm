from fylm.model.constants import Constants
from fylm.service.annotation import AnnotationSet as AnnotationSetService
from fylm.model.annotation import KymographAnnotationSet
from fylm.model.summary import SummarySet
from fylm.service.base import BaseSetService


class Summary(BaseSetService):
    def __init__(self, experiment):
        super(Summary, self).__init__()
        self._experiment = experiment
        self._annotation_service = AnnotationSetService(experiment)
        self._annotation_set = KymographAnnotationSet(experiment, ignore_kymographs=True)
        self._annotation_set.kymograph_set = self._annotation_service._kymograph_set
        self._annotation_service.load_existing_models(self._annotation_set)
        self._summary_set = SummarySet(experiment)

    def save_action(self, model):
        """
        We don't know what order the models will come in, and there's only one of each class,
        so we dynamically pick their save method.

        """
        action = {"FinalState": self._save_final_state}
        model_type = model.__class__.__name__
        action[model_type](model)

    def _save_final_state(self, model):
        for field_of_view in self._experiment.fields_of_view:
            for channel_number in xrange(Constants.NUM_CATCH_CHANNELS):
                channel_group = self._annotation_set.get_model(field_of_view, channel_number)
                state = "Empty" if channel_group is None else channel_group.last_state
                model.add(field_of_view, channel_number, state)