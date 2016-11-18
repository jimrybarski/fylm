from fylm.service.base import BaseSetService
from fylm.service.interactor.location import ApproximateChannelFinder
from fylm.service.interactor.exact import ExactChannelFinder
from fylm.service.image_reader import ImageReader
import logging

log = logging.getLogger(__name__)


class LocationSet(BaseSetService):
    def __init__(self, experiment):
        super(LocationSet, self).__init__()
        self._name = "channel locations"
        self._image_reader = ImageReader(experiment)

    def save_action(self, model):
        self._image_reader.field_of_view = model.field_of_view
        self._image_reader.time_period = 1
        image = self._image_reader.get_image(0, channel="Mono", z_level=1)
        acf = ApproximateChannelFinder(image.data, model.field_of_view)
        top_left_x, top_left_y, bottom_right_x, bottom_right_y = acf.results
        model.set_header(top_left_x, top_left_y, bottom_right_x, bottom_right_y)
        ExactChannelFinder(model, image.data)