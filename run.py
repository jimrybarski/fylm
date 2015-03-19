import argparse
from fylm.model.overseer import Overseer
from fylm.model.workunit import WorkUnit
from fylm.model.timestamp import Timestamps
import logging

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
    parser.add_argument('-t', '--timepoint', type=int, help='Specifies a timepoint (needed only for some steps)')
    parser.add_argument('-f', '--fov', type=int, help='Specifies a field of view (needed only for some steps)')
    parser.add_argument('-c', '--channel', type=int, help='Specifies a channel (needed only for some steps)')
    parser.add_argument('--movies', nargs="*", default=False, help='Make movies for space-separated time periods')
    parser.add_argument("-v", "--verbosity", action="count", default=0, help="Specify -v through -vvvvv")
    args = parser.parse_args(namespace=Args())

except Exception:
    log.exception("Unhandled exception!")
    log.critical("""



    ===================  Unhandled exception!  =======================

    Jim did not account for something and fylm_critic crashed!
    Copy and paste the error above and email it to him.

    ==================================================================


    """)