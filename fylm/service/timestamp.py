from fylm.model.timestamp import Timestamps
from fylm.service.reader import Reader
from fylm.service.base import BaseSetService
from fylm.service.utilities import timer
import logging
import nd2reader
import time

log = logging.getLogger(__name__)


class TimestampSet(BaseSetService):
    """
    Reads timestamps from ND2 files and writes them to disk.

    """
    def __init__(self, experiment):
        super(TimestampSet, self).__init__()
        self._experiment = experiment
        self._name = "timestamps"

    @timer
    def save_action(self, timestamps_model):
        """
        Writes missing timestamp files.

        So the first ND2 starts at 2015-11-13 16:53:12.
        The second ND2 starts at 2015-11-14 17:01:43.


        :type timestamps_model: fylm.model.Timestamps()

        """
        # ND2 timestamps are relative to the beginning of acquisition of a single time period. So to get the true timestamp
        # we need to look at the datetime that each ND2 began and compare it to the first ND2. This will be zero for the
        # first one.
        timestamp_offset = self._experiment.exact_start_time(timestamps_model.time_period) - self._experiment.exact_start_time(1)
        log.info("Creating timestamps for time_period:%s, Field of View:%s" % (timestamps_model.time_period,
                                                                               timestamps_model.field_of_view))
        nd2_filename = self._experiment.get_nd2_from_time_period(timestamps_model.time_period)
        nd2 = nd2reader.Nd2(nd2_filename)
        # subtract 1 from the field of view since nd2reader uses 0-based indexing, but we
        # refer to the fields of view with 1-based indexing
        for image_set in nd2.image_sets(field_of_view=timestamps_model.field_of_view,
                                        channels=[""],
                                        z_levels=[0]):
            image = [i for i in image_set][0]
            timestamps_model.add(image.timestamp + timestamp_offset)