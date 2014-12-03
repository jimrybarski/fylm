from fylm.model.base import BaseFile, BaseSet
import logging
import re

log = logging.getLogger("fylm")


class RegistrationSet(BaseSet):
    """
    Models all the translational offsets needed to align every image in a given field of view.

    """
    def __init__(self, experiment):
        super(RegistrationSet, self).__init__(experiment, "registration")
        self._model = Registration


class Registration(BaseFile):
    """
    Models the output file that contains the translational adjustments needed for all images in a stack.

    """
    def __init__(self):
        super(Registration, self).__init__()
        self.timepoint = None
        self.field_of_view = None
        self._offsets = {}
        self._line_regex = re.compile(r"""^(?P<index>\d+) (?P<dx>-?\d+\.\d+) (?P<dy>-?\d+\.\d+)""")

    def load(self, data):
        for line in data:
            try:
                index, dx, dy = self._parse_line(line)
            except Exception as e:
                log.error("Could not parse line: '%s' because of: %s" % (line, e))
            else:
                self._offsets[index] = dx, dy

    def _parse_line(self, line):
        match = self._line_regex.match(line)
        return int(match.group("index")), float(match.group("dx")), float(match.group("dy"))

    @property
    def _ordered_data(self):
        for index, (dx, dy) in sorted(self._offsets.items()):
            yield index, dx, dy

    @property
    def data(self):
        for index, dx, dy in self._ordered_data:
            yield dx, dy

    @property
    def lines(self):
        for index, dx, dy in self._ordered_data:
            yield "%s %s %s" % (index, dx, dy)

    def add(self, dx, dy):
        index = 1 if not self._offsets.keys() else max(self._offsets.keys()) + 1
        log.debug("%s dx: %s dy: %s" % (index, dx, dy))
        self._offsets[index] = float(dx), float(dy)