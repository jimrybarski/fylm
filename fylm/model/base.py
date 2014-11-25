from abc import abstractproperty, abstractmethod


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

    @abstractproperty
    def filename(self):
        """
        Returns the name of the file.

        """
    @abstractmethod
    def load(self, data):
        """
        Populates some or all of the model's attributes from a text stream.

        :param data:    a stream of text representing the data in a model
        :type data:     str

        """
        raise NotImplemented


class BaseSet(object):
    def __init__(self, experiment, top_level_directory):
        self.base_path = experiment.data_dir + "/%s" % top_level_directory
        self._current_filenames = []
        self._regex = None

    @abstractproperty
    def _expected(self):
        raise NotImplemented

    @property
    def remaining(self):
        """
        Yields a child of BaseFile that represents work needing to be done.

        """
        for model in self._expected:
            if model.filename not in self._current_filenames:
                yield model

    def add_current(self, filename):
        if self._regex.match(filename):
            self._current_filenames.append(filename)