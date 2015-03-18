from fylm.service.errors import terminal_error
import logging
import nd2reader
import os

log = logging.getLogger(__name__)


class Experiment(object):
    def __init__(self):
        """
        Models all the analysis that has been done for a particular FYLM experiment.
        Since we can only run one physical experiment at a time, and the experiments take at least one
        day (though ideally four) the start date for an experiment acts as a unique ID.

        """
        self._base_dir = None
        self.start_date = None

    def load(self, start_date, base_dir):
        self.start_date = start_date
        # set the base directory
        if not os.path.isdir(base_dir):
            terminal_error("Base directory does not exist: %s" % base_dir)
        self.base_dir = base_dir
        log.debug("Experiment base directory: %s" % self.base_dir)

        # set the time_periods
        self._get_nd2_attributes()

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

    def _find_time_periods(self, experiment):
        """
        Finds the time_periods of all available ND2 files associated with the experiment.

        """
        regex = re.compile(r"""FYLM-%s-0(?P<time_period>\d+)\.nd2""" % experiment.start_date.clean_date)
        found = False
        for filename in sorted(self._os.listdir(experiment.base_dir)):
            match = regex.match(filename)
            if match:
                found = True
                time_period = int(match.group("time_period"))
                log.debug("time_period: %s" % time_period)
                experiment.add_time_period(time_period)
        for time_period in self._read_time_period_log(experiment):
            found = True
            experiment.add_time_period(time_period)
        if not found:
            terminal_error("No ND2s found!")

    def _get_nd2_attributes(self):
        """
        Determine how many fields of view there are, and whether the ND2s have fluorescent channels.

        :type experiment:   model.experiment.Experiment()

        """
        for nd2_filename in self.nd2s:
            try:
                nd2 = nd2reader.Nd2(nd2_filename)
            except IOError:
                pass
            else:
                self.field_of_view_count = nd2.field_of_view_count
                for channel in nd2.channels:
                    if channel.name != "":
                        log.info("Experiment has fluorescent channels.")
                        experiment.has_fluorescent_channels = True
                        break
                else:
                    log.info("Experiment does not have fluorescent channels.")
                break
        else:
            terminal_error("Could not get the field of view count. Maybe all the ND2s are missing?")