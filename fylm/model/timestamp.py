from fylm.model.base import BaseFile
import re


class TimestampSet(object):
    def __init__(self, experiment):
        self.base_path = experiment.data_dir + "/timestamps"


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
    def filename(self):
        return "tp%s-fov%s-timestamps.txt" % (self.timepoint, self.field_of_view)

    @property
    def path(self):
        return "%s/%s" % (self.base_path, self.filename)