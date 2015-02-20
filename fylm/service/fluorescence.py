from fylm.service.base import BaseSetService
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
        self._name = "fluorescence analyses"

    @timer
    def save_action(self, fl_model):
        """
        Calculates the rotation offset for a single field of view and time_period.

        :type fl_model:   fylm.model.fluorescence.Fluorescence()

        """
        log.debug("Creating fluorescence file %s" % fl_model.filename)
        # This is a pretty naive loop - the same file will get opened 8-12 times
        # There are obvious ways to optimize this but that can be done later if it matters
        # It probably doesn't matter though and I like simple things
        nd2_filename = self._experiment.get_nd2_from_time_period(fl_model.time_period)
        nd2 = nd2reader.Nd2(nd2_filename)
        # gets the first out-of-focus image from the first time_period in the stack
        for image_set in nd2.image_sets(fl_model.field_of_view, z_levels=[1]):
            mean, stddev, median, area, centroid = self._measure_fluorescence()
            fl_model.add(mean, stddev, median, area, centroid)

    @staticmethod
    def _measure_fluorescence():
        pass