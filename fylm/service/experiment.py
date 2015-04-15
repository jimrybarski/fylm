from fylm.model.experiment import Experiment as ExperimentModel
from fylm.service.errors import terminal_error
import logging
import json
import os
import re
import nd2reader
import time

log = logging.getLogger(__name__)


class Experiment(object):
    def __init__(self):
        self._os = os

    def get_experiment(self, experiment_start_date, base_dir, version):
        experiment = ExperimentModel()
        experiment.version = version

        # set start date
        experiment.start_date = experiment_start_date
        if not experiment.start_date.is_valid:
            terminal_error("Invalid start date: %s (use the format: YYMMDD)" % experiment_start_date)
        log.debug("Experiment start date: %s" % experiment.start_date.clean_date)

        # set the base directory
        if not self._os.path.isdir(base_dir):
            terminal_error("Base directory does not exist: %s" % base_dir)
        experiment.base_dir = base_dir
        log.debug("Experiment base directory: %s" % experiment.base_dir)

        # set the time_periods
        # experiment log as Python dict
        # {'time_periods': [1, 2, 3],
        #  'field_of_view_count': 8,
        #  'has_fluorescent_channels': True}
        self._find_time_periods(experiment)
        self._build_directories(experiment)
        self._get_nd2_attributes(experiment)
        return experiment

    def _load_experiment_log(self, experiment):
        with open(experiment.data_dir + "/experiment.txt", "a+") as f:
            try:
                experiment_log = json.load(f)
            except ValueError:
                experiment_log = {'time_periods': [], 'start_unix_timestamps': {}}
            return experiment_log

    def _save_experiment_log(self, experiment, experiment_log):
        with open(experiment.data_dir + "/experiment.txt", "w+") as f:
            json.dump(experiment_log, f)

    def add_time_period_to_log(self, experiment, time_period):
        experiment_log = self._load_experiment_log(experiment)
        if time_period in experiment_log['time_periods']:
            log.debug("TP%s already in experiment.txt" % time_period)
            return True
        log.debug("TP%s must be added experiment.txt" % time_period)
        experiment_log['time_periods'].append(time_period)
        self._save_experiment_log(experiment, experiment_log)

    def _build_directories(self, experiment):
        """
        Creates all the directories needed for output files.

        Currently works for:
            1. rotation

        """
        # first make all the top-level directories
        subdirs = ["annotation",
                   "fluorescence",
                   "kymograph",
                   "location",
                   "puncta",
                   "registration",
                   "rotation",
                   "timestamp",
                   "movie",
                   "output",
                   "summary"]
        for subdir in subdirs:
            try:
                self._os.makedirs(experiment.data_dir + "/" + subdir)
            except OSError:
                pass

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
        experiment_log = self._load_experiment_log(experiment)
        for time_period in experiment_log['time_periods']:
            found = True
            experiment.add_time_period(time_period)
        if not found:
            terminal_error("No ND2s found!")

    def _get_nd2_attributes(self, experiment):
        """
        Determine several attributes of the ND2s used in this experiment.

        :type experiment:   model.experiment.Experiment()

        """
        experiment_log = self._load_experiment_log(experiment)
        for n, nd2_filename in enumerate(experiment.nd2s):
            try:
                nd2 = nd2reader.Nd2(nd2_filename)
            except IOError:
                pass
            else:
                # We need to know the absolute time that an experiment began so we can figure out the gap between
                # different files (as that could be any amount of time).
                log.debug("ABSTART %s" % nd2.absolute_start)

                timestamp = self._utc_timestamp(nd2.absolute_start)
                time_period = n + 1
                experiment.set_time_period_start_time(time_period, timestamp)
                experiment_log['start_unix_timestamps'][time_period] = timestamp

                experiment.field_of_view_count = nd2.field_of_view_count
                experiment_log['field_of_view_count'] = nd2.field_of_view_count
                experiment_log['has_fluorescent_channels'] = False
                for channel in nd2.channels:
                    if channel.name != "":
                        log.info("Experiment has fluorescent channels.")
                        experiment.has_fluorescent_channels = True
                        experiment_log['has_fluorescent_channels'] = True
                        break
                else:
                    log.info("Experiment does not have fluorescent channels.")
                self._save_experiment_log(experiment, experiment_log)
                break
        else:
            # There are no ND2s so we load all the information we need from the log.
            if 'field_of_view_count' not in experiment_log.keys() or 'has_fluorescent_channels' not in experiment_log.keys():
                terminal_error("No ND2s found and no attributes saved. It seems like you haven't even started this experiment.")
            experiment.field_of_view_count = int(experiment_log['field_of_view_count'])
            experiment.has_fluorescent_channels = experiment_log['has_fluorescent_channels']
            for time_period, timestamp in experiment_log['start_unix_timestamps'].items():
                experiment.set_time_period_start_time(time_period, timestamp)

    def _utc_timestamp(self, date):

        # We're converting stuff here. Is it good?

        return time.mktime(tuple(date.utctimetuple())) - time.mktime((1970, 1, 1, 0, 0, 0, 0, 0, 0))