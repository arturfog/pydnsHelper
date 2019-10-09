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
from django.utils import timezone
from webui.models import Host
from django.db import IntegrityError, transaction

from webui.models import Logs

class HostsManager:
    ttlThreadRunning = False
    def __init__(self):
        self.eng = None
        self.conn = None
        self.session = None
        self.threads = []
        self.do_monitor_ttl = True
        self.enable_debug = False

    @staticmethod
    def block_site(url: str):
        HostsManager.remove_site(url)
        HostsManager.add_site(url=url, ttl=999)

    @staticmethod
    def unblock_site(url: str):
        HostsManager.remove_site(url)

    @staticmethod
    def get_ip(url: str):
        instance = Host.objects.filter(url=url).first()
        if instance:
            if(instance.ipv4 == "0.0.0.0" and instance.ttl != 999):
                return None

            return instance.ipv4
        else:
            return None

    @staticmethod
    def get_ipv6(url: str):
        instance = Host.objects.filter(url=url).first()
        if instance:
            if(instance.ipv6 == "::0" and instance.ttl != 999):
                return None

            return instance.ipv6
        else:
            return None

    @staticmethod
    def add_site(url: str, comment: str="", ttl: int=920, ip: str="0.0.0.0", ipv6: str="::0"):        
        if url == "" or url == "0.0.0.0":
            return

        try: 
            obj = Host.objects.filter(url=url).first()
            if not obj:
                if __debug__: print("!!!!!!!!!!!!!! 1 add_site url: [" + url + "] ip: " + ip + " ipv6: " + ipv6 + " ttl:" + str(ttl) + " comment: [" + comment + "]")
                Host.objects.create(ipv4=ip, ipv6=ipv6, url=url, ttl=ttl, comment=comment, hits=0, created=timezone.now())
            else:
                if(ipv6 != "::0"):
                    if __debug__: print("!!!!!!!!!!!!!! 2 add_site url: [" + url + "] ipv6: " + ipv6)
                    Host.objects.filter(url=url).update(ipv6=ipv6)
                elif(ip != "0.0.0.0"):
                    if __debug__: print("!!!!!!!!!!!!!! 3 add_site url: [" + url + "] ip: " + ip)
                    Host.objects.filter(url=url).update(ipv4=ip)
        except UnicodeEncodeError:
            return


    @staticmethod
    def remove_site(url: str):
        if not Host.objects.filter(url=url).exists():
            instance = Host.objects.get(url=url)
            instance.delete()

    # TODO: add support for threads
    def import_host_files(self, path: str):
        from os import listdir
        from os.path import isfile, join
        onlyfiles = [f for f in listdir(path) if isfile(join(path, f))]
        for file in onlyfiles:
            if __debug__: print("File: " + file)
            with open(join(path, file), "r", encoding="utf-8") as hosts_file:
                with transaction.atomic():
                    for line in hosts_file:
                        HostsManager.add_imported_entry(line)

    @staticmethod
    def add_imported_entry(line: str):
        line = line.strip()
        if line.startswith("#"):
            return

        line = re.sub('[\t+]', '', line)
        line = re.sub('#', ' ', line)

        columns = line.split(' ')
        columns_nr = len(columns)
        url = columns[1] if columns_nr > 1 else None

        if url is not None:
            if HostsManager.get_ip(url) is not None:
                return
        
        if url is not None:
            url = url + "."
            if columns_nr > 2:
                HostsManager.add_site(url=url, comment=' '.join(columns[2:columns_nr]), ttl=999)
            elif columns_nr > 1:
                HostsManager.add_site(url=url, ttl=999)

    def start_ttl_monitoring(self):
        self.threads.append(Thread(target=self.monitor_ttl))
        self.threads[0].start()

    @staticmethod
    def isTTLThreadRunning():
        return HostsManager.ttlThreadRunning

    def monitor_ttl(self):
        msg = 'Monitor started ...'
        Logs.objects.create(msg=msg)
        HostsManager.ttlThreadRunning = True
        while self.do_monitor_ttl:
            # select all non blocked urls
            query = Host.objects.order_by('ttl').filter(ttl__lt=999).all()
            now = timezone.now()
            for item in query:
                #
                diff = now - item.created
                minutes = int(diff.seconds/60)
                #
                if item.ttl - minutes <= 0:
                    self.remove_site(item.url)
            # wait ten minutes for next update
            sleep(600)

    @staticmethod
    def generate_host_file(output_path: str):
        all_entries = Host.objects.all()
        with open(output_path, "w", encoding="utf-8") as hosts_file:
            for host in all_entries:
                hosts_file.write(host.ipv4 + " " + host.url + "\n")
