from fylm.service.base import BaseSetService
from fylm.service.location import LocationSet as LocationService
from fylm.model.location import LocationSet
from fylm.service.utilities import timer
import logging
import nd2reader

log = logging.getLogger(__name__)


class FluorescenceSet(BaseSetService):
    """
    Determines the rotational skew of an image.

    """
    def __init__(self, experiment):
        super(FluorescenceSet, self).__init__()
        self._experiment = experiment
        self._location_set = LocationSet(experiment)
        LocationService(experiment).load_existing_models(experiment)
        self._name = "fluorescence analyses"

    @timer
    def save_action(self, fl_model):
        """
        Calculates the rotation offset for a single field of view and time_period.

        :type fl_model:   fylm.model.fluorescence.Fluorescence()

        """
        log.debug("Creating fluorescence file %s" % fl_model.filename)
        nd2_filename = self._experiment.get_nd2_from_time_period(fl_model.time_period)
        nd2 = nd2reader.Nd2(nd2_filename)
        channels = [channel.name for channel in nd2.channels if channel.name != ""]
        fl_model.image_slice = self._location_set.
        # gets the first out-of-focus image from the first time_period in the stack
        for image_set in nd2.image_sets(fl_model.field_of_view, z_levels=[1]):
            for channel in channels:
                mean, stddev, median, area, centroid = self._measure_fluorescence(image_set, channel)
                fl_model.add(mean, stddev, median, area, centroid)

    @staticmethod
    def _measure_fluorescence(image_set, channel):
        pass