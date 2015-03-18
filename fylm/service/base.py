from abc import abstractmethod
from fylm.service.reader import Reader
from fylm.service.utilities import FileInteractor
import logging
import os

log = logging.getLogger(__name__)


class BaseService(object):
    """
    Basically this just exists to allow dependency injection for testing wherever services interact with
    third party systems.

    """
    def __init__(self):
        self._os = os


class BaseSetService(BaseService):
    """
    All services that do analysis and write results to disk should inherit from this.

    """
    def __init__(self):
        super(BaseSetService, self).__init__()
        self._name = "BaseService"

    @abstractmethod
    def save_action(self, model):
        """
        Calculates values and sets them on the model, so that when it is passed to the file writer,
        the correct data gets written to disk.

        :type model:    fylm.model.base.BaseFile()

        """
        raise NotImplemented

    def save_text(self, model_set):
        """
        Takes a model set, calculates any values that need to be calculated, and writes them to disk.

        :type model_set:    fylm.mode.base.BaseSet()

        """
        did_work = False
        remaining = list(model_set.remaining)
        for model in remaining:
            log.debug("Remaining: %s %s %s" % (model.time_period, model.field_of_view, model.channel_number))
        for model in remaining:
            did_work = True
            writer = FileInteractor(model)
            self.save_action(model)
            writer.write_text()
        if not did_work:
            log.info("All %s have been calculated." % self._name)

    def load_existing_models(self, model_set):
        """
        Loads every existing model from disk and puts it into the model set.

        """
        reader = Reader()
        self.find_current(model_set)
        for model in model_set.existing:
            reader.read(model)

    def find_current(self, model_set):
        """
        Searches the directory for files that have already been created.

        :param model_set:   fylm.model.base.BaseSet()

        """
        for filename in self._os.listdir(model_set.base_path):
            model_set.add_existing_data_file(filename)