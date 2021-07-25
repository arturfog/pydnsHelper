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
from django.db import IntegrityError, transaction, utils
import random
import os
import shutil
from django import db
from webui.models import Logs

class HostsManager:
    ttlThreadRunning = False
    hostsq = Host.objects.all()
    ip4q = IPv4.objects.all()
    ip6q = IPv6.objects.all()

    DB_PATH = "/tmp/db.sqlite3"
    STATS_PATH = "/tmp/stats.sqlite3"

    def __init__(self):
        self.threads = []
        self.do_monitor_ttl = True

    @staticmethod
    def get_or_none(url):
        try:
            return HostsManager.hostsq.get(url=url)
        except Host.DoesNotExist:
            return None
        except utils.OperationalError:
            db.close_old_connections()
            return None
        except db.OperationalError:
            db.close_old_connections()
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
        instance = HostsManager.get_or_none(url=url)
        if instance:
            if instance.blocked == True:
                return ["0.0.0.0"]
            query4 = HostsManager.ip4q.filter(host=instance).all()
            if query4:
                resp = []
                for i in query4:
                    resp.append(i.ip)
                return resp
        return None

    @staticmethod
    def get_ip(url: str):
        instance = HostsManager.get_or_none(url=url)
        if instance:
            if instance.blocked == True:
                return "0.0.0.0"
            query4 = HostsManager.ip4q.filter(host=instance).first()
            if query4:
                return query4.ip
        return None

    @staticmethod
    def get_ipv6_all(url: str):
        instance = HostsManager.get_or_none(url=url)
        if instance:
            if instance.blocked == True:
                return ["::0"]
            query6 = HostsManager.ip6q.filter(host=instance).all()
            if query6:
                resp = []
                for i in query6:
                    resp.append(i.ip)
                return resp
        return None

    @staticmethod
    def get_ipv6(url: str):
        instance = HostsManager.get_or_none(url=url)
        if instance:
            if instance.blocked == True:
                return "::0"
            query6 = HostsManager.ip6q.filter(host=instance).first()
            if query6:
                return query6.ip
        return None

    @staticmethod
    @transaction.atomic
    def add_site(url: str, comment: str="", ttl: int=7000, ip: str="0.0.0.0", ipv6: str="::0"):
        if url == "" or url == "0.0.0.0":
            return
        try:
            rand_ttl = ttl
            if ttl != -1:
                rand_ttl = ttl + random.randint(1,100)
            obj = HostsManager.get_or_none(url=url)
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
                        #if __debug__: print("!!!!!!!!!!!!!! [update ipv6] add_site url: [" + url + "] ipv6: " + ipv6)
                        # IPv6.objects.create(host=obj, ip=ipv6, ttl=rand_ttl)
                        IPv6.objects.filter(id=obj.id).update(ip=ipv6, last_updated=timezone.now())
                    elif(ip != "0.0.0.0"):
                        # if __debug__: print("!!!!!!!!!!!!!! [update ipv4] add_site url: [" + url + "] ip: " + ip)
                        # IPv4.objects.create(host=obj, ip=ip, ttl=rand_ttl)
                        IPv4.objects.filter(id=obj.id).update(ip=ip, last_updated=timezone.now())
        except UnicodeEncodeError:
            return

    @staticmethod
    def remove_site(url: str):
        if Host.objects.filter(url=url).exists():
            instance = Host.objects.get(url=url)
            instance.delete()

    def update_yt(self):
        from . import downloader
        import os
        yt_filter_url="https://raw.githubusercontent.com/kboghdady/youTube_ads_4_pi-hole/master/black.list"
        print("Updating youtube filter ...")
        dl = downloader.HTTPDownloader()
        if not os.path.isdir("/tmp/hosts/"):
            os.mkdir("/tmp/hosts")
        dl.download(yt_filter_url, "/tmp/hosts/yt.txt")
        self.import_host_files("/tmp/hosts/")

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
        url = None
        if columns_nr > 1:
            url = columns[1]
        elif columns_nr == 1:
            url = columns[0]

        if url is not None:
            if HostsManager.get_ip(url) is not None:
                return
        else:
            return

        url = url + "."
        if columns_nr > 2:
            HostsManager.add_site(url=url, comment=' '.join(columns[2:columns_nr]), ttl=-1)
        elif columns_nr >= 1:
            HostsManager.add_site(url=url, ttl=-1)

    def start_ttl_monitoring(self):
        self.threads.append(Thread(target=self.monitor_ttl))
        self.threads[0].start()

    def start_auto_update_hosts(self):
        self.threads.append(Thread(target=self.auto_update_hosts))
        self.threads[1].start()

    def start_auto_backup(self):
        self.threads.append(Thread(target=self.auto_backup_db))
        self.threads[2].start()

    @staticmethod
    def isTTLThreadRunning():
        return HostsManager.ttlThreadRunning

    def auto_update_hosts(self):
        from . import hosts_sources
        while self.do_monitor_ttl:
            # check if after 3am
            now = timezone.now()
            if now.hour == 3:
                msg = 'Auto hosts update ...'
                Logs.objects.create(msg=msg)
                hosts_sources.HostsSourcesUtils.clean_dl_dir()
                hosts_sources.HostsSourcesUtils.download_hosts()
                self.import_host_files("/tmp/hosts/")
                sleep(60*60)

    @staticmethod
    def restore_backup():
        print("Restoring backup ...")
        items = os.listdir("./backup")
        items.sort(reverse=True)
        newest_dir = items[0]

        if os.path.getsize(HostsManager.DB_PATH) == 0:
                print("Removing empty db")
                os.remove(HostsManager.DB_PATH)
                shutil.copy2("./backup/" + newest_dir+"/db.sqlite3", HostsManager.DB_PATH)
                shutil.copy2("./backup/" + newest_dir+"/stats.sqlite3", HostsManager.STATS_PATH)

        sleep(1)
        print("Finished restoring backup ...")

    def auto_backup_db(self):
        while self.do_monitor_ttl:
            msg = 'Auto db backup ...'
            Logs.objects.create(msg=msg)

            if not os.path.exists("./backup"):
                os.mkdir("./backup")

            now = timezone.now()
            DST_NAME = "./backup/" + str(now.day) + "_" + str(now.month) + "_" + str(now.year) + "_" + str(now.hour) + "_" + str(now.minute)
            os.mkdir(DST_NAME)

            if os.path.exists(self.DB_PATH):
                shutil.copy2(self.DB_PATH, DST_NAME)

            if os.path.exists(self.STATS_PATH):
                shutil.copy2(self.STATS_PATH, DST_NAME)

            # sleep for 12h
            sleep(12*60*60)
            
    # removes all items which expired based on ttl
    def monitor_ttl(self):
        msg = 'Monitor started ...'
        Logs.objects.create(msg=msg)
        HostsManager.ttlThreadRunning = True
        
        sleep(60)

        deleted_items = 0
        while self.do_monitor_ttl:
            # select all non blocked urls
            hosts = HostsManager.hostsq.exclude(blocked=True).order_by('created').all()
            now = timezone.now()
            with transaction.atomic():
                for item in hosts:
                #
                    diff = now - item.created
                    minutes_days = diff.days * 24 * 60
                    minutes = int(diff.seconds/60)
                    minutes_total = minutes_days + minutes
                    #
                    ip4 = HostsManager.ip4q.order_by('ttl').filter(host__id=item.id).first()
                    if ip4.ttl - minutes_total <= 0:
                        item.delete()
                        deleted_items += 1
                    if not ip4:
                        item.delete()
            db.close_old_connections()
            
            # wait ten minutes for next update
            sleep(7200)
            
            msg = "TTL removed items: " + str(deleted_items)
            Logs.objects.create(msg=msg)
            deleted_items = 0

    @staticmethod
    def generate_host_file(output_path: str):
        all_entries = Host.objects.all()
        with open(output_path, "w", encoding="utf-8") as hosts_file:
            for host in all_entries:
                ip = HostsManager.get_ip(host.url)
                hosts_file.write(ip + " " + host.url + "\n")
