from fylm.service.base import BaseSetService
from fylm.service.interactor.annotation import KymographAnnotator
from fylm.model.kymograph import KymographSet
from fylm.service.kymograph import KymographSet as KymographSetService
import logging

log = logging.getLogger(__name__)


class AnnotationSet(BaseSetService):
    """
    Saves the annotations of kymographs produced by a human.

    """
    def __init__(self, experiment):
        super(AnnotationSet, self).__init__()
        self._experiment = experiment
        self._kymograph_set = KymographSet(experiment)
        KymographSetService(experiment).load_existing_models(self._kymograph_set)
        self._name = "kymograph annotations"

    def save(self, annotation_model_set):
        annotation_model_set.kymograph_set = self._kymograph_set
        self.load_existing_models(annotation_model_set)
        if annotation_model_set.work_remains:
            # There are annotations that need to be done still
            KymographAnnotator(annotation_model_set)
        else:
            log.debug("All %s have been calculated." % self._name)