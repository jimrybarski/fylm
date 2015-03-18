class WorkUnit(object):
    def __init__(self, model):
        """

        :param model:   the data structure that is being populated with data

        """
        self._model = model
        self._model_sources = {}

    def add_model_source(self, model_source):
        self._model_sources[model_source.name] = model_source

    @property
    def required_data_sources(self):
        return self._model.required_data_sources

    @property
    def time_periods_needed(self):
        return self._model.time_periods_needed

    @property
    def name(self):
        return self._model.name

    def dependencies_satisfied(self, completed_work_units):
        completed_names = [work_unit.name for work_unit in completed_work_units]
        for dependency in self._model.dependencies:
            if dependency not in completed_names:
                return False
        return True