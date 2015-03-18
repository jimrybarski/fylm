class WorkUnit(object):
    def __init__(self, model, required_data_sources, dependencies=None):
        """

        :param model:   the data structure that is being populated with data
        :param required_data_sources:   one of: "nd2", "imagereader"
        :type required_data_sources:    str
        :param dependencies:    models that must be completed before this one can be started
        :type dependencies:     str

        """
        self._model = model
        self._required_data_sources = required_data_sources
        self._dependencies = dependencies
        self._model_sources = {}

    def add_model_source(self, model_source):
        self._model_sources[model_source.name] = model_source

    @property
    def required_data_sources(self):
        return self._required_data_sources

    @property
    def is_complete(self):
        return self._model.is_complete

    @property
    def name(self):
        return self._model.name

    def dependencies_satisfied(self, completed_work_units):
        completed_names = [work_unit.name for work_unit in completed_work_units]
        for dependency in self._dependencies:
            if dependency not in completed_names:
                return False
        return True