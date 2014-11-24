from fylm.model import Experiment as ExperimentModel, StartDate
from fylm.service import terminal_error
import logging
import os
import re

log = logging.getLogger("fylm")


class Experiment(object):
    def __init__(self):
        self._os = os

    def get_experiment(self, experiment_start_date, base_dir):
        experiment = ExperimentModel()

        # set start date
        start_date = StartDate(experiment_start_date)
        if not start_date.is_valid:
            terminal_error("Invalid start date: %s (use the format: YYMMDD)" % experiment_start_date)
        experiment.start_date = start_date

        # set the base directory
        if not self._os.path.isdir(base_dir):
            terminal_error("Base directory does not exist: %s" % base_dir)
        experiment.base_dir = base_dir

    def find_timepoints(self, experiment):
        """
        Finds the timepoints of all available ND2 files associated with the experiment.

        """
        regex = re.compile(r"""FYLM-%s-0(?P<index>\d+)\.nd2""" % experiment.start_date)
        found = False
        for filename in self._os.listdir(experiment.base_dir):
            match = regex.match(filename)
            if match:
                found = True
                index = int(match.group("index"))
                experiment.add_timepoint(index)
        if not found:
            log.warn("No ND2s available for this experiment!")