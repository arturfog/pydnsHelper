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

# based on https://github.com/samuelcolvin/dnserver
from . import dnsmanager

import logging
import os
import signal
from datetime import datetime
from textwrap import wrap
from time import sleep

from dnslib import DNSLabel, QTYPE, RR, dns
from dnslib.proxy import ProxyResolver
from dnslib.server import DNSServer
from django.db.models import F

from django.db import IntegrityError, transaction

from webui.models import Logs
from webui.models import Stats, Client, StatsHosts
from concurrent.futures import ThreadPoolExecutor

SERIAL_NO = int((datetime.utcnow() - datetime(1970, 1, 1)).total_seconds())

TYPE_LOOKUP = {
    'A': (dns.A, QTYPE.A),
    'AAAA': (dns.AAAA, QTYPE.AAAA),
    'CAA': (dns.CAA, QTYPE.CAA),
    'CNAME': (dns.CNAME, QTYPE.CNAME),
    'DNSKEY': (dns.DNSKEY, QTYPE.DNSKEY),
    'MX': (dns.MX, QTYPE.MX),
    'NAPTR': (dns.NAPTR, QTYPE.NAPTR),
    'NS': (dns.NS, QTYPE.NS),
    'PTR': (dns.PTR, QTYPE.PTR),
    'RRSIG': (dns.RRSIG, QTYPE.RRSIG),
    'SOA': (dns.SOA, QTYPE.SOA),
    'SRV': (dns.SRV, QTYPE.SRV),
    'TXT': (dns.TXT, QTYPE.TXT),
    'SPF': (dns.TXT, QTYPE.TXT),
}

