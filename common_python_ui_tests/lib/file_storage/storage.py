from .external_storage import ExternalStorage
from .local_storage import LocalStorage


class Storage:
    instance: ExternalStorage = None

    @classmethod
    def init(cls, instance):
        assert isinstance(instance, ExternalStorage) or \
               isinstance(instance, LocalStorage)
        cls.instance = instance

    @classmethod
    def local_path(cls, *path_tail):
        return cls.instance.local_path(*path_tail)

    @classmethod
    def clear_cache(cls):
        return cls.instance.clear_cache()

    @classmethod
    def receive(cls, path_in_storage):
        return cls.instance.receive(path_in_storage)

    @classmethod
    def open(cls, file_path, mode='rb'):
        return cls.instance.open(file_path, mode)

    @classmethod
    def find(cls, path_in_storage, filetype):
        return cls.instance.find_files_filetype_at_storage(path_in_storage, filetype)
