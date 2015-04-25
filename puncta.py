from fylm.service.experiment import Experiment as ExperimentService
from fylm.service.puncta import PunctaSet as PunctaService
import logging


log = logging.getLogger(__name__)

experiment = ExperimentService().get_experiment("141111", "/tmp/", "2.2.3")
ps = PunctaService(experiment)

print("OK you can use ps")

