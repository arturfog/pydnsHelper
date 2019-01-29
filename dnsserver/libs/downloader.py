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

from webui.models import Logs

# Test file with not even number of bytes:
# https://ftp.gnu.org/pub/gnu/bash/bash-2.02.1.tar.gz

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
        self.parts = 2

    def clean(self):
        self.total_bytes = 0
        self.downloaded_bytes = 0
        self.work = True
        del self.threads[:]
        self.url = ''
        self.file_path = ''

    def create_empty_file(self, file_path: str):
        fp = open(file_path, "wb")
        fp.seek(self.total_bytes - 1)
        fp.write(b"\0")
        fp.close()

    @staticmethod
    def gen_random_filename(prefix: str, directory: str):
        import tempfile
        name = tempfile.mktemp(prefix=prefix, dir=directory)
        return name

    @staticmethod
    def get_filename_from_url(url: str):
        pass

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
        print(repr(response.headers))

        if total_length is not None:
            print("Total: " + str(total_length))
            self.total_bytes = int(total_length)
            # don't download files smaller than 128 Kb in chunks
            if self.total_bytes < 131072:
                self.parts = 1

            part_bytes = int(total_length) / self.parts
            print("Part: " + str(part_bytes))

            self.create_empty_file(self.file_path)

            print("starting threads")
            for i in range(self.parts):
                start = int((part_bytes + 1) * i)
                end = int(start + part_bytes)
                if i == (self.parts - 1):
                    end = self.total_bytes
                self.threads.append(Thread(target=self.dl, kwargs={'start': start, 'end': end}))
                self.threads[i].start()

            for i in range(self.parts):
                self.threads[i].join()

    def dl(self, start: int, end: int):
        with open(self.file_path, "w+b") as file:
            log = "Downloading %s" % self.file_path + " s:" + str(start) + " e: " + str(end)
            Logs.objects.create(log)
            # specify the starting and ending of the file
            headers = {'Range': 'bytes=%d-%d' % (start, end)}
            response = requests.get(self.url, headers=headers, stream=True)

            self.downloaded_bytes = 0
            file.seek(start)
            for data in response.iter_content(chunk_size=self.chunk_bytes):
                # continue ?
                if self.work == WorkMode.STOP or self.work == WorkMode.CANCEL:
                    print("stopping download ...")
                    self.clean()
                    file.close()
                    if self.work == WorkMode.CANCEL:
                        print("cancelling download ...")
                        os.unlink(self.file_path)
                    break

                self.downloaded_bytes += len(data)
                file.write(data)
            file.close()

    def stop(self):
        self.work = WorkMode.STOP

    def cancel(self):
        self.work = WorkMode.CANCEL

    @property
    def get_progress(self) -> []:
        return [self.total_bytes, self.downloaded_bytes]