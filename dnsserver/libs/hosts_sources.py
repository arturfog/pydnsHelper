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

        HostSources.objects.create(url='Sample title')

    @staticmethod 
    def get_links():
        """
            Gets list of string with links to dl files

            Returns
            -------
            []->string
                List of string with links to dl file

        """
        if len(HostsSourcesUtils.links) <= 0:
            HostsSourcesUtils.load_sources_urls()
        return HostsSourcesUtils.links

    @staticmethod
    def get_number_of_links():
        return len(HostsSourcesUtils.links)

    @staticmethod
    def check_for_new_hosts():
        pass

    @staticmethod
    def download_hosts():
        if len(HostsSourcesUtils.links) <= 0:
            HostsSourcesUtils.load_sources_urls()

        dl = downloader.HTTPDownloader()
        for link in HostsSourcesUtils.links:
            print(link)
            dl.download(link, dl.gen_random_filename("hosts", "/tmp"))

    @staticmethod
    def get_link(num):
        """
            Gets link from list at selected position

            Parameters
            ----------
            num : int
                number of link to get

            Returns
            -------
            string
                String with selected link

        """
        if len(HostsSourcesUtils.links) <= 0:
            HostsSourcesUtils.load_sources_urls()
        if num < HostsSourcesUtils.get_number_of_links():
            return HostsSourcesUtils.links[num]
        return None
