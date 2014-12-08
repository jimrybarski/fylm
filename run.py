from fylm.service.experiment import Experiment as ExperimentService
from fylm.activity import Activity

experiment = ExperimentService().get_experiment("141111", "/home/jim/Desktop/experiments")

act = Activity(experiment)
act.calculate_rotation_offset()
act.extract_timestamps()
act.calculate_registration()
# image_reader = act.get_image_reader()
# image_reader.field_of_view = 1
# for i in image_reader:
#     print(i.timestamp)