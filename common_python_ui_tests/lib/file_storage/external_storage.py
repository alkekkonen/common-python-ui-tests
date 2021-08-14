import os
import shutil
from contextlib import contextmanager
import json

import requests

from common_python_ui_tests.lib.utils.url_builder import urljoin


def download_file_from_url(url, retries_count):
    i = 0
    while i < retries_count:
        res = requests.get(url, stream=True)
        i += 1
        if res.status_code == 200:
            break
    if res.status_code != 200:
        raise ValueError(f"""Couldn't download file from '<your_storage_name>'. Response code {res.status_code}
                    Error message: {res.text}
                    Path: {url}
                    """)
    return res


class ExternalStorage:
    backup_folder = None
    DEFAULT_STORAGE_ADDRESS = "http://your_file_storage_url.com"  # Can be read from config

    def backup_file(self, path_in_storage):
        backup_file = os.path.join(self.backup_folder, path_in_storage)
        folder, _ = os.path.split(backup_file)
        os.path.exists(folder) or os.makedirs(folder)
        shutil.copy(os.path.join(self.location, path_in_storage),
                    os.path.join(self.backup_folder, path_in_storage))

    @contextmanager
    def file(self, path_in_storage: str, mode='rb'):
        url = self._resolve_url(path_in_storage)
        local_cache_path = self._resolve_local_cache_path(path_in_storage)

        if not os.path.exists(local_cache_path):
            if not self._file_exist_at_storage(url):
                raise ValueError(f'No file "{url}" at storage.')
            actual_folder, actual_name = os.path.split(local_cache_path)
            os.path.exists(actual_folder) or os.makedirs(actual_folder)
            res = download_file_from_url(url, retries_count=5)
            with open(local_cache_path, 'wb') as local_file_descriptor:
                for block in res.iter_content(1024):
                    local_file_descriptor.write(block)
            if self.backup_folder:
                self.backup_file(path_in_storage)
        open_file = open(local_cache_path, mode=mode)

        yield open_file

        open_file.close()

    def __init__(self, location: str, address=DEFAULT_STORAGE_ADDRESS):
        self.location = location
        self.address = address

    def _resolve_local_cache_path(self, path_in_storage):
        return os.path.join(self.location, *path_in_storage.split('/'))

    def _resolve_url(self, path_in_storage):
        return urljoin(self.address, *path_in_storage.split('/'))

    def open(self, path_in_storage, mode='rb'):
        if os.path.isabs(path_in_storage):
            if not path_in_storage.startswith(self.location):
                raise ValueError(f"Absolute path {path_in_storage} doesn't belong to the storage.")
            path_in_storage = '/'.join(path_in_storage[len(self.location):].strip('/\\').split('/\\'))

        if 'r' in mode:
            return self.file(path_in_storage, mode=mode)
        else:
            path = self.local_path(path_in_storage)
            folder, name = os.path.split(path)
            if not os.path.exists(folder):
                os.makedirs(folder)
            return open(path, mode)

    def clear_cache(self):
        if os.path.exists(self.location):
            shutil.rmtree(self.location)

    def local_path(self, *path_tail: str):
        file_path = '/'.join([x.strip('/') for x in path_tail])
        if os.path.isabs(file_path):
            if not file_path.startswith(self.location):
                raise ValueError("Absolute path doesn't belong to the storage.")
            return file_path
        local_abs_path = self._resolve_local_cache_path(file_path)
        if not os.path.exists(local_abs_path):
            url = self._resolve_url(file_path)
            if self._file_exist_at_storage(url):
                with self.open(file_path):
                    pass
        return local_abs_path

    def _file_exist_at_storage(self, url):
        folder = '/'.join(url.split('/')[:-1])
        name = url.split('/')[-1]
        resp = requests.get(folder)
        resp.raise_for_status()
        files = resp.json()['files']
        return name in files

    def find_files_filetype_at_storage(self, path_in_storage, file_type):
        folder_path = self._resolve_url(path_in_storage)
        resp = requests.get(folder_path).text
        content = json.loads(resp)
        files = content['files']
        found_files = []
        for filename in files:
            if filename.split('.')[-1] == file_type:
                found_files.append(filename)
        return found_files
