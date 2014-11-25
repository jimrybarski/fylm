from fylm.service.utilities import FileInteractor
import logging
import nd2reader

log = logging.getLogger("fylm")


class TimestampExtractor(object):
    """
    Reads timestamps from ND2 files and writes them to disk.

    """