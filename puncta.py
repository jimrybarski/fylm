from fylm.service.experiment import Experiment as ExperimentService
from fylm.service.puncta import PunctaSet as PunctaService
import logging


log = logging.getLogger(__name__)

experiment = ExperimentService().get_experiment("150514", "/mnt/8A82663D82662E3F/150514-data", "2.2.3", False)
ps = PunctaService(experiment)

channels = [
     (1, 9, 1),
]
for fov, channel, death_tp in channels:
    pd = ps.get_puncta_data(fov, channel)
    pd.dump(death_tp)

print("********* DONE &&&&&&&&&&")
