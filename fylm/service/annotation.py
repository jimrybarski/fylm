from fylm.service.base import BaseSetService
from fylm.service.interactor.annotation import KymographAnnotator
from fylm.model.kymograph import KymographSet
import logging

log = logging.getLogger("fylm")


class AnnotationSet(BaseSetService):
    """
    Saves the annotations of kymographs produced by a human.

    """
    def __init__(self, experiment):
        super(AnnotationSet, self).__init__()
        self._experiment = experiment
        self._kymograph_set = KymographSet(experiment)
        self._name = "kymograph annotations"

    def save(self, annotation_model_set):
        annotation_model_set.load_existing_models()
        if list(annotation_model_set.remaining):
            # There are annotations that need to be done still
            KymographAnnotator(annotation_model_set, self._kymograph_set)
        else:
            log.debug("All %s have been calculated." % self._name)