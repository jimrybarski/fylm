from fylm.service.base import BaseSetService
from fylm.service.interactor.location import ApproximateChannelFinder
from fylm.service.interactor.location import ExactChannelFinder
from nd2reader import Nd2
import logging

log = logging.getLogger("fylm")


class LocationSet(BaseSetService):
    def __init__(self, experiment):
        super(LocationSet, self).__init__()
        self._experiment = experiment
        self._name = "channel locations"

    def save_action(self, model):
        nd2 = Nd2(model)
        ApproximateChannelFinder()