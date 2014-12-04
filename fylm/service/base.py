from abc import abstractmethod
from fylm.service.utilities import FileInteractor
import logging
import os

log = logging.getLogger("fylm")


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

    def save(self, model_set):
        """
        Takes a model set, calculates any values that need to be calculated, and writes them to disk.

        :type model_set:    fylm.mode.base.BaseSet()

        """
        did_work = False
        for model in model_set.remaining:
            did_work = True
            writer = FileInteractor(model)
            self.save_action(model)
            writer.write_text()
        if not did_work:
            log.debug("All %s have been calculated." % self._name)

    def find_current(self, model_set):
        """
        Searches the directory for files that have already been created.

        :param model_set:   fylm.model.base.BaseSet()

        """
        for filename in self._os.listdir(model_set.base_path):
            model_set.add_existing_data_file(filename)