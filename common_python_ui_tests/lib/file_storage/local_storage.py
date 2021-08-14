import os
from contextlib import contextmanager


class LocalStorage:
    def __init__(self, location: str):
        self.location = location

    def _resolve_path(self, file_path: str):
        return os.path.join(self.location, *file_path.split('/'))

    @contextmanager
    def open(self, file_path: str, mode='rb'):
        if os.path.isabs(file_path):
            if not file_path.startswith(self.location):
                raise ValueError("Absolute path doesn't belong to the storage.")
            file_path = '/'.join(file_path[len(self.location):].strip('/\\').split('/\\'))

        abs_path = os.path.join(self.location, *file_path.split('/'))
        folder, name = os.path.split(abs_path)
        if not os.path.exists(folder):
            os.makedirs(folder)
        descriptor = open(abs_path, mode=mode)
        yield descriptor
        descriptor.close()

    def clear_cache(self):
        raise NotImplementedError("Local storage has no cache.")

    def local_path(self, *path_tail):
        file_path = os.path.join(*path_tail)
        if os.path.isabs(file_path):
            if not file_path.startswith(self.location):
                raise ValueError("Absolute path doesn't belong to the storage.")

        return os.path.join(self.location, file_path)
