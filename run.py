from fylm.service.experiment import Experiment as ExperimentService
from fylm.activity import Activity


experiment = ExperimentService().get_experiment("141028", "/home/jim/Desktop/experiments")

act = Activity(experiment)
act.calculate_rotation_offset()
act.extract_timestamps()
act.calculate_registration()
act.input_channel_locations()
# act.create_kymographs()
act.fov_movie()