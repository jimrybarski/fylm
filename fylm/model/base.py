from abc import abstractproperty, abstractmethod
import re


class BaseFile(object):
    def __init__(self):
        self.base_path = None
        self.timepoint = None
        self.field_of_view = None

    @abstractproperty
    def lines(self):
        """
        Yields lines of text that should be written to the file.

        """
        raise NotImplemented

    @property
    def path(self):
        return "%s/%s" % (self.base_path, self.filename)

    @property
    def filename(self):
        # This is just the default filename and it won't always be valid.
        return "tp%s-fov%s.txt" % (self.timepoint, self.field_of_view)

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
        # The default regex assumes the only distinguishing features are timepoints and fields of view.
        self._regex = re.compile(r"""tp\d+-fov\d+.txt""")
        # We use 1-based indexing for fields of view
        self._fields_of_view = [fov + 1 for fov in range(experiment.field_of_view_count)]
        # Timepoints are already 1-based since they come from the ND2 filenames
        self._timepoints = [timepoint for timepoint in experiment.timepoints]

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