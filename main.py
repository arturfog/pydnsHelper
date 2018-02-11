#!/usr/bin/env python

from modules import downloader
from modules import hosts_sources
from modules import hosts_manager


def files(path):
    import os
    for file in os.listdir(path):
        if os.path.isfile(os.path.join(path, file)):
            yield file


def main():
    dl = downloader.Downloader()
    i = 0
    for link in hosts_sources.HostsSources.get_links():
        dl.download_file(link, filename="hosts_" + str(i) + ".txt")
        i += 1

    #
    hm = hosts_manager.HostsManager()
    for file in files("."):
        hm.import_host_file(file)


if __name__ == '__main__':
    main()
