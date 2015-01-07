from fylm.model.timestamp import Timestamps
from fylm.service.reader import Reader
from fylm.service.base import BaseSetService
from fylm.service.utilities import timer
import logging
import nd2reader

log = logging.getLogger("fylm")


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

        :type timestamps_model: fylm.model.Timestamps()

        """
        if timestamps_model.time_period > 1:
            previous_model = Timestamps()
            previous_model.base_path = timestamps_model.base_path
            previous_model.time_period = timestamps_model.time_period - 1
            previous_model.field_of_view = timestamps_model.field_of_view
            reader = Reader()
            reader.read(previous_model)
            last_timestamp = previous_model.last
        else:
            last_timestamp = 0.0
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
            timestamps_model.add(image.timestamp + last_timestamp)