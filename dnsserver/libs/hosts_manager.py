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
from webui.models import Host, IPv4, IPv6
from django.db import IntegrityError, transaction
from multiprocessing import Lock
import random
from webui.models import Logs

class HostsManager:
    ttlThreadRunning = False
    lock = Lock()
    def __init__(self):
        self.eng = None
        self.conn = None
        self.session = None
        self.threads = []
        self.do_monitor_ttl = True
        self.enable_debug = False

    @staticmethod
    def get_or_none(model, *args, **kwargs):
        try:
            return model.objects.get(*args, **kwargs)
        except model.DoesNotExist:
            return None

    @staticmethod
    def block_site(url: str):
        HostsManager.remove_site(url)
        HostsManager.add_site(url=url, ttl=-1)

    @staticmethod
    def unblock_site(url: str):
        HostsManager.remove_site(url)

    @staticmethod
    def get_ip_all(url: str):
        try:
            HostsManager.lock.acquire()
            instance = HostsManager.get_or_none(Host, url=url)
            HostsManager.lock.release()
            if instance:
                if instance.blocked == True:
                    return ["0.0.0.0"]
                query4 = IPv4.objects.filter(host=instance).all()
                if query4:
                    resp = []
                    for i in query4:
                        resp.append(i.ip)
                    return resp
                return None
            else:
                return None
        except:
            HostsManager.lock.release()

    @staticmethod
    def get_ip(url: str):
        try:
            HostsManager.lock.acquire()
            instance = HostsManager.get_or_none(Host, url=url)
            HostsManager.lock.release()
            if instance:
                if instance.blocked == True:
                    return "0.0.0.0"
                query4 = IPv4.objects.filter(host=instance).first()
                if query4:
                    return query4.ip
                return None
            else:
                return None
        except:
            HostsManager.lock.release()

    @staticmethod
    def get_ipv6_all(url: str):
        try:
            HostsManager.lock.acquire()
            instance = HostsManager.get_or_none(Host, url=url)
            HostsManager.lock.release()
            if instance:
                if instance.blocked == True:
                    return ["::0"]
                query6 = IPv6.objects.filter(host=instance).all()
                if query6:
                    resp = []
                    for i in query6:
                        resp.append(i.ip)
                    return resp
                return None
            else:
                return None
        except:
            HostsManager.lock.release()

    @staticmethod
    def get_ipv6(url: str):
        try:
            HostsManager.lock.acquire()
            instance = HostsManager.get_or_none(Host, url=url)
            HostsManager.lock.release()
            if instance:
                if instance.blocked == True:
                    return "::0"
                query6 = IPv6.objects.filter(host=instance).first()
                if query6:
                    return query6.ip
                return None
            else:
                return None
        except:
            HostsManager.lock.release()

    @staticmethod
    def add_site(url: str, comment: str="", ttl: int=7000, ip: str="0.0.0.0", ipv6: str="::0"):        
        if url == "" or url == "0.0.0.0":
            return
        try: 
            rand_ttl = ttl
            if ttl != -1:
                rand_ttl = ttl + random.randint(100,1000)
            obj = HostsManager.get_or_none(Host, url=url)
            if not obj:
                #if __debug__: print("!!!!!!!!!!!!!! [new] add_site url: [" + url + "] ip: " + ip + " ipv6: " + ipv6 + " ttl:" + str(ttl) + " comment: [" + comment + "]")
                if ttl != -1:
                    host = Host.objects.create(url=url, comment=comment,hits=0, created=timezone.now())
                    IPv4.objects.create(host=host, ip=ip, ttl=rand_ttl)
                    if ipv6 != "::0":
                        IPv6.objects.create(host=host, ip=ipv6, ttl=rand_ttl)
                else:
                    host = Host.objects.create(url=url, comment=comment,hits=0, created=timezone.now(), blocked=True)
            else:
                if obj.blocked == False:
                    if(ipv6 != "::0"):
                        if __debug__: print("!!!!!!!!!!!!!! [update ipv6] add_site url: [" + url + "] ipv6: " + ipv6)
                        IPv6.objects.create(host=obj, ip=ipv6, ttl=rand_ttl)
                    elif(ip != "0.0.0.0"):
                        if __debug__: print("!!!!!!!!!!!!!! [update ipv4] add_site url: [" + url + "] ip: " + ip)
                        IPv4.objects.create(host=obj, ip=ip, ttl=rand_ttl)
        except UnicodeEncodeError:
            return

    @staticmethod
    def remove_site(url: str):
        if Host.objects.filter(url=url).exists():
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
                        line = line.strip()
                        if not line.startswith("#"):
                            HostsManager.add_imported_entry(line)

    @staticmethod
    def add_imported_entry(line: str):
        line = re.sub('[\t+]', '', line)
        line = re.sub('#', ' ', line)

        columns = line.split(' ')
        columns_nr = len(columns)
        url = columns[1] if columns_nr > 1 else None

        if url is not None:
            if HostsManager.get_ip(url) is not None:
                return
        else:
            return
        
        url = url + "."
        if columns_nr > 2:
            HostsManager.add_site(url=url, comment=' '.join(columns[2:columns_nr]), ttl=-1)
        elif columns_nr > 1:
            HostsManager.add_site(url=url, ttl=-1)

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
            hosts = Host.objects.order_by('created').exclude(blocked=True).all()
            now = timezone.now()
            for item in hosts:
                #
                diff = now - item.created
                minutes_days = diff.days * 24 * 60
                minutes = int(diff.seconds/60)
                minutes_total = minutes_days + minutes
                #
                ip4 = IPv4.objects.order_by('ttl').filter(host__id=item.id).first()
                if ip4.ttl - minutes_total <= 0:
                    item.delete()
                if not ip4:
                    item.delete()

            query6 = IPv6.objects.order_by('ttl').exclude(ttl=-1).all()
            now = timezone.now()
            for item in query6:
                #
                diff = now - item.host.created
                minutes = int(diff.seconds/60)
                #
                if item.ttl - minutes <= 0:
                    item.delete()
            # wait ten minutes for next update
            sleep(3600)

    @staticmethod
    def generate_host_file(output_path: str):
        all_entries = Host.objects.all()
        with open(output_path, "w", encoding="utf-8") as hosts_file:
            for host in all_entries:
                ip = HostsManager.get_ip(host.url)
                hosts_file.write(ip + " " + host.url + "\n")
