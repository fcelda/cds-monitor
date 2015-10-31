#!/usr/bin/env python3

import dns.query
import dns.resolver
import dns.zone

class Source:
    def get_delegations(self):
        raise NotImplemented()

class AXFRSource(Source):
    def __init__(self, server, zone):
        self._server = server
        self._zone = zone

    def _is_delegation(self, node):
        return node.get_rdataset(dns.rdataclass.IN, dns.rdatatype.NS) is not None

    def _get_ds(self, node):
        rrs = node.get_rdataset(dns.rdataclass.IN, dns.rdatatype.DS)
        return [rr.to_text() for rr in rrs] if rrs else []

    def get_delegations(self):
        zone = dns.zone.from_xfr(dns.query.xfr(self._server, self._zone))
        for name in zone:
            fqdn = name.concatenate(zone.origin)
            if fqdn == zone.origin:
                continue
            node = zone[name]
            if self._is_delegation(node):
                ds = self._get_ds(node)
                yield (fqdn, ds)

class CDSFetch:
    def __init__(self, resolver):
        self._resolver = resolver

    def get_cds(self, zone):
        try:
            rrs = self._resolver.query(zone, "CDS", raise_on_no_answer=False).rrset
            return [rr.to_text() for rr in rrs] if rrs else []
        except dns.resolver.NoNameservers:
            return []

source = AXFRSource("::2", "example.com")

resolver = dns.resolver.Resolver(configure=False)
resolver.nameservers = [ "::1" ]
resolver.port = 53000

cdsfetch = CDSFetch(resolver)

for (zone, ds_list) in source.get_delegations():
    print("# %s" % zone)
    for ds in ds_list:
        print("- parent %s" % ds)

    cds_list = cdsfetch.get_cds(zone)
    for cds in cds_list:
        print("- client %s" % cds)
