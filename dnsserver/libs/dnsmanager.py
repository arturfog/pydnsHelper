#!/usr/bin/env python
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
from io import BytesIO
import random
from django.utils import timezone
import requests

from . import hosts_manager
import getdns
from urllib3.util import connection
from webui.models import Logs
from django.db.models import F
from django.core.exceptions import ObjectDoesNotExist
from multiprocessing import Lock
from concurrent.futures import ThreadPoolExecutor
import datetime
import time
from webui.models import IPv4
import timeit
import pycurl
from io import BytesIO

__version__ = '0.0.2'

# cloudflare
# https://developers.cloudflare.com/1.1.1.1/dns-over-https/request-structure/
# curl 'https://cloudflare-dns.com/dns-query?ct=application/dns-json&name=google.com&type=A'
# - https://1.1.1.1/dns-query
# - https://1.0.0.1/dns-query
# google
# https://developers.google.com/speed/public-dns/docs/dns-over-https
# - https://dns.google.com/resolve

# domain to test dnssec verification: dnssec-failed.org

# response fields
# AD
# If true, it means that every record in the answer was verified with DNSSEC.
# CD
# If true, the client asked to disable DNSSEC validation.
# In this case, Cloudflare will still fetch the DNSSEC-related records, but it will not attempt to validate the records.

# Resource Record Types
A = 1
AAAA = 28
# DNS status codes
NOERROR = 0
FORMAT_ERROR = 1
SERVER_FAIL = 2
NX_DOMAIN = 3  # domain does not exists


UNRESERVED_CHARS = 'abcdefghijklmnopqrstuvwxyz' \
                   'ABCDEFGHIJKLMNOPQRSTUVWXYZ' \
                   '0123456789-._~'


class InvalidHostName(Exception):
    pass


_orig_create_connection = connection.create_connection


def patched_create_connection(address, *args, **kwargs):
    """Wrap urllib3's create_connection to resolve the name elsewhere"""
    # resolve hostname to an ip address; use your own
    # resolver here, as otherwise the system resolver will be used.
    host, port = address
    hostname = DNSSEC.resolveIPv4(host)  # your_dns_resolver(host)

    print("resolving host using standard dns: " + host)
    if hostname is not None and len(hostname) > 1:
        hostname = hostname[0]
    return _orig_create_connection((hostname, port), *args, **kwargs)


class DNSSEC():
    dnssec_status = {
        "DNSSEC_SECURE": 400,
        "DNSSEC_BOGUS": 401,
        "DNSSEC_INDETERINATE": 402,
        "DNSSEC_INSECURE": 403,
        "DNSSEC_NOT_PERFORMED": 404
    }

    @staticmethod
    def gen_message(value):
        for message in DNSSEC.dnssec_status.keys():
            if DNSSEC.dnssec_status[message] == value:
                return message

    @staticmethod
    def resolve_dnssec(domain: str):
        ctx = getdns.Context()
        extensions = {"return_both_v4_and_v6":
                          getdns.EXTENSION_TRUE,
                      "dnssec_return_status":
                          getdns.EXTENSION_TRUE}
        results = ctx.address(name=domain,
                              extensions=extensions)

        adresses = []
        statuses = []
        if results.status == getdns.RESPSTATUS_GOOD:
            for addr in results.just_address_answers:
                adresses.append(addr["address_data"])

            for result in results.replies_tree:
                if "dnssec_status" in result.keys():
                    if results.status != getdns.RESPSTATUS_NO_NAME:
                        statuses.append(result["dnssec_status"])

            return adresses, statuses

    @staticmethod
    def resolve(domain: str):
        addresses, statuses = DNSSEC.resolve_dnssec(domain)
        is_secure = True

        for status in statuses:
            if status != DNSSEC.dnssec_status["DNSSEC_SECURE"]:
                is_secure = False

        # hack for google
        if is_secure == False:
            if domain == "dns.google.com" or domain == "dns.quad9.net":
                is_secure = True
        if is_secure:
            return addresses
        else:
            return None

    @staticmethod
    def resolveIPv4(domain: str):
        adresses_ipv4 = []
        adresses = DNSSEC.resolve(domain)
        if adresses is None:
            return None

        for addr in adresses:
            if "." in addr:
                adresses_ipv4.append(addr)

        SecureDNS.add_url_to_cache(url=domain, ip=adresses_ipv4)
        return adresses_ipv4

    @staticmethod
    def resolveIPv6(domain: str):
        # ip = SecureDNS.get_ip_from_cache6(domain)
        adresses = DNSSEC.resolve(domain)
        if adresses is None:
            return None
        adresses_ipv6 = []
        for addr in adresses:
            if ":" in addr:
                adresses_ipv6.append(addr)

        print(adresses_ipv6)
        return adresses_ipv6


