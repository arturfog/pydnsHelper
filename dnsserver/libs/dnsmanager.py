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
import random
import requests

from . import hosts_manager
import getdns
from urllib3.util import connection

from webui.models import Logs
from webui.models import Host
from webui.models import Traffic
from django.db.models import F
from django.core.exceptions import ObjectDoesNotExist

from multiprocessing import Lock
from concurrent.futures import ThreadPoolExecutor
import datetime


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
NX_DOMAIN = 3 # domain does not exists


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
    hostname = DNSSEC.resolveIPv4(host) # your_dns_resolver(host)

    print("host: " + host)
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

        if is_secure:
            return addresses
        else:
            return None

    @staticmethod
    def resolveIPv4(domain: str):
        ip = SecureDNS.get_ip_from_cache(domain)
        if ip is not None:
            ip = ip.replace("'", "")
            ip = ip.replace("[", "")
            ip = ip.replace("]", "")
            ip = ip.replace(" ", "")
            return ip.split(",")

        adresses_ipv4 = []
        adresses = DNSSEC.resolve(domain)
        if adresses is None:
            return None

        for addr in adresses:
            if "." in addr:
                adresses_ipv4.append(addr)

        SecureDNS.add_url_to_cache(url=domain, ttl=100, ip=adresses_ipv4)
        return adresses_ipv4

    @staticmethod
    def resolveIPv6(domain: str):
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
    executor = ThreadPoolExecutor(max_workers=20)

    @staticmethod
    def prepare_hostname(hostname: str):
        '''verify the hostname is well-formed'''
        hostname = hostname.rstrip('.')  # strip trailing dot if present

        if not(1 <= len(hostname) <= 253):  # test length of hostname
            raise InvalidHostName

        for label in hostname.split('.'):  # test length of each label
            if not(1 <= len(label) <= 63):
                raise InvalidHostName
        try:
            return hostname.encode('ascii')
        except UnicodeEncodeError:
            raise InvalidHostName

    @staticmethod
    def add_url_to_cache_func(url: str, ip: str, ttl: int):
        msg = 'adding url ipv4: {}, with ip: {} to cache'.format(url, ip)
        SecureDNS.lock.acquire()
        try:
            #print("^^^^^^^^^^^^ Adding ipv4: " + url + " to cache")
            hosts_manager.HostsManager.add_site(url=url, ip=ip)
            Logs.objects.create(msg=msg)
            SecureDNS.lock.release()
        except:
            SecureDNS.lock.release()
        

    @staticmethod
    def add_url_to_cache_func6(url: str, ip: str, ttl: int):
        msg = 'adding url ipv6: {}, with ip: {} to cache'.format(url, ip)
        SecureDNS.lock.acquire()
        try:
            #print("^^^^^^^^^^^^^ Adding ipv6: " + url + " to cache")
            hosts_manager.HostsManager.add_site(url=url, ipv6=ip)
            Logs.objects.create(msg=msg)
            SecureDNS.lock.release()
        except:
            SecureDNS.lock.release()

    @staticmethod
    def add_url_to_cache(url: str, ip: str, ttl: int):
        #print("&&&&&&&&&&&&& Adding ipv4: " + url + " to cache")
        SecureDNS.executor.submit(SecureDNS.add_url_to_cache_func, url, ip, ttl)

    @staticmethod
    def add_url_to_cache6(url: str, ipv6: str, ttl: int):
        #print("&&&&&&&&&&&&& Adding ipv6: " + url + " to cache")
        SecureDNS.executor.submit(SecureDNS.add_url_to_cache_func6, url, ipv6, ttl)

    @staticmethod
    def log_traffic(hostname: str):
        SecureDNS.lock.acquire()
        Host.objects.filter(url = hostname).update(hits = F('hits')+1)
        Traffic.objects.get_or_create(date = datetime.date.today())
        Traffic.objects.filter(date = datetime.date.today()).update(hits = F('hits')+1)
        SecureDNS.lock.release()


    @staticmethod
    def get_ip(url: str):
      try:
          instance = Host.objects.get(url=url)
          if(instance.ipv4 == "0.0.0.0" and instance.ttl != 999):
              return None 
          return instance.ipv4
      except ObjectDoesNotExist:
          return None

    @staticmethod
    def get_ipv6(url: str):
        try:
          instance = Host.objects.get(url=url)
          if(instance.ipv6 == "::0" and instance.ttl != 999):
            return None
          return instance.ipv6
        except ObjectDoesNotExist:
          return None

    @staticmethod
    def get_ip_from_cache(hostname: str):
        ip = SecureDNS.get_ip(hostname)
        if ip is not None:
            print("Getting ipv4 [" + ip + "] for: " + hostname + " from cache")
            #SecureDNS.executor.submit(SecureDNS.log_traffic, hostname)
            return ip

        return None

    @staticmethod
    def get_ipv6_from_cache(hostname: str):
        ip = SecureDNS.get_ipv6(hostname)
        if ip is not None:
            print("Getting ipv6 [" + ip + "] for: " + hostname + " from cache")
            #SecureDNS.executor.submit(SecureDNS.log_traffic, hostname)
            return ip

        return None


    @staticmethod
    def generate_padding():
        '''generate a pad using unreserved chars'''
        pad_len = random.randint(10, 50)
        return ''.join(random.choice(UNRESERVED_CHARS) for _ in range(pad_len))


