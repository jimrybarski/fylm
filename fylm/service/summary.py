from fylm.service.annotation import AnnotationSet as AnnotationService
from fylm.model.annotation import KymographAnnotationSet


class Summary(object):
    def __init__(self, experiment):
        self._annotation_set = KymographAnnotationSet(experiment)
        AnnotationService(experiment).load_existing_models(self._annotation_set)

    def save(self):
        pass