class SecureDNS(object):
    lock = Lock()
    executor = ThreadPoolExecutor(max_workers=5)
    ram_cache = {}
    ram_cache6 = {}
    cache_created = time.time()
    session = requests.Session()

    @staticmethod
    def add_to_ram_cache4(url: str, ip):
        if len(SecureDNS.ram_cache) < 2000:
            if (time.time() - SecureDNS.cache_created) < 7200:
                if url not in SecureDNS.ram_cache:
                    print("Adding ipv4 : " + url + " to RAM cache (" +
                          str(len(SecureDNS.ram_cache)) + ")")
                    SecureDNS.ram_cache[url] = ip
            else:
                SecureDNS.ram_cache.clear()
                SecureDNS.cache_created = time.time()
        else:
            SecureDNS.ram_cache.clear()
            SecureDNS.cache_created = time.time()

    @staticmethod
    def add_to_ram_cache6(url: str, ip):
        if len(SecureDNS.ram_cache6) < 2000:
            if (time.time() - SecureDNS.cache_created) < 7200:
                if url not in SecureDNS.ram_cache6:
                    print("Adding ipv6 : " + url + " to RAM cache (" +
                          str(len(SecureDNS.ram_cache6)) + ")")
                    SecureDNS.ram_cache6[url] = ip
            else:
                SecureDNS.ram_cache6.clear()
                SecureDNS.cache_created = time.time()
        else:
            SecureDNS.ram_cache6.clear()
            SecureDNS.cache_created = time.time()


    @staticmethod
    def get_ip_from_ram_cache4(url: str):
        if url in SecureDNS.ram_cache:
            print("Getting ipv4 for: " + url +
                  " from RAM cache (" + str(len(SecureDNS.ram_cache)) + ")")
            return SecureDNS.ram_cache[url]
        return None

    @staticmethod
    def get_ip_from_ram_cache6(url: str):
        if url in SecureDNS.ram_cache6:
            print("Getting ipv6 for: " + url +
                  " from RAM cache (" + str(len(SecureDNS.ram_cache6)) + ")")
            return SecureDNS.ram_cache6[url]
        return None

    @staticmethod
    def prepare_hostname(hostname: str) -> str:
        '''verify the hostname is well-formed'''
        hostname = hostname.rstrip('.')  # strip trailing dot if present

        if not(1 <= len(hostname) <= 253):  # test length of hostname
            raise InvalidHostName

        for label in hostname.split('.'):  # test length of each label
            if not(1 <= len(label) <= 63):
                raise InvalidHostName

        return hostname
        

    @staticmethod
    def add_url_to_cache_func(url: str, ip: str):
        SecureDNS.lock.acquire()
        try:
            hosts_manager.HostsManager.add_site(url=url, ip=ip)
            SecureDNS.lock.release()
        except:
            SecureDNS.lock.release()

    @staticmethod
    def add_url_to_cache_func6(url: str, ip: str):
        SecureDNS.lock.acquire()
        try:
            hosts_manager.HostsManager.add_site(url=url, ipv6=ip)            
            SecureDNS.lock.release()
        except:
            SecureDNS.lock.release()

    @staticmethod
    def add_url_to_cache(url: str, ip: str):
        print("&&&&&&&&&&&&& Adding ipv4: " + url + " to cache, ip: " + str(ip))
        SecureDNS.executor.submit(
            SecureDNS.add_url_to_cache_func, url, ip)
        #SecureDNS.add_to_ram_cache4(url, ip)

    @staticmethod
    def add_url_to_cache6(url: str, ipv6: str):
        print("&&&&&&&&&&&&& Adding ipv6: " + url + " to cache")
        SecureDNS.executor.submit(
            SecureDNS.add_url_to_cache_func6, url, ipv6)

    @staticmethod
    def get_ip_from_cache(hostname: str):
        ip = SecureDNS.get_ip_from_ram_cache4(hostname)
        if ip is not None:
            return ip
        _, ip = hosts_manager.HostsManager.get_ip_all(hostname)
        if ip is not None:
            SecureDNS.add_to_ram_cache4(hostname, ip)
            print("Getting ipv4 [" + str(ip) + "] for: " + hostname + " from cache")
            return ip
        return None

    @staticmethod
    def get_ip_from_cache6(hostname: str):
        ip = SecureDNS.get_ip_from_ram_cache6(hostname)
        if ip is not None:
            return ip
        _, ip = hosts_manager.HostsManager.get_ipv6_all(hostname)
        if ip is not None:
            SecureDNS.add_to_ram_cache6(hostname, ip)
            print("Getting ipv6 [" + str(ip) + "] for: " + hostname + " from cache")
            return ip
        return None

    @staticmethod
    def generate_padding():
        '''generate a pad using unreserved chars'''
        pad_len = random.randint(10, 50)
        return ''.join(random.choice(UNRESERVED_CHARS) for _ in range(pad_len))

    def resolveIPV6(self, hostname: str):
        b = BytesIO()
        c = pycurl.Curl()
        '''return ip address(es) of hostname'''
        tmp_hostname = hostname # hostname.replace("www.", "")

        print(">>>>>>>> IPv6 FOR " + tmp_hostname + " NOT IN CACHE >>>>>>>>>>")
        hostname_orig = tmp_hostname

        connection.create_connection = patched_create_connection
        hostname = SecureDNS.prepare_hostname(hostname)

        self.params.update({'type': 'AAAA'})

        if self.provider_name == "google" and self.params['random_padding']:
            padding = SecureDNS.generate_padding()
            self.params.update({'random_padding': padding})

        connection.create_connection = patched_create_connection
        hostname = SecureDNS.prepare_hostname(hostname)
        #
        params_str = ""
        for i in self.params:
            params_str += "&"+ i + "=" + str(self.params[i])
        c.setopt(c.URL, self.url+"?name=" + str(hostname) + params_str)
        c.setopt(c.WRITEDATA, b)
        c.setopt(c.TIMEOUT, 3)
        c.perform()
        #
        connection.create_connection = _orig_create_connection

        if c.getinfo(pycurl.HTTP_CODE) == 200:
            c.close()
            response_str = b.getvalue()
            import json
            response = json.loads(response_str)
            print(response)
            if response['Status'] == NOERROR:
                answers = []
                type = None
                if 'Authority' in response:
                    for answer in response['Authority']:
                        name, response_type, ttl, data = \
                            map(answer.get, ('name', 'type', 'TTL', 'data'))
                        answers.append(data)
                        type = response_type
                        SecureDNS.add_url_to_cache6(url=hostname_orig, ipv6="::1")        
                elif 'Answer' in response:
                    for answer in response['Answer']:
                        name, response_type, ttl, data = \
                            map(answer.get, ('name', 'type', 'TTL', 'data'))
                        if response_type is AAAA:
                            answers.append(data)
                            type = response_type
                            SecureDNS.add_url_to_cache6(url=hostname_orig, ipv6=data)
                if answers is []:
                    return None
                return [answers, type]
        #
        c.close()
        return None

    def resolveIPV4(self, hostname: str):
        '''return ip address(es) of hostname'''
        b = BytesIO()
        c = pycurl.Curl()

        tmp_hostname = hostname # hostname.replace("www.", "")
        if tmp_hostname not in self.pending_requests_4:
            print(">>>>>>>> [" + self.provider_name + "] IPv4 FOR " + tmp_hostname + " NOT IN CACHE >>>>>>>>>>")
            self.pending_requests_4.append(tmp_hostname)
        else:
            # wait 5 seconds for response
            for i in range(5):
                time.sleep(1)
                print(">>>>>>>> [" + self.provider_name + "]  IPv4 FOR " + tmp_hostname + " NOT IN CACHE >>>>>> WAITING (" + str(i) + ") >>>>")
                ip = SecureDNS.get_ip_from_cache(tmp_hostname)
                if ip is not None:
                    if tmp_hostname in self.pending_requests_4:
                        self.pending_requests_4.remove(tmp_hostname)
                    return ip

            if tmp_hostname in self.pending_requests_4:
                self.pending_requests_4.remove(tmp_hostname)
            return None

        hostname_orig = tmp_hostname

        connection.create_connection = patched_create_connection
        hostname = SecureDNS.prepare_hostname(hostname)
        #
        params_str = ""
        for i in self.params:
            params_str += "&"+ i + "=" + str(self.params[i])
        c.setopt(c.URL, self.url+"?name=" + str(hostname) + params_str)
        c.setopt(c.WRITEDATA, b)
        c.setopt(c.TIMEOUT, 3)
        c.perform()
        #
        connection.create_connection = _orig_create_connection

        if c.getinfo(pycurl.HTTP_CODE) == 200:
            c.close()
            response_str = b.getvalue()
            import json
            response = json.loads(response_str)
            print(response)
            if response['Status'] == NOERROR:
                answers = []
                if 'Answer' in response:
                    for answer in response['Answer']:
                        name, response_type, ttl, data = \
                            map(answer.get, self.response_keys)
                        if response_type is A:
                            answers.append(data)
                            SecureDNS.add_url_to_cache(url=hostname_orig, ip=data)
                if tmp_hostname in self.pending_requests_4:
                    self.pending_requests_4.remove(tmp_hostname)
                if answers is []:    
                    return None
                return answers
        #
        if tmp_hostname in self.pending_requests_4:
            self.pending_requests_4.remove(tmp_hostname)
        #
        c.close()
        return None

