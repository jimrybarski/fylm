import argparse
from fylm.service.experiment import Experiment as ExperimentService
from fylm.activity import Activity
import sys
import os


with open(os.path.dirname(sys.argv[0]) + "/VERSION") as f:
    version = f.read(-1).strip()


class Args(dict):
    """
    This class just allows us to get arguments from argparse using dot syntax.

    """
    pass

parser = argparse.ArgumentParser()
parser.add_argument('date', help='Date formatted like YYMMDD')
parser.add_argument('dir', help='The directory where the ND2 files are located (and where results are stored)')
parser.add_argument('--skip', nargs="+", default=[], help='Steps to skip (useful mostly for debugging)')
parser.add_argument('--action', help='Do an optional action')
parser.add_argument('-t', '--timepoint', type=int, help='Specifies a timepoint (needed only for some steps)')
parser.add_argument('-f', '--fov', type=int, help='Specifies a field of view (needed only for some steps)')
parser.add_argument('-c', '--channel', type=int, help='Specifies a channel (needed only for some steps)')
parser.add_argument("-v", "--verbosity", action="count", default=0, help="Specify -v through -vvvvv")
args = parser.parse_args(namespace=Args())

experiment = ExperimentService().get_experiment(args.date, args.dir, version)

# These are the actions that need to be run to completion for each experiment.
standard_activities = ("rotation",
                       "timestamp",
                       "registration",
                       "location",
                       "kymograph",
                       "annotation")

# Define what each action is and the arguments it takes (note: not all methods take arguments)
act = Activity(experiment)
actions = {"rotation": act.calculate_rotation_offset,
           "timestamp": act.extract_timestamps,
           "registration": act.calculate_registration,
           "location": act.input_channel_locations,
           "kymograph": act.create_kymographs,
           "annotation": act.annotate_kymographs,
           "movie": act.make_movie}
action_args = {"movie": (args.timepoint, args.fov, args.channel)}

# Now run whatever methods are needed
if not args.action:
    # The user didn't specify a specific action, so we'll do the standard set of actions
    for activity in standard_activities:
        if activity not in args.skip:
            actions[activity]()
else:
    # A specific action was selected
    method = actions[args.action]
    # Check if the method needs arguments to be passed to it, and look them up if so
    arguments = action_args.get(args.action)
    if arguments:
        method(*arguments)
    else:
        method()