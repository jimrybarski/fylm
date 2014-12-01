from fylm.model.base import BaseFile, BaseSet


class RegistrationSet(BaseSet):
    """
    Models all the translational offsets needed to align every image in a given field of view.

    """
    def __init__(self, experiment):
        super(RegistrationSet, self).__init__(experiment, "registration")
        self._model = Registration


class Registration(BaseFile):
    """
    Models the output file that contains the translational adjustments needed for all images in a stack.

    """
    def __init__(self):
        super(Registration, self).__init__()
        self._offset = None

    def load(self, data):
        pass

    @property
    def lines(self):
        yield str(self._offset)