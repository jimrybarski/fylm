from fylm.model.base import BaseFile, BaseSet
import re


class RotationSet(BaseSet):
    """
    Models all the rotation offsets for a given experiment (over any number of ND2 files).

    """
    def __init__(self, experiment):
        super(RotationSet, self).__init__(experiment, "rotation")
        self._fields_of_view = [fov for fov in range(experiment.field_of_view_count)]
        self._timepoints = [timepoint for timepoint in experiment.timepoints]
        self._regex = re.compile(r"""tp\d+-fov\d+-rotation.txt""")

    @property
    def _expected(self):
        """
        Yields all the rotation offset models that represent all the calculations we could do for the
        available images.

        """
        for field_of_view in self._fields_of_view:
            for timepoint in self._timepoints:
                rotation = Rotation()
                rotation.timepoint = timepoint
                rotation.field_of_view = field_of_view
                rotation.base_path = self.base_path
                yield rotation


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
        return "%s/%s" % (self.base_path, self.filename)