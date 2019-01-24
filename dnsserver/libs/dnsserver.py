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


SERIAL_NO = int((datetime.utcnow() - datetime(1970, 1, 1)).total_seconds())

handler = logging.StreamHandler()
handler.setLevel(logging.INFO)
handler.setFormatter(logging.Formatter('%(asctime)s: %(message)s', datefmt='%H:%M:%S'))

logger = logging.getLogger(__name__)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

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


class Record:
    def __init__(self, rname, rtype, args):
        self._rname = DNSLabel(rname)

        rd_cls, self._rtype = TYPE_LOOKUP[rtype]

        if self._rtype == QTYPE.SOA and len(args) == 2:
            # add sensible times to SOA
            args += (SERIAL_NO, 3600, 3600 * 3, 3600 * 24, 3600),

        if self._rtype == QTYPE.TXT and len(args) == 1 and isinstance(args[0], str) and len(args[0]) > 255:
            # wrap long TXT records as per dnslib's docs.
            args = wrap(args[0], 255),

        if self._rtype in (QTYPE.NS, QTYPE.SOA):
            ttl = 3600 * 24
        else:
            ttl = 300

        self.rr = RR(
            rname=self._rname,
            rtype=self._rtype,
            rdata=rd_cls(*args),
            ttl=ttl,
        )

    def match(self, q):
        return q.qname == self._rname and (q.qtype == QTYPE.ANY or q.qtype == self._rtype)

    def sub_match(self, q):
        return self._rtype == QTYPE.SOA and q.qname.matchSuffix(self._rname)

    def __str__(self):
        return str(self.rr)


class Resolver(ProxyResolver):
    def __init__(self, upstream):
        super().__init__(upstream, 53, 5)
        self.cdns = dnsmanager.SecureDNSCloudflare()
        self.gdns = dnsmanager.SecureDNSGoogle()

    def resolve(self, request, handler):
        domain = str(request.q.qname)
        ip = self.cdns.resolveIPV4(domain)
        # no response in cache and from cloudflare, try google dns
        if ip is None:
            ip = self.gdns.resolve(domain)

        type_name = QTYPE[request.q.qtype]

        #print(repr(request.header))
        d = dns.DNSRecord()
        d.header = request.header
        d.header.set_qr(1)
        d.header.set_ra(1)
        d.add_question(dns.DNSQuestion(domain))

        a = dns.A(ip[0])
        #aaa = dns.AAAA(ip[0])

        d.add_answer(RR(domain, QTYPE.A, ttl=60, rdata=a))

        # resolve using normal DNS
        # ret = super().resolve(request, handler)

        # return generated answer
        return d


def handle_sig(signum, frame):
    logger.info('pid=%d, got signal: %s, stopping...', os.getpid(), signal.Signals(signum).name)
    exit(0)


class SecureDNSServer:
    static_udp_server = None
    @staticmethod
    def start():
        #signal.signal(signal.SIGTERM, handle_sig)

        port = int(os.getenv('PORT', 5053))
        upstream = os.getenv('UPSTREAM', '8.8.8.8')
        resolver = Resolver(upstream)
        static_udp_server = DNSServer(resolver, port=port)
        tcp_server = DNSServer(resolver, port=port, tcp=True)

        logger.info('starting DNS server on port %d, upstream DNS server "%s"', port, upstream)
        static_udp_server.start_thread()
        tcp_server.start_thread()

        try:
            while udp_server.isAlive():
                sleep(1)
        except KeyboardInterrupt:
            pass

    def stop():
        pass

    def isRunning():
        return static_udp_server.isAlive()
