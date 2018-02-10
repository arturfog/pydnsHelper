class HostsSources:
    links = []

    @staticmethod
    def load_sources_urls():
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
