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

#!/usr/bin/env python

# based on https://github.com/ssut/public-dns/blob/master/publicdns/client.py
import random
import requests
import dns.resolver
import dns.name
import time
import struct
__version__ = '0.0.2'

# cloudflare
# https://developers.cloudflare.com/1.1.1.1/dns-over-https/request-structure/
# curl 'https://cloudflare-dns.com/dns-query?ct=application/dns-json&name=google.com&type=A'
# - https://1.1.1.1/dns-query
# - https://1.0.0.1/dns-query
# google
# https://developers.google.com/speed/public-dns/docs/dns-over-https
# - https://dns.google.com/resolve

# domain to test dnssec verification: dnssec-failed.org

# Resource Record Types
A = 1
AAAA = 28
# DNS status codes
NOERROR = 0


UNRESERVED_CHARS = 'abcdefghijklmnopqrstuvwxyz' \
                   'ABCDEFGHIJKLMNOPQRSTUVWXYZ' \
                   '0123456789-._~'


class InvalidHostName(Exception):
    pass


__default_ns__ = '8.8.8.8'
class DNSSEC(object):
    # https://github.com/ajportier/python-scripts/blob/master/dnssec-validate.py
    @classmethod
    def getDomainSOA(domain_name):
        """Returns the set of SOA records for the given domain using the
        default system resolver"""

        resolver = dns.resolver.Resolver()
        resolver.use_edns(0, dns.flags.DO, 4096)
        resolver.nameservers = ([__default_ns__])

        if (domain_name == '.'):
            return domain_name
        query_domain_parts = domain_name.split('.')
        query_domain = '.'.join(query_domain_parts)
        try:
            soa_response = resolver.query(query_domain, 'SOA')
        except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN):
            query_domain_parts.pop(0)
            query_domain = '.'.join(query_domain_parts)
            domain_name = DNSSEC.getDomainSOA(query_domain)
        return domain_name

    @classmethod
    def getNS(domain_name):
        """Returns all IPs for all NS for the given domain using the
        system default resolver"""

        resolver = dns.resolver.Resolver()
        resolver.use_edns(0,dns.flags.DO,4096)
        resolver.nameservers=([__default_ns__])

        return_ns = set()

        try:
            response_ns = resolver.query(domain_name, 'NS')
        except dns.resolver.NoAnswer:
            print("no answer returned")
        except dns.resolver.NXDOMAIN:
            print("NXDOMAIN")

        for ns in response_ns:
            try:
                response_a = resolver.query(ns.target, 'A')
            except dns.resolver.NoAnswer:
                print("no answer returned")
            except dns.resolver.NXDOMAIN:
                print("NXDOMAIN")
            for a in response_a:
                return_ns.add(a.address)

        return return_ns

    @classmethod
    def getDSFromNS(domain_name, name_server):
        '''Return the set of DS records for the given domain, as obtained
        from the given server'''

        resolver = dns.resolver
        resolver.nameservers = ([name_server])
        try:
            response_ds = resolver.query(domain_name, 'DS')
        except resolver.NoAnswer:
            print('no answer returned')
        except resolver.NXDOMAIN:
            print('NXDOMAIN')
        return response_ds

    @classmethod
    def getDNSKEYFromNS(domain_name, name_server):
        '''Return the set of DNSKEY records for the given domain, as obtained from
        the given server'''

        resolver = dns.resolver.Resolver()
        resolver.use_edns(0, dns.flags.DO, 4096)
        resolver.nameservers = ([name_server])
        name = dns.name.from_text(domain_name)
        rdtype = dns.rdatatype.DNSKEY
        rdclass = dns.rdataclass.IN

        try:
            response = resolver.query(name, rdtype, rdclass, True).response
            response_rrkey = response.find_rrset(response.answer, name, rdclass, dns.rdatatype.RRSIG, rdtype)
            response_dnskey = response.find_rrset(response.answer, name, rdclass, rdtype)
        except dns.resolver.NoAnswer:
            print('no answer returned')
        except dns.resolver.NXDOMAIN:
            print('NXDOMAIN')
        return (response_dnskey, response_rrkey)

    @classmethod
    def getRecordFromNS(domain_name, record, name_server):
        '''Return the set of DNSKEY records for the given domain, as obtained from
        the given server'''

        resolver = dns.resolver.Resolver()
        resolver.use_edns(0, dns.flags.DO, 4096)
        resolver.nameservers = ([name_server])
        name = dns.name.from_text(domain_name)
        rdtype = dns.rdatatype.from_text(record)
        rdclass = dns.rdataclass.IN

        try:
            response = resolver.query(name, rdtype, rdclass, True).response
            response_rrkey = response.find_rrset(response.answer, name, rdclass, dns.rdatatype.RRSIG, rdtype)
            response_rrset = response.find_rrset(response.answer, name, rdclass, rdtype)
        except dns.resolver.NoAnswer:
            response_rrset, response_rrkey = DNSSEC.getRecordFromNS(domain_name, 'CNAME', name_server)
        except dns.resolver.NXDOMAIN:
            print
            'NXDOMAIN'

        return (response_rrset, response_rrkey)

    def getExpiredRRSIG(rrset):
        '''Return the set of RRSIG records in the given rrset that have expired'''

        expired_rrsig = set()

        for rrsig in rrset:
            sig_expire = rrsig.expiration
            if len(str(sig_expire)) == 14:
                time_now = int(time.strftime("%Y%m%d%H%M%S", time.gmtime()))
            else:
                time_now = int(time.time())
            time_diff = sig_expire - time_now
            if time_diff <= 0:
                expired_rrsig.add(rrsig)
        return expired_rrsig

    def getKeyTag(rdata):
        '''Return the key_tag for the given DNSKEY rdata, as specified in RFC 4034.'''

        if rdata.algorithm == 1:
            return struct.unpack('!H', rdata.key[-3:-1])[0]

        key_str = struct.pack('!HBB', rdata.flags, rdata.protocol, rdata.algorithm) + rdata.key

        ac = 0
        for i in range(len(key_str)):
            b, = struct.unpack('B', key_str[i])
            if i & 1:
                ac += b
            else:
                ac += (b << 8)

        ac += (ac >> 16) & 0xffff
        return ac & 0xffff

    def resolve(self, domain):
        parent_ns = set()
        child_ns = set()
        domain_ds = set()
        domain_dnskey = set()
        domain_dnskey_rrsig = set()
        expired_dnskey_rrsig = set()
        valid_dnskey = set()
        record_rrset = set()
        record_rrset_rrsig = set()
        expired_rrset_rrsig = set()
        valid_rrset_rrsig = set()

        domain_parts = domain.split('.')
        record = domain_parts.pop(0)
        child_domain = '.'.join(domain_parts)

        child_domain = DNSSEC.getDomainSOA(domain)
        domain_parts = child_domain.split('.')
        domain_parts.pop(0)
        parent_domain = DNSSEC.getDomainSOA('.'.join(domain_parts))

        print
        "Child Domain: " + child_domain
        print
        "Parent Domain: " + parent_domain

        # Determine the nameservers for the parent domain
        parent_ns = DNSSEC.getNS(parent_domain)

        # Determine the nameservers for the requested domain
        child_ns = DNSSEC.getNS(child_domain)

        # Query parent domain nameservers for DS records of the requested domain
        # TODO: Verify response is the same from all name servers
        for ns in parent_ns:
            response_ds = DNSSEC.getDSFromNS(child_domain, ns)
            for ds in response_ds:
                domain_ds.add(ds.key_tag)

        # Query requested domain nameservers for DNSKEY and RRSIG records
        # TODO: Verify response is the same from all name servers
        for ns in child_ns:
            response_dnskey, response_dnskey_rrsig = DNSSEC.getDNSKEYFromNS(child_domain, ns)
            for dnskey in response_dnskey:
                domain_dnskey.add(DNSSEC.getKeyTag(dnskey))
            for rrsig in response_dnskey_rrsig:
                domain_dnskey_rrsig.add(rrsig.key_tag)

            response_expired_rrsig = getExpiredRRSIG(response_dnskey_rrsig)
            for rrsig in response_expired_rrsig:
                print
                "DNSKEY RRSIG " + str(rrsig.key_tag) + " has expired"
                expired_dnskey_rrsig.add(rrsig.key_tag)

        # Verify that DS and DNSKEY records match up, are signed and signatures have not expired
        valid_dnskeys = domain_ds.copy()
        valid_dnskeys.intersection_update(domain_dnskey)
        valid_dnskeys.intersection_update(domain_dnskey_rrsig)
        valid_dnskeys.difference_update(expired_dnskey_rrsig)
        if len(valid_dnskeys) == 0:
            print
            "No valid DNSKEYS for this domain"
        else:
            for dnskey in valid_dnskeys:
                print
                "Valid DNSKEY: " + str(dnskey)

        # Verify the RRSIG covering the requsted domain records is signed and has not expired
        for ns in child_ns:
            response_rrset, response_rrset_rrsig = getRecordFromNS(domain, 'A', ns)
            for record in response_rrset:
                record_rrset.add(record)
            for rrsig in response_rrset_rrsig:
                valid_rrset_rrsig.add(rrsig.key_tag)
                record_rrset_rrsig.add(rrsig)

        response_expired_rrsig = getExpiredRRSIG(record_rrset_rrsig)
        for rrsig in response_expired_rrsig:
            print
            "RRset RRSIG " + str(rrsig.key_tag) + " has expired"
            expired_rrset_rrsig.add(rrsig.key_tag)

        print
        "Domain DNSKEY: " + str(domain_dnskey)
        print
        "DNSKEY RRSIG: " + str(domain_dnskey_rrsig)
        print
        "RRSet RRSIG: " + str(valid_rrset_rrsig)

        valid_rrset_rrsig.intersection_update(valid_dnskeys)
        valid_rrset_rrsig.difference_update(expired_rrset_rrsig)
        if len(valid_rrset_rrsig) == 0:
            print
            "No valid RRset RRSIGs for this domain"
        else:
            for rrsig in valid_rrset_rrsig:
                print
                "Valid RRSIG: " + str(rrsig)

