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

from modules import dnsserver
from modules import dnsmanager
from modules import hosts_sources
from modules import hosts_manager

def main():
    #dns = dnsserver.SecureDNSServer()
    #dns.start()

    #hosts_sources.HostsSources.load_sources_urls()
    #links = hosts_sources.HostsSources.get_links()

    hm = hosts_manager.HostsManager()
    hm.open_db('/tmp/hosts.db')
    hm.import_host_files('/home/artur/hosts')
    #hosts_manager.HostsManager.generate_host_file(hm.get_session(), '/tmp/hosts.txt')
    #print(hm.get_ip("consumerproductsusa.com"))

    cdns = dnsmanager.SecureDNSCloudflare()
    ip4 = cdns.resolveIPV4('www.dobre-programy.pl')
    print("ip4: " + ip4[0])
    ip4 = cdns.resolveIPV4('www.google.com')
    print("ip4: " + ip4[0])
    #ip6 = cdns.resolveIPV6("www.facebook.com")
    #print("ip6: " + ip6[0])


if __name__ == "__main__":
    main()
