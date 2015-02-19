from fylm.service.errors import terminal_error
import logging
import re


log = logging.getLogger(__name__)


class StartDate(object):
    def __init__(self, start_date):
        self._raw_date = start_date

    @property
    def is_valid(self):
        try:
            regex = re.compile(r"""^(?P<year>\d\d)(?P<month>\d\d)(?P<day>\d\d)$""")
            match = regex.match(self.clean_date)
            year_ok = 14 <= int(match.group("year")) <= 38  # we'd better cure aging by 2038
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
        self._time_periods = set()
        self.field_of_view_count = None
        self._version = None

    @property
    def version(self):
        return self._version

    @version.setter
    def version(self, value):
        version_regex = re.compile(r"""\d+\.\d+\.\d+""")
        if version_regex.match(value):
            self._version = value
        else:
            log.critical("Change the value in the VERSION file in the root directory of fylm_critic to 'x.y.z'.")
            terminal_error("Invalid version number! %s" % value)

    @property
    def start_date(self):
        return self._start_date

    @start_date.setter
    def start_date(self, value):
        """
        :type value:    str

        """
        self._start_date = StartDate(value)

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
    def data_dir(self):
        return self.base_dir + "/" + self.start_date.clean_date

    @property
    def _nd2_base_filename(self):
        return self.base_dir + "/" + "FYLM-%s-" % self.start_date.clean_date

    @property
    def nd2s(self):
        """
        Yields absolute paths to the ND2 files associated with this experiment.

        :returns:   str

        """
        for time_period in self.time_periods:
            yield self.get_nd2_from_time_period(time_period)

    def get_nd2_from_time_period(self, time_period):
        # pads time_period with leading zeros to create 3-digit number
        return self._nd2_base_filename + "%03d.nd2" % time_period

    def add_time_period(self, number):
        """
        Registers the existence of an ND2 file with a given index.

        :param number:  the series number (e.g. the 7 in FYLM-140909-007.nd2)
        :type number:   int

        """
        assert number > 0
        self._time_periods.add(number)

    @property
    def time_periods(self):
        for time_period in sorted(self._time_periods):
            yield time_period

    @property
    def time_period_count(self):
        return len(self._time_periods)

    @property
    def fields_of_view(self):
        for i in range(self.field_of_view_count):
            yield i