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

    @abstractproperty
    def data(self):
        """
        Yields or returns the data that was written to disk, with the types converted appropriately from strings.
        Data is returned in the order it was obtained in the experiment.

        """
        raise NotImplemented


class BaseSet(object):
    def __init__(self, experiment, top_level_dir):
        self.base_path = experiment.data_dir + "/" + top_level_dir
        self._current_filenames = []
        # The default regex assumes the only distinguishing features are timepoints and fields of view.
        self._regex = re.compile(r"""tp\d+-fov\d+.txt""")
        # We use 1-based indexing for fields of view
        self._fields_of_view = [fov + 1 for fov in range(experiment.field_of_view_count)]
        # Timepoints are already 1-based since they come from the ND2 filenames
        self._timepoints = [timepoint for timepoint in experiment.timepoints]
        # The BaseFile model that this set contains
        self._model = None

    @property
    def _expected(self):
        """
        Yields instantiated children of BaseFile that represent the work we expect to have done.

        """
        assert self._model is not None
        for field_of_view in self._fields_of_view:
            for timepoint in self._timepoints:
                model = self._model()
                model.timepoint = timepoint
                model.field_of_view = field_of_view
                model.base_path = self.base_path
                yield model

    @property
    def remaining(self):
        """
        Yields a child of BaseFile that represents work needing to be done.

        """
        for model in self._expected:
            if model.filename not in self._current_filenames:
                yield model

    def add_existing_data_file(self, filename):
        """
        Informs the model of a unit of work that has already been done.

        :param filename:    path to a file that contains completed work
        :type filename:     str

        """
        if self._regex.match(filename):
            self._current_filenames.append(filename)