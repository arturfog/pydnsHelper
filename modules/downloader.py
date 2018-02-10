import requests
import os
from urllib.parse import urlparse


class Downloader:

    def __init__(self):
        self.req = None
        self.download_dir = Downloader.get_current_dir() + "/dl/"

    @staticmethod
    def get_current_dir() -> str:
        return os.getcwd()

    def set_download_dir(self, path: str) -> None:
        self.download_dir = path

    @staticmethod
    def get_filename_from_url(url: str) -> str:
        parsed = urlparse(url)
        return os.path.basename(parsed.path)

    @property
    def get_download_dir(self) -> str:
        return self.download_dir

    def send_request(self, url: str) -> None:
        print("Sending request: " + url)
        self.req = requests.get(url)
        print(self.req.status_code)
        print(self.req.headers['content-type'])
        print(self.req.encoding)

    def download_file(self, url, filename=None):
        self.send_request(url)
        if filename is None:
            filename = self.get_filename_from_url(url)
        output_path = self.get_download_dir + filename
        print("Downloading to: " + output_path)
        with open(output_path, 'wb') as f:
            f.write(self.req.content)
