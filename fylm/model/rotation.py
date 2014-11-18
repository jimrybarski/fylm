from fylm.model.base import BaseFile


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