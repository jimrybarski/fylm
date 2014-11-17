from abc import abstractproperty


class BaseFile(object):
    def __init__(self):
        self.base_path = None

    @abstractproperty
    def lines(self):
        """
        Yields lines of text that should be written to the file.

        """
        raise NotImplemented

    @abstractproperty
    def path(self):
        """
        Returns the path relative to the base directory where the file should be written to.

        """
        raise NotImplemented