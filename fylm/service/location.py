from fylm.service.base import BaseSetService
from fylm.service.interactor.location import ApproximateChannelFinder
from fylm.service.interactor.exact import ExactChannelFinder
from fylm.service.image_reader import ImageReader
import logging

log = logging.getLogger("fylm")


class LocationSet(BaseSetService):
    def __init__(self, experiment):
        super(LocationSet, self).__init__()
        self._name = "channel locations"
        self._image_reader = ImageReader(experiment)

    def save_action(self, model):
        image = self._image_reader.get_image(0, 1)
        acf = ApproximateChannelFinder(image.data)
        top_left_x, top_left_y, bottom_right_x, bottom_right_y = acf.results
        model.set_header(top_left_x, top_left_y, bottom_right_x, bottom_right_y)
        exact = ExactChannelFinder(model, image.data)