# curl -vk "https://dns-querycloudflare-dns.com/dns-query?ct=application/dns-json&type=1&name=facebook.com"
class SecureDNSCloudflare(SecureDNS):
    def __init__(
            self
    ):
        self.url: str = 'https://cloudflare-dns.com/dns-query'
        self.params = {
            'ct': 'application/dns-json',
            'type': 1
        }
        self.provider_name = "cloudflare"
        self.response_keys = ('name', 'type', 'TTL', 'data')
        self.pending_requests_4 = []
        self.pending_requests_6 = []


class SecureDNSGoogle(SecureDNS):
    '''Resolve domains using Google's Public DNS-over-HTTPS API'''
    def __init__(
        self
    ):
        self.url: str = 'https://dns.google.com/resolve'
        self.params = {
            'type': 1,
            'cd': False,
            'edns_client_subnet': '0.0.0.0/0',
            'random_padding': False,
        }
        self.provider_name = "google"
        self.response_keys = ('name', 'type', 'TTL', 'data')
        self.pending_requests_4 = []
        self.pending_requests_6 = []

# curl -vk "https://dns.quad9.net:5053/dns-query?ct=application/dns-json&type=1&name=facebook.com"
class SecureQuad9(SecureDNS):
    '''Resolve domains using Quad9 Public DNS-over-HTTPS API'''
    def __init__(
        self
    ):
        self.url: str = 'https://dns.quad9.net:5053/dns-query'
        self.params = {
            'type': 1,
            'cd': False
        }
        self.provider_name = "quad9"
        self.response_keys = ('name', 'type', 'TTL', 'data')
        self.pending_requests_4 = []
        self.pending_requests_6 = []
