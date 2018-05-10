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


class HostsSources:
    links = []

    @staticmethod
    def load_sources_urls():
        HostsSources.links.clear()
        HostsSources.links.append("http://winhelp2002.mvps.org/hosts.txt")
        HostsSources.links.append("https://raw.githubusercontent.com/yous/YousList/master/hosts.txt")
        HostsSources.links.append("https://raw.githubusercontent.com/StevenBlack/hosts/master/hosts")
        HostsSources.links.append("http://sysctl.org/cameleon/hosts")
        HostsSources.links.append("http://someonewhocares.org/hosts/hosts")

    @staticmethod 
    def get_links():
        """
            Gets list of string with links to dl files

            Returns
            -------
            []->string
                List of string with links to dl file

        """
        HostsSources.load_sources_urls()
        return HostsSources.links

    @staticmethod
    def get_number_of_links():
        return len(HostsSources.links)

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
        HostsSources.load_sources_urls()
        if num < HostsSources.get_number_of_links():
            return HostsSources.links[num]
        return None
