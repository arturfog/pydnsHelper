#!/usr/bin/env python

from modules import downloader
from modules import hosts_sources


def main():
    dl = downloader.Downloader()
    for link in hosts_sources.HostsSources.get_links():
        dl.download_file(link)


if __name__ == '__main__':
    main()
