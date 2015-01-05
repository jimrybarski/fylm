import argparse
from fylm.service.experiment import Experiment as ExperimentService
from fylm.activity import Activity
import sys


class Args(dict):
    pass

parser = argparse.ArgumentParser()
parser.add_argument('date', help='Date formatted like YYMMDD')
parser.add_argument('dir', help='The directory where the ND2 files are located (and where results are stored)')
parser.add_argument('--skip', nargs="+", help='Steps to skip (useful mostly for debugging)')
parser.add_argument('--action', help='Do an optional action')
parser.add_argument('-t', '--timepoint', type=int, help='Specifies a timepoint (needed only for some steps)')
parser.add_argument('-f', '--fov', type=int, help='Specifies a field of view (needed only for some steps)')
parser.add_argument('-c', '--channel', type=int, help='Specifies a channel (needed only for some steps)')
parser.add_argument("-v", "--verbosity", action="count", default=0, help="Specify -v through -vvvvv")
args = parser.parse_args(namespace=Args())

experiment = ExperimentService().get_experiment(args.date, args.dir)

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
           "annotation": act.annotate_kymographs,
           "movie": act.make_movie}

action_args = {"movie": (args.timepoint, args.fov, args.channel)}

if not args.action:
    # The user didn't specify a specific action, so we'll do the standard set of actions
    for activity in activities:
        if activity not in args.skip:
            actions[activity]()
else:
    method = actions[args.action]
    arguments = action_args[args.action]
    method(*arguments)