class SecureDNSCloudflare(SecureDNS):
    def __init__(
            self,
            query_type='A',
            ct='application/dns-json'
    ):
        self.url = 'https://cloudflare-dns.com/dns-query'
        self.params = {
            'type': query_type,
            'ct': ct
        }

    def resolveIPV6(self, hostname: str):
        '''return ip address(es) of hostname'''
        #print("############## RESOLVE IPV6 " + hostname)
        tmp_hostname = hostname.replace("www.", "")
        ip = SecureDNS.get_ipv6_from_cache(tmp_hostname)
        if ip is not None:
            #print(">>>>>>>> IPv6 FOR " + hostname + " IN CACHE >>>>>>>>>>")    
            return [ip, 28]

        print(">>>>>>>> IPv6 FOR " + tmp_hostname + " NOT IN CACHE >>>>>>>>>>")
        hostname_orig = tmp_hostname
        connection.create_connection = patched_create_connection
        hostname = SecureDNS.prepare_hostname(hostname)
        self.params.update({'name': hostname})
        self.params.update({'type': 'AAAA'})

        r = requests.get(self.url, params=self.params)
        connection.create_connection = _orig_create_connection
        if r.status_code == 200:
            response = r.json()
            #print(response)
            if response['Status'] == NOERROR:
                answers = []
                if 'Authority' in response:
                    for answer in response['Authority']:
                        name, response_type, ttl, data = \
                            map(answer.get, ('name', 'type', 'TTL', 'data'))
                        answers.append(data)
                        answers.append(response_type)
                        SecureDNS.add_url_to_cache6(url=hostname_orig, ttl=ttl, ipv6="::1")
                elif 'Answer' in response:
                    for answer in response['Answer']:
                        name, response_type, ttl, data = \
                            map(answer.get, ('name', 'type', 'TTL', 'data'))
                        if response_type is AAAA:
                            answers.append(data)
                            answers.append(response_type)
                            SecureDNS.add_url_to_cache6(url=hostname_orig, ttl=ttl, ipv6=data)
                            break
                if answers is []:
                    return None
                return answers
        return None

    def resolveIPV4(self, hostname: str):
        '''return ip address(es) of hostname'''
        tmp_hostname = hostname.replace("www.", "")
        ip = SecureDNS.get_ip_from_cache(tmp_hostname)
        if ip is not None:
            return [ip]

        print(">>>>>>>> IPv4 FOR " + tmp_hostname + " NOT IN CACHE >>>>>>>>>>")
        hostname_orig = tmp_hostname

        connection.create_connection = patched_create_connection
        hostname = SecureDNS.prepare_hostname(hostname)
        self.params.update({'name': hostname})

        r = requests.get(self.url, params=self.params)
        connection.create_connection = _orig_create_connection
        if r.status_code == 200:
            response = r.json()
            #print(response)
            if response['Status'] == NOERROR:
                answers = []
                if 'Answer' in response:
                    for answer in response['Answer']:
                        name, response_type, ttl, data = \
                            map(answer.get, ('name', 'type', 'TTL', 'data'))
                        if response_type is A:
                            answers.append(data)
                            SecureDNS.add_url_to_cache(url=hostname_orig, ttl=int(ttl), ip=data)
                            break
                if answers is []:
                    return None
                return answers
        return None


class SecureDNSGoogle(SecureDNS):
    '''Resolve domains using Google's Public DNS-over-HTTPS API'''
    def __init__(
        self,
        query_type=1,
        cd=False,
        edns_client_subnet='0.0.0.0/0',
        random_padding=True,
    ):
        self.url = 'https://dns.google.com/resolve'
        self.params = {
            'type': query_type,
            'cd': cd,
            'edns_client_subnet': edns_client_subnet,
            'random_padding': random_padding,
        }

    def resolve(self, hostname: str):
        '''return ip address(es) of hostname'''

        connection.create_connection = patched_create_connection
        hostname = self.prepare_hostname(hostname)
        self.params.update({'name': hostname})

        if self.params['random_padding']:
            padding = SecureDNS.generate_padding()
            self.params.update({'random_padding': padding})

        r = requests.get(self.url, params=self.params)
        connection.create_connection = _orig_create_connection
        if r.status_code == 200:
            response = r.json()
            print(response)
            if response['Status'] == NOERROR:
                answers = []
                if 'Answer' in response:
                    for answer in response['Answer']:
                        name, response_type, ttl, data = \
                            map(answer.get, ('name', 'type', 'ttl', 'data'))
                        if response_type in (A, AAAA):
                            answers.append(data)
                            SecureDNS.add_url_to_cache(url=hostname, ttl=int(ttl), ip=data)
                if answers is []:
                    return None
                return answers
        return None


