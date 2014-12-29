from fylm.service.experiment import Experiment as ExperimentService
from fylm.activity import Activity

# The date of the experiment you want to quantify. This must match the ND2 files.
experiment_date = "141111"

# The directory where the ND2 files are location. A directory will be created within
# this directory, named whatever the experiment date is. All the output will go there.
nd2_dir = "/home/jim/Desktop/experiments"

experiment = ExperimentService().get_experiment(experiment_date, nd2_dir)

act = Activity(experiment)
act.calculate_rotation_offset()
act.extract_timestamps()
act.calculate_registration()
# act.input_channel_locations()
act.create_kymographs()
# act.annotate_kymographs()
# act.fov_movie()