import os


class BaseService(object):
    def __init__(self):
        self._os = os


class SingleDirectoryService(BaseService):
    def find_current(self, file_set):
        for filename in self._os.listdir(file_set.base_path):
            file_set.add_current(filename)