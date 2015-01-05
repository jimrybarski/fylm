from fylm.model.experiment import Experiment as ExperimentModel
from fylm.service.errors import terminal_error
import logging
import os
import re
import nd2reader

log = logging.getLogger("fylm")


class Experiment(object):
    def __init__(self):
        self._os = os

    def get_experiment(self, experiment_start_date, base_dir):
        experiment = ExperimentModel()

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

        # set the timepoints
        self._find_timepoints(experiment)
        self._build_directories(experiment)
        self._get_nd2_attributes(experiment)
        return experiment

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
                   "movie"]
        for subdir in subdirs:
            try:
                self._os.makedirs(experiment.data_dir + "/" + subdir)
            except OSError:
                pass

    def _find_timepoints(self, experiment):
        """
        Finds the timepoints of all available ND2 files associated with the experiment.

        """
        regex = re.compile(r"""FYLM-%s-0(?P<index>\d+)\.nd2""" % experiment.start_date.clean_date)
        found = False
        for filename in sorted(self._os.listdir(experiment.base_dir)):
            match = regex.match(filename)
            if match:
                found = True
                index = int(match.group("index"))
                log.debug("Timepoint: %s" % index)
                experiment.add_timepoint(index)
        if not found:
            log.warn("No ND2s available for this experiment!")

    def _get_nd2_attributes(self, experiment):
        # grab the first nd2 file available
        try:
            nd2_filename = sorted([n for n in experiment.nd2s])[0]
            nd2 = nd2reader.Nd2(nd2_filename)
            experiment.field_of_view_count = nd2.field_of_view_count
        except Exception as e:
            terminal_error("Could not find field of view count: %s" % e)
        else:
            return True