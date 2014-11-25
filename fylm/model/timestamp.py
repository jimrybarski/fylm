from fylm.model.base import BaseFile, BaseSet


class TimestampSet(BaseSet):
    """
    Models all the timestamps for every set of images.

    """
    def __init__(self, experiment):
        super(TimestampSet, self).__init__(experiment, "timestamps")

    def _expected(self):



class Timestamp(BaseFile):
    def __init__(self):
        super(Timestamp, self).__init__()
        self.timepoint = None
        self.field_of_view = None
        self._timestamps = []

    def load(self, data):
        for line in data:
            self._timestamps.append(float(line))

    @property
    def lines(self):
        for timestamp in self._timestamps:
            yield str(timestamp)

    @property
    def path(self):
        return "%s/%s" % (self.base_path, self.filename)