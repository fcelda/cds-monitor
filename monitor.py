#!/usr/bin/env python3

import dns.query
import dns.resolver
import dns.zone

RESOLVER = dns.resolver.Resolver(configure=False)
RESOLVER.nameservers = [ "::1" ]
RESOLVER.port = 53000

class Source:
    def __init__(self):
        pass

    def get_delegations(self):
        pass

class AXFRSource(Source):
    def __init__(self, server, zone):
        self._server = server
        self._zone = zone

    def get_delegations(self):
        zone = dns.zone.from_xfr(dns.query.xfr(self._server, self._zone))
        for name in zone:
            fqdn = name.concatenate(zone.origin)
            if fqdn == zone.origin:
                continue
            if zone[name].get_rdataset(dns.rdataclass.IN, dns.rdatatype.NS):
                yield fqdn

SOURCES = [
        AXFRSource("::2", "example.com")
]
