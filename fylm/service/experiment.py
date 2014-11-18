import os
import logging
from fylm.model import Experiment as ExperimentModel, StartDate
from fylm.service import terminal_error

log = logging.getLogger("fylm")


class Experiment(object):

    def get_experiment(self, experiment_start_date, base_dir):
        experiment = ExperimentModel()

        # set start date
        start_date = StartDate(experiment_start_date)
        if not start_date.is_valid:
            terminal_error("Invalid start date: %s (use the format: YYMMDD)" % experiment_start_date)
        experiment.start_date = start_date

        # set the base directory
        if not os.path.isdir(base_dir):
            terminal_error("Base directory does not exist: %s" % base_dir)
        experiment.base_dir = base_dir

    def set_files(self, experiment):
        """
        Finds all ND2 files associated with the experiment and determines what work has been done.

        """
        