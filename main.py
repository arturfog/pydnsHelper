from modules import hosts_manager
from modules import downloader


def main():
    hm = hosts_manager.HostsManager()
    dl = downloader.HTTPDownloader()

    dl.download(url='http://localhost/hosts.txt', file_path='/tmp/hosts.txt')


if __name__ == "__main__":
    main()
