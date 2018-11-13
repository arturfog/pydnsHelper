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
import re
from time import sleep
from threading import Thread
from webui.models import Host


class HostsManager:
    def __init__(self):
        self.eng = None
        self.conn = None
        self.session = None
        self.threads = []
        self.do_monitor_ttl = True

    def block_site(self, url: str):
        self.remove_site(url)
        self.add_site(url=url, ttl=999)

    def unblock_site(self, url: str):
        self.remove_site(url)

    def get_ip(self, url: str):
        instance = Host.objects.filter(url=url).first()
        if instance:
            return instance.ip
        else:
            return None

    def add_site(self, url: str, comment: str="", ttl: int=60, ip: str='0.0.0.0'):
        if url == "" or url == "0.0.0.0":
            return

        if not Host.objects.filter(url=url).exists():
            Host.objects.create(ip=ip, url=url, ttl=ttl, comment=comment)

    def remove_site(self, url: str):
        if not Host.objects.filter(url=url).exists():
            instance = Host.objects.get(url=url)
            instance.delete()

    # TODO: add support for threads
    def import_host_files(self, path: str):
        from os import listdir
        from os.path import isfile, join
        onlyfiles = [f for f in listdir(path) if isfile(join(path, f))]
        for file in onlyfiles:
            print("File: " + file)
            with open(join(path, file), "r", encoding="utf-8") as hosts_file:
                for line in hosts_file:
                    self.add_imported_entry(line)

    def add_imported_entry(self, line: str):
        line = line.strip()
        if line.startswith("#"):
            return

        line = re.sub('[\t+]', '', line)
        line = re.sub('#', ' ', line)

        columns = line.split(' ')
        columns_nr = len(columns)
        url = columns[1] if columns_nr > 1 else None

        if url is not None:
            if self.get_ip(url) is not None:
                return

        if columns_nr > 2:
            self.add_site(url=url, comment=' '.join(columns[2:columns_nr]), ttl=999)
        elif columns_nr > 1:
            self.add_site(url, ttl=999)

    def start_ttl_monitoring(self):
        self.threads.append(Thread(target=self.monitor_ttl))
        self.threads[0].start()

    def monitor_ttl(self):
        print("Monitor started ...")
        while self.do_monitor_ttl:
            # select all non blocked urls
            query = Host.objects.order_by('ttl').filter(ttl__lt=999).all()
            for item in query:
                if item.ttl <= 0:
                    self.remove_site(item.url)
                else:
                    item.ttl -= 1

            # wait one minute for next update
            sleep(60)

    @staticmethod
    def generate_host_file(output_path: str):
        all_entries = Host.objects.all()
        with open(output_path, "w", encoding="utf-8") as hosts_file:
            for host in all_entries:
                hosts_file.write(host.ip + " " + host.url + "\n")
