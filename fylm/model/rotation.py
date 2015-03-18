class Rotation(object):
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