from fylm.service.experiment import Experiment as ExperimentService
from fylm.service.puncta import PunctaSet as PunctaService
import logging


log = logging.getLogger(__name__)

experiment = ExperimentService().get_experiment("141111", "/home/jim/Desktop/experiments", "2.2.3")
ps = PunctaService(experiment)

channelz = [
     (4, 12, 1),
     (6, 26, 1),
     (6, 22, 3),
     (6, 23, 3),
        (0, 7, 1),
        (7, 26, 2),
        (7, 8, 4),
        (0, 26, 3),
        (4, 16, 4),
        (5, 13, 2),
        (7, 6, 2),
        (3, 19, 1),
        (3, 26, 3),
        (0, 12, 2),
        (5, 12, 2),
        (1, 24, 3),
        (7, 14, 1),
        (0, 18, 2),
        (1, 11, 4),
        (6, 20, 3),
        (7, 9, 2),
        (1, 13, 3),
        (4, 19, 1),
        # (6, 24, 3),
        # (4, 26, 2),
        # (0, 20, 2),
        # (7, 12, 2),
        # (4, 23, 2),
        # (3, 8, 2),
        # (7, 19, 2),
        # (7, 0, 1),
        # (7, 2, 1),
        # (4, 14, 1),
        # (3, 27, 1),
        # (4, 18, 3),
        # (3, 22, 4),
        # (4, 0, 2),
        # (6, 2, 4),
        # (0, 10, 3),
]
for fov, channel, death_tp in channelz:
    pd = ps.get_puncta_data(fov, channel)
    pd.dump(death_tp)

print("********* DONE &&&&&&&&&&")
