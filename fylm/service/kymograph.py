from fylm.model.constants import Constants
from fylm.service.base import BaseSetService
import nd2reader
import logging


log = logging.getLogger("fylm")


class RegistrationSet(BaseSetService):
    """
    Determines the rotational skew of an image.

    """
    def __init__(self, experiment):
        super(RegistrationSet, self).__init__()
        self._experiment = experiment
        self._name = "registration offsets"

    def save(self, model_set):
        pass