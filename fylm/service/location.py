from fylm.service.base import BaseSetService
from fylm.service.interactor.location import ApproximateChannelFinder
# from fylm.service.interactor.location import ExactChannelFinder
from nd2reader import Nd2
import logging

log = logging.getLogger("fylm")


class LocationSet(BaseSetService):
    def __init__(self, experiment):
        super(LocationSet, self).__init__()
        self._experiment = experiment
        self._name = "channel locations"
        self._nd2 = Nd2(self._experiment.get_nd2_from_timepoint(1))

    def save_action(self, model):
        image = self._nd2.get_image(0, model.field_of_view, "", 1)
        acf = ApproximateChannelFinder(image.data)
        (top_left_x, top_left_y), (bottom_right_x, bottom_right_y) = acf.results
        model.set_header(top_left_x, top_left_y, bottom_right_x, bottom_right_y)