class Resolver(ProxyResolver):
    executor = ThreadPoolExecutor(max_workers=5)
    stats_cache = []

    def __init__(self, upstream):
        super().__init__(upstream, 53, 5)
        self.gdns = dnsmanager.SecureDNSGoogle()
        self.cdns = dnsmanager.SecureDNSCloudflare()
        self.quad9 = dnsmanager.SecureQuad9()

        self.dns_to_use = 0
        self.dns_servers = [self.gdns, self.cdns, self.quad9]

    @staticmethod
    def get_or_none(classmodel, **kwargs):
        try:
            return classmodel.objects.get(**kwargs)
        except classmodel.DoesNotExist:
            return None

    @staticmethod
    def log_stats(hostname: str, ip: str) -> None:
        print("log_stats: " + str(len(Resolver.stats_cache)))
        host = Resolver.get_or_none(StatsHosts,host=hostname)
        client = Resolver.get_or_none(Client,ip=ip)
        
        try:
            if client is None:
                client = Client.objects.create(ip=ip, mac='00:00:00:00:00:00')
            if len(Resolver.stats_cache) >= 10:
                with transaction.atomic():
                    #
                    Resolver.stats_cache.append([hostname, client])
                    #
                    for item in Resolver.stats_cache:
                        host = Resolver.get_or_none(StatsHosts,host=item[0])
                        if host is None:
                            host = StatsHosts.objects.create(host=item[0])
                        else:
                            StatsHosts.objects.filter(host=item[0]).update(hits=F('hits')+1)
                        Stats.objects.create(host=host, client=item[1])    
                Resolver.stats_cache = []
            else:
                Resolver.stats_cache.append([hostname, client])
        except Exception as e:
            Resolver.stats_cache = []
            print(e)

    def change_server(self):
        self.dns_to_use += 1
        # switching between dns servers
        if self.dns_to_use >= len(self.dns_servers):
            self.dns_to_use = 0

    def handle_ipv4(self, domain: str, record):
        record.add_question(dns.DNSQuestion(domain,qtype=1))
        ip = dnsmanager.SecureDNS.get_ip_from_cache(domain)
        if ip is None:
            ip = self.dns_servers[self.dns_to_use].resolveIPV4(domain)
        
        # try again
        if ip is None:
            self.change_server()
            ip = self.dns_servers[self.dns_to_use].resolveIPV4(domain)
        
        # many servers
        if ip is not None and len(ip) > 0:
            for ans in ip:
                a = dns.A(ans)
                record.add_answer(RR(domain, QTYPE.A, ttl=360, rdata=a))
        # 
        if ip is None:
            dnsmanager.SecureDNS.add_url_to_cache(domain, "0.0.0.0")
            print("@@@@@@ Failed ipv4 query for " + domain)
        self.change_server()

    def handle_ipv6(self, domain:str, record):
        record.add_question(dns.DNSQuestion(domain,qtype=28))
        cached_ip = dnsmanager.SecureDNS.get_ip_from_cache6(domain)
        if cached_ip is None:
            ip = self.dns_servers[self.dns_to_use].resolveIPV6(domain)
            print("ip6 #1: " + repr(ip))
        else:
            ip = [cached_ip, 28]
        # many servers
        if ip is not None and len(ip[0]) > 0 and ip[0] is not None:
            # check response type
            if ip[1] == 28:
                print("ip6: " + repr(ip[0]))
                for ans in ip[0]:
                    aaaa = dns.AAAA(ans)
                    record.add_answer(RR(domain, QTYPE.AAAA, ttl=360, rdata=aaaa))
            if ip[1] == 6:
                x = ip[0][0].split(" ")
                # TODO: clean up
                aaaa = dns.SOA(mname=x[0], rname=x[1], times=( int(x[2]), int(x[3]), int(x[4]), int(x[5]), int(x[6])) ) 
                record.add_auth(RR(domain, QTYPE.SOA, ttl=60, rdata=aaaa))
        
        if ip is None:
            print("@@@@@@@ Failed ipv6 query for " + domain)
        self.change_server()

    def resolve(self, request, handler):
        #print("Type: " + repr(request))
        domain = str(request.q.qname)
               
        if request.q.qtype == 65:
            request.q.qtype = 1
        type_name = QTYPE[request.q.qtype]

        #print(repr(request.header))
        d = dns.DNSRecord()
        d.header = request.header
        d.header.set_qr(1)
        d.header.set_ra(1)

        #print("Type: " + type_name)

        if "_http._tcp." in domain:
                domain = domain.replace("_http._tcp.", "")

        if type_name == 'A':
            self.handle_ipv4(domain, d)
            Resolver.executor.submit(Resolver.log_stats, domain, handler.client_address[0])
            return d
        elif type_name == 'AAAA':
            self.handle_ipv6(domain, d)
            Resolver.executor.submit(Resolver.log_stats, domain, handler.client_address[0])
            return d
        else:
            #print(repr(request.q))
            # resolve using normal DNS
            ret = super().resolve(request, handler)
            return ret
       


def handle_sig(signum, frame):
    msg = 'pid=%d, got signal: %s, stopping...'.format(os.getpid(), signal.Signals(signum).name)
    Logs.objects.create(msg=msg)
    exit(0)


class SecureDNSServer:
    static_udp_server = None

    @staticmethod
    def start():
        #signal.signal(signal.SIGTERM, handle_sig)

        port = int(os.getenv('PORT', 5053))
        upstream = os.getenv('UPSTREAM', '8.8.8.8')
        resolver = Resolver(upstream)
        SecureDNSServer.static_udp_server = DNSServer(resolver, port=port)
        tcp_server = DNSServer(resolver, port=port, tcp=True)

        msg = 'starting DNS server on port {}, upstream DNS server {}'.format(port, upstream)
        Logs.objects.create(msg=msg)

        SecureDNSServer.static_udp_server.start_thread()
        sleep(1)
        tcp_server.start_thread()
        sleep(1)

    def stop():
        pass

    def isRunning():
        if SecureDNSServer.static_udp_server is None:
            return False
        try:
            return SecureDNSServer.static_udp_server.isAlive()
        except Exception as e:
            return False
