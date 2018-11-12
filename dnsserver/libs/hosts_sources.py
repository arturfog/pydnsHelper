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
from . import downloader
from webui.models import HostSources
import os

class HostsSourcesUtils:
    links = []

    @staticmethod
    def load_sources_urls():
        HostsSourcesUtils.links.clear()
        HostsSourcesUtils.links.append("http://winhelp2002.mvps.org/hosts.txt")
        HostsSourcesUtils.links.append("https://raw.githubusercontent.com/yous/YousList/master/hosts.txt")
        HostsSourcesUtils.links.append("https://raw.githubusercontent.com/StevenBlack/hosts/master/hosts")
        HostsSourcesUtils.links.append("http://sysctl.org/cameleon/hosts")
        HostsSourcesUtils.links.append("http://someonewhocares.org/hosts/hosts")

        for link in HostsSourcesUtils.links:
            if not HostSources.objects.filter(url=link).exists():
                HostSources.objects.create(url=link)

    @staticmethod
    def get_number_of_links():
        return HostSources.objects.count()

    @staticmethod
    def download_hosts():
        if HostsSourcesUtils.get_number_of_links() > 0:
            all_entries = HostSources.objects.all()
            dl = downloader.HTTPDownloader()
            for link in all_entries:
                print(link.url)
                if not os.path.isdir("/tmp/hosts/"):
                    os.mkdir("/tmp/hosts")
                dl.download(link.url, "/tmp/hosts/hosts" + str(link.id))
