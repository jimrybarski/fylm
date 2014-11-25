from fylm.model.base import BaseFile
import re


class RotationSet(object):
    """
    Models all the rotation offsets for a given experiment (over any number of ND2 files).

    """
    def __init__(self, experiment):
        self._fields_of_view = [fov for fov in range(experiment.field_of_view_count)]
        self._timepoints = [timepoint for timepoint in experiment.timepoints]
        self._base_path = experiment.data_dir
        self._current_rotation_filenames = []
        self._regex = re.compile(r"""tp\d+-fov\d+-rotation.txt""")

    @property
    def _expected_rotations(self):
        """
        Yields all the rotation offset models that represent all the calculations we could do for the
        available images.

        """
        for field_of_view in self._fields_of_view:
            for timepoint in self._timepoints:
                rotation = Rotation()
                rotation.timepoint = timepoint
                rotation.field_of_view = field_of_view
                rotation.base_path = self._base_path
                yield rotation

    @property
    def remaining_rotations(self):
        """
        Yields a model.Rotation for each rotation offset that needs to be calculated.

        """
        for rotation in self._expected_rotations:
            if rotation.filename not in self._current_rotation_filenames:
                yield rotation

    def add_current_rotation(self, filename):
        if self._regex.match(filename):
            self._current_rotation_filenames.append(filename)


class Rotation(BaseFile):
    """
    Models the output file that contains the rotational adjustment required for all images in a stack.

    """
    def __init__(self):
        super(Rotation, self).__init__()
        self.timepoint = None
        self.field_of_view = None
        self._offset = None

    def load(self, data):
        self.offset = data.strip("\n ")

    @property
    def offset(self):
        """
        The number of degrees the image must be rotated in order for the FYLM to be perfectly aligned in the image.

        """
        return self._offset

    @offset.setter
    def offset(self, value):
        self._offset = float(value)

    @property
    def lines(self):
        yield str(self._offset)

    @property
    def filename(self):
        return "tp%s-fov%s-rotation.txt" % (self.timepoint, self.field_of_view)

    @property
    def path(self):
        return "%s/rotation/%s" % (self.base_path, self.filename)