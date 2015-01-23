from fylm.model.base import BaseTextFile, BaseSet
from collections import defaultdict


class SummarySet(BaseSet):
    def __init__(self, experiment):
        super(SummarySet, self).__init__(experiment, "summary")

    def _expected(self):
        final_state = FinalState()
        final_state.base_path = self.base_path
        yield final_state
        # in the future, yield the general summary (issue #81)


class FinalState(BaseTextFile):
    def __init__(self):
        super(FinalState, self).__init__()
        self._data = defaultdict(dict)
        self._state_code = {"Ejected": "-1",
                            "Empty": "0",
                            "Dies": "1",
                            "Survives": "2"}

    @property
    def filename(self):
        return "final_state.txt"

    def add(self, time_period, channel, state):
        self._data[time_period][channel] = state

    @property
    def lines(self):
        for time_period, channel in sorted(self._data.items()):
            line = tuple(self._state_code[state] for channel, state in sorted(channel.items()))
            template = "%s " * len(line)
            yield (template % line).strip()