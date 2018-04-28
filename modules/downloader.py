# Copyright (C) 2018  Artur Fogiel
# This file is part of pyDNSHelper.
#
# pyDNSHelper is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# pyDNSHelper is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with pyDNSHelper.  If not, see <http://www.gnu.org/licenses/>.

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
        self.parts = 1

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
        :raise: ValueError
        :rtype: bool
        """
        if not str(url):
            raise ValueError("url cannot be empty")

        if not str(file_path):
            raise ValueError("file_path cannot be empty")

        self.clean()
        self.url = url
        self.file_path = file_path

        response = requests.get(self.url, stream=True)
        total_length = response.headers.get('content-length')

        if total_length is not None:
            self.total_bytes = int(total_length)
            # TODO: watch out for small files
            part_bytes = int(total_length) / self.parts

            self.create_empty_file(self.file_path)

            print("starting threads")
            for i in range(self.parts):
                start = int(part_bytes * i)
                end = int(start + part_bytes)

            self.threads.append(Thread(target=self.dl(), kwargs={'start': start, 'end': end}))
            self.threads[0].start()
            self.threads[0].join()

    def dl(self, start, end):
        with open(self.file_path, "w+b") as file:
            print("Downloading %s" % self.file_path)

            # specify the starting and ending of the file
            headers = {'Range': 'bytes=%d-%d' % (start, end)}
            response = requests.get(self.url, headers=headers, stream=True)

            self.downloaded_bytes = 0
            for data in response.iter_content(chunk_size=self.chunk_bytes):
                # continue ?
                if self.work == WorkMode.STOP or self.work == WorkMode.CANCEL:
                    self.clean()
                    file.close()
                    if self.work == WorkMode.CANCEL:
                        os.unlink(self.file_path)
                    break

                self.downloaded_bytes += len(data)
                file.seek(start)
                file.write(data)

    def stop(self):
        self.work = WorkMode.STOP

    def cancel(self):
        self.work = WorkMode.CANCEL

    @property
    def get_progress(self) -> []:
        return [self.total_bytes, self.downloaded_bytes]