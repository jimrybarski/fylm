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
            terminal_error("Invalid start date: %s" % experiment_start_date)
        experiment.start_date = start_date

        # set the base directory
        if not os.path.isdir(base_dir):
            terminal_error("Base directory does not exist: %s" % base_dir)
        experiment.base_dir = base_dir


    # @staticmethod
    # def _join_dirs(base_dir, sub_dir):
    #     """
    #     Creates an absolute path from a base directory and a relative directory. The resulting path
    #     does not necessarily exist.
    #
    #     :param base_dir:    the base directory (an absolute path)
    #     :type base_dir:     str
    #     :param sub_dir:     a relative path to a directory or file
    #     :type sub_dir:      str
    #
    #     """
    #     return base_dir.rstrip("/") + "/" + sub_dir