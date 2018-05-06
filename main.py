from modules import dnsserver


def main():
    dns = dnsserver.SecureDNSServer()
    dns.start()


if __name__ == "__main__":
    main()
