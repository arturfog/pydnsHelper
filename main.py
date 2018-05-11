from modules import dnsserver
from modules import dnsmanager
from modules import hosts_sources
from modules import downloader
from modules import hosts_manager

def main():
    #dns = dnsserver.SecureDNSServer()
    #dns.start()

    #cdns = dnsmanager.SecureDNSCloudflare()
    #ip4 = cdns.resolveIPV4("www.google.com")
    #ip6 = cdns.resolveIPV6("www.facebook.com")

    hosts_sources.HostsSources.load_sources_urls()
    links = hosts_sources.HostsSources.get_links()

    dl = downloader.HTTPDownloader()
    #for link in links:
        #print(link)
        #dl.download(link, dl.gen_random_filename("hosts", "/tmp"))
        #dl.download('https://ftp.gnu.org/pub/gnu/bash/bash-2.02.1.tar.gz', '/tmp/hosts1')

    hm = hosts_manager.HostsManager()
    hm.open_db('/tmp/hosts.db')
    hm.import_host_files('/home/artur/hosts')
    hosts_manager.HostsManager.generate_host_file(hm.get_session(), '/tmp/hosts.txt')
    print(hm.get_ip("dobre-programy.pl"))


if __name__ == "__main__":
    main()
