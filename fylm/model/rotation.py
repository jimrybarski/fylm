from fylm.model.base import BaseFile, BaseSet


class RotationSet(BaseSet):
    """
    Models all the rotation offsets for a given experiment (over any number of ND2 files).

    """
    def __init__(self, experiment):
        super(RotationSet, self).__init__(experiment, "rotation")
        self._model = Rotation


class Rotation(BaseFile):
    """
    Models the output file that contains the rotational adjustment required for all images in a stack.

    """
    def __init__(self):
        super(Rotation, self).__init__()
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