from fylm.service.experiment import Experiment as ExperimentService
from fylm.activity import Activity
import sys

# The date of the experiment you want to quantify. This must match the ND2 files.
experiment_date = "141111"

# The directory where the ND2 files are location. A directory will be created within
# this directory, named whatever the experiment date is. All the output will go there.
nd2_dir = "/home/jim/Desktop/experiments"

experiment = ExperimentService().get_experiment(experiment_date, nd2_dir)

activities = ("rotation",
              "timestamp",
              "registration",
              "location",
              "kymograph",
              "annotation")

act = Activity(experiment)

actions = {"rotation": act.calculate_rotation_offset,
           "timestamp": act.extract_timestamps,
           "registration": act.calculate_registration,
           "location": act.input_channel_locations,
           "kymograph": act.create_kymographs,
           "annotation": act.annotate_kymographs}

# For debugging purposes, you can skip certain actions by passing their names as arguments on the command line.
# My current use case for this is to skip the channel location thing, since I don't want to quantify everything
# and just do two fields of view total before moving on to the next steps.

for activity in activities:
    if activity not in sys.argv[1:]:
        actions[activity]()