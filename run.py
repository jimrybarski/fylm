from fylm.service.experiment import Experiment as ExperimentService
from fylm.activity import Activity

experiment = ExperimentService().get_experiment("141111", "/home/jim/Desktop/experiments")

act = Activity(experiment)
act.calculate_rotation_offset()