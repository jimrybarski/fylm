import argparse
from fylm.service.experiment import Experiment as ExperimentService
from fylm.activity import Activity
import logging
import sys
import os


root = os.path.dirname(sys.argv[0])
version_filename = "VERSION" if root == '' else "/VERSION"
with open(root + version_filename) as f:
    version = f.read(-1).strip()

log = logging.getLogger(__name__)


class Args(dict):
    """
    This class just allows us to get arguments from argparse using dot syntax.

    """
    pass

try:
    parser = argparse.ArgumentParser()
    parser.add_argument('date', help='Date formatted like YYMMDD')
    parser.add_argument('dir', help='The directory where the ND2 files are located (and where results are stored)')
    parser.add_argument('--skip', nargs="+", default=[], help='Steps to skip (useful mostly for debugging)')
    parser.add_argument('--action', help='Do an optional action')
    parser.add_argument('-t', '--timeperiod', default=1, type=int, help='Specifies a time period (needed only for some steps)')
    parser.add_argument('-f', '--fov', type=int, default=0, help='Specifies a field of view (needed only for some steps)')
    parser.add_argument('-c', '--channel', type=int, default=0, help='Specifies a catch channel (needed only for some steps)')
    parser.add_argument('--movies', action='store_true', help='Make movies for space-separated time periods')
    parser.add_argument("-v", "--verbosity", action="count", default=0, help="Specify -v through -vvvvv")
    parser.add_argument('-r', "--review", action='store_true', help="Review all annotations regardless of whether they've been completed")
    args = parser.parse_args(namespace=Args())

    experiment = ExperimentService().get_experiment(args.date, args.dir, version, args.review)

    # These are the actions that need to be run to completion for each experiment.
    first_activities = ("rotation",
                        "timestamp",
                        "registration",
                        "location",
                        "kymograph")

    manual_activities = ("annotation",
                         # "fluorescence",
                         "output",
                         "summary")

    # Define what each action is and the arguments it takes (note: not all methods take arguments)
    act = Activity(experiment)
    actions = {"rotation": act.calculate_rotation_offset,
               "timestamp": act.extract_timestamps,
               "registration": act.calculate_registration,
               "location": act.input_channel_locations,
               "kymograph": act.create_kymographs,
               "movies": act.make_movies,
               "annotation": act.annotate_kymographs,
               # "fluorescence": act.quantify_fluorescence,
               "output": act.generate_output,
               "summary": act.generate_summary,
               "puncta": act.analyze_puncta,
               }

    action_args = {"movies": (int(args.fov),),
                   "puncta": (int(args.timeperiod), int(args.fov), int(args.channel))}

    # Now run whatever methods are needed
    if not args.action:
        # The user didn't specify a specific action, so we'll do the standard set of actions
        for activity in first_activities:
            if activity not in args.skip:
                actions[activity]()

        # movies get special treatment since they're almost always needed but take a very long time to produce
        if args.movies:
            # args.movies will be either None (make all movies) or a list (make specified movies)
            actions["movies"](*action_args['movies'])

        for activity in manual_activities:
            if activity not in args.skip:
                actions[activity]()
    else:
        # A specific action was selected. Usually this is for things not related to typical processing, like making
        # images for machine learning or something.
        method = actions[args.action]
        # Check if the method needs arguments to be passed to it, and look them up if so
        arguments = action_args.get(args.action)
        if arguments:
            method(*arguments)
        else:
            method()

except Exception:
    log.exception("Unhandled exception!")
    log.critical("""



    ===================  Unhandled exception!  =======================

    Jim did not account for something and fylm_critic crashed!
    Copy and paste the error above and email it to him.

    ==================================================================


    """)