import requests
from enum import Enum
import os
from threading import Thread


class WorkMode(Enum):
    NORMAL = 0
    STOP = 1
    # same as stop, but also removes file
    CANCEL = 2


class HTTPDownloader:
    def __init__(self):
        self.chunk_bytes = 4096
        self.total_bytes = 0
        self.downloaded_bytes = 0
        self.work = True
        self.url = ''
        self.file_path = ''
        self.threads = []
        self.response = None

    def clean(self):
        self.total_bytes = 0
        self.downloaded_bytes = 0
        self.work = True

    def create_empty_file(self, file_path: str):
        fp = open(file_path, "wb")
        fp.write('\0' * self.total_bytes)
        fp.close()

    def download(self, url: str, file_path: str) -> None:
        r"""Downloads file from HTTP server.

        :param url: URL of file.
        :param file_path: path to file
        :return: :bool object
        :rtype: bool
        """
        self.clean()
        self.url = url
        self.file_path = file_path

        response = requests.get(self.url, stream=True)
        total_length = response.headers.get('content-length')

        if total_length is not None:
            self.total_bytes = int(total_length)

            print("starting thread")
            self.threads.append(Thread(target=self.dl()))
            self.threads[0].start()
            self.threads[0].join()

    def dl(self):
        with open(self.file_path, "wb") as file:
            print("Downloading %s" % self.file_path)

            self.downloaded_bytes = 0
            for data in self.response.iter_content(chunk_size=self.chunk_bytes):
                # continue ?
                if self.work == WorkMode.STOP or self.work == WorkMode.CANCEL:
                    self.clean()
                    file.close()
                    if self.work == WorkMode.CANCEL:
                        os.unlink(self.file_path)
                    break

                self.downloaded_bytes += len(data)
                file.write(data)

    def stop(self):
        self.work = WorkMode.STOP

    def cancel(self):
        self.work = WorkMode.CANCEL

    @property
    def get_progress(self) -> []:
        return [self.total_bytes, self.downloaded_bytes]