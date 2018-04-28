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

import dnslib
from modules.dnsmanager import *
import time


class SecureResolver(dnslib.BaseResolver):
        def resolve(self, request, handler):
            gdns = SecureDNSGoogle()
            cdns = SecureDNSCloudflare()
            ip = cdns.resolve(request.q.qname)
            reply = request.reply()
            reply.add_answer(dnslib.RR("abc.com", dnslib.QTYPE.A, rdata=A(ip), ttl=60))
            return reply


class SecureDNSServer:
    def start(self):
        logger = dnslib.DNSLogger(prefix=False)
        resolver = SecureResolver()
        server = dnslib.DNSServer(resolver, port=8053, address="localhost", logger=logger, tcp=True)
        server.start_thread()

        while server.isAlive():
            time.sleep(1)