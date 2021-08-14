import logging
import os
import random
from datetime import timedelta, datetime

from common_api_tests.lib.file_storage.storage import Storage

log = logging.getLogger(__name__)


class FilesHelper:
    """
    Example of the code to work with the files.
    """
    RANDOM_ID = random.randint(1, 1000000)

    @staticmethod
    def create_folder_if_not_exists():
        """
        Generate unique folder path for concurrency runs
        """
        folder_path = os.path.join(
            os.getcwd(), f'QA_AUTO_temp_downloads_{FilesHelper.RANDOM_ID}')
        try:
            os.mkdir(folder_path)
        except FileExistsError:
            log.info(f"Directory {folder_path} already exists")

        return folder_path

    @staticmethod
    def is_file_downloaded(folder, current_files_qty, time_to_wait):
        ending_time = datetime.now() + timedelta(seconds=time_to_wait)
        while True:
            if len(os.listdir(folder)) > current_files_qty:
                return True
            elif datetime.now() >= ending_time:
                log.info(f"Download time's up: {time_to_wait} seconds gone")
                return False

    @staticmethod
    def get_file_path(file_name):
        with Storage.open(file_name, 'rb'):
            return os.path.join(Storage.instance.location, os.path.join(file_name))
