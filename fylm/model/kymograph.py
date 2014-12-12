from fylm.model.base import BaseFile, BaseSet
from fylm.service.errors import terminal_error
import logging
import re

log = logging.getLogger("fylm")


class KymographSet(BaseSet):
    """
    Models all kymograph images for a given experiment.

    """
    def __init__(self, experiment):
        super(KymographSet, self).__init__(experiment, "kymograph")
        self._model = Kymograph
        self._regex = re.compile(r"""tp\d+-fov\d+-channel\d+.txt""")


class Kymograph(BaseFile):
    def __init__(self, experiment):
        super(Kymograph, self).__init__()
        self._channel = None

    @property
    def channel(self):
        return self._channel

    @channel.setter
    def channel(self, value):
        self._channel = int(value)

    @property
    def filename(self):
        # This is just the default filename and it won't always be valid.
        return "tp%s-fov%s-channel%s.txt" % (self.timepoint, self.field_of_view, self.channel)

