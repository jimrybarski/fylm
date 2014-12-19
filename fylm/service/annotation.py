from fylm.service.base import BaseSetService
import nd2reader
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
        pass