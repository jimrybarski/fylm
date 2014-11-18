import logging
from nd2reader import Nd2
import re

log = logging.getLogger("fylm")


class StartDate(object):
    def __init__(self, start_date):
        self._raw_date = start_date

    @property
    def is_valid(self):
        try:
            regex = re.compile(r"""^(?P<year>\d\d)(?P<month>\d\d)(?P<day>\d\d)$""")
            match = regex.match(self.clean_date)
            year_ok = 14 <= int(match.group("year")) <= 25
            month_ok = 1 <= int(match.group("month")) <= 12
            day_ok = 1 <= int(match.group("day")) <= 31
        except Exception as e:
            log.error(str(e))
            return False
        else:
            return year_ok and month_ok and day_ok

    @property
    def clean_date(self):
        return self._raw_date.strip("\n\r\t ")


class Experiment(object):
    def __init__(self):
        """
        Models all the analysis that has been done for a particular FYLM experiment.
        Since we can only run one physical experiment at a time, and the experiments take at least one
        day (though ideally four) the start date for an experiment acts as a unique ID.

        """
        self._start_date = None
        self._base_dir = None

    @property
    def start_date(self):
        return self._start_date.clean_date

    @start_date.setter
    def start_date(self, value):
        """
        :type value:    fylm.model.StartDate()

        """
        self._start_date = value

    @property
    def base_dir(self):
        return self._base_dir

    @base_dir.setter
    def base_dir(self, value):
        """
        :param value:   the parent directory that contains the ND2 file and the directory with the data
                        for this particular experiment
        :type value:    str

        """
        self._base_dir = value.rstrip("/")

    @property
    def _nd2_base_filename(self):
        return self.base_dir + "/" + "FYLM-%s-00" % self.start_date