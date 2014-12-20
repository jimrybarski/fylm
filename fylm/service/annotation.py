from fylm.service.base import BaseSetService
from fylm.service.interactor.annotation import KymographAnnotator
import logging

log = logging.getLogger("fylm")


class AnnotationSet(BaseSetService):
    """
    Saves the annotations of kymographs produced by a human.

    """
    def __init__(self, experiment):
        super(AnnotationSet, self).__init__()
        self._experiment = experiment
        self._name = "kymograph annotations"

    def save(self, annotation_model_set):
        annotation_model_set.load_existing_models()
        if annotation_model_set.remaining:
            KymographAnnotator(annotation_model_set)
        if not annotation_model_set.did_work:
            log.debug("All %s have been calculated." % self._name)