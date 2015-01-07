from fylm.model.base import BaseTextFile, BaseSet
import re


class RotationSet(BaseSet):
    """
    Models all the rotation offsets for a given experiment (over any number of ND2 files).

    """
    def __init__(self, experiment):
        super(RotationSet, self).__init__(experiment, "rotation")
        self._model = Rotation
        self._regex = re.compile(r"""fov\d+.txt""")
        self._time_periods = [1]

    def get_data(self, field_of_view):
        """
        Returns the rotation offset for a given field of view.

        """
        model = self._get_current(field_of_view)
        return model.data

    def _get_current(self, field_of_view):
        """
        Returns the model for a given field of view.

        """
        for model in sorted(self.existing, key=lambda x: x.time_period):
            if model.field_of_view == field_of_view:
                return model


class Rotation(BaseTextFile):
    """
    Models the output file that contains the rotational adjustment required for all images in a stack.

    """
    def __init__(self):
        super(Rotation, self).__init__()
        self._offset = None

    def load(self, data):
        """
        :param data:    a list with a single string in it that represents a float value
        :type data:     list

        """
        self.offset = float(data[0].strip("\n "))

    @property
    def filename(self):
        # This is just the default filename and it won't always be valid.
        return "fov%s.txt" % self.field_of_view

    @property
    def data(self):
        return self.offset

    @property
    def lines(self):
        yield str(self.offset)

    @property
    def offset(self):
        """
        The number of degrees the image must be rotated in order for the FYLM to be perfectly aligned in the image.

        """
        return self._offset

    @offset.setter
    def offset(self, value):
        self._offset = float(value)