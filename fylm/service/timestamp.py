from fylm.service.utilities import FileInteractor
import logging
import nd2reader

log = logging.getLogger("fylm")


class TimestampExtractor(object):
    """
    Reads timestamps from ND2 files and writes them to disk.

    """
    def __init__(self, experiment):
        self._experiment = experiment

    def save(self, timestamp_set):
        """
        Writes missing timestamp files.

        :type timestamp_set: fylm.model.TimestampSet()

        """
        did_work = False