class SecureDNS(object):

    def getDNSSecResponse(self, hostname):
        pass

    def prepare_hostname(self, hostname):
        '''verify the hostname is well-formed'''
        hostname = hostname.rstrip('.')  # strip trailing dot if present

        if not(1 <= len(hostname) <= 253):  # test length of hostname
            raise InvalidHostName

        for label in hostname.split('.'):  # test length of each label
            if not(1 <= len(label) <= 63):
                raise InvalidHostName
        try:
            return hostname.encode('ascii')
        except UnicodeEncodeError:
            raise InvalidHostName


class SecureDNSCloudflare(SecureDNS):
    def __init__(
            self,
            query_type='A',
            ct='application/dns-json'
    ):
        self.url = 'https://cloudflare-dns.com/dns-query'
        self.params = {
            'type': query_type,
            'ct': ct
        }

    def resolve(self, hostname):
        '''return ip address(es) of hostname'''
        hostname = self.prepare_hostname(hostname)
        self.params.update({'name': hostname})

        r = requests.get(self.url, params=self.params)
        if r.status_code == 200:
            response = r.json()

            if response['Status'] == NOERROR:
                answers = []
                for answer in response['Answer']:
                    name, response_type, ttl, data = \
                        map(answer.get, ('name', 'type', 'ttl', 'data'))
                    if response_type in (A, AAAA):
                        answers.append(data)
                if answers == []:
                    return None
                return answers
        return None

class SecureDNSGoogle(SecureDNS):
    '''Resolve domains using Google's Public DNS-over-HTTPS API'''

    def __init__(
        self,
        query_type=1,
        cd=False,
        edns_client_subnet='0.0.0.0/0',
        random_padding=True,
    ):
        self.url = 'https://dns.google.com/resolve'
        self.params = {
            'type': query_type,
            'cd': cd,
            'edns_client_subnet': edns_client_subnet,
            'random_padding': random_padding,
        }

    def resolve(self, hostname):
        '''return ip address(es) of hostname'''
        hostname = self.prepare_hostname(hostname)
        self.params.update({'name': hostname})

        if self.params['random_padding']:
            padding = self.generate_padding()
            self.params.update({'random_padding': padding})

        r = requests.get(self.url, params=self.params)
        if r.status_code == 200:
            response = r.json()

            if response['Status'] == NOERROR:
                answers = []
                for answer in response['Answer']:
                    name, response_type, ttl, data = \
                        map(answer.get, ('name', 'type', 'ttl', 'data'))
                    if response_type in (A, AAAA):
                        answers.append(data)
                if answers == []:
                    return None
                return answers
        return None

    def generate_padding(self):
        '''generate a pad using unreserved chars'''
        pad_len = random.randint(10, 50)
        return ''.join(random.choice(UNRESERVED_CHARS) for _ in range(pad_len))


def main():
    dns1 = SecureDNSGoogle()
    result1 = dns1.resolve("bzwbk.pl")
    print(repr(result1))

    dns2 = SecureDNSCloudflare()
    result2 = dns2.resolve("bzwbk.pl")
    print(repr(result2))


if __name__ == '__main__':
    main()
