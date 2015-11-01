#!/usr/bin/env python3

import cdsmon.source

import dns.query
import dns.resolver
import dns.zone

class CDSFetch:
    def __init__(self, resolver):
        self._resolver = resolver

    def get_cds(self, zone):
        try:
            rrs = self._resolver.query(zone, "CDS", raise_on_no_answer=False).rrset
            return [rr.to_text() for rr in rrs] if rrs else []
        except dns.resolver.NoNameservers:
            return []

class DSUpdate:
    def update_ds(self, zone, ds_set):
        raise NotImplementedError()

import dns.name, dns.query, dns.tsigkeyring, dns.update

class DDNSUpdate(DSUpdate):
    def __init__(self, server, port, origin, ttl, tsig=None):
        self._server = server
        self._port = port
        self._origin = origin
        self._ttl = ttl
        self._tsig = tsig

    def _init_update(self, zone):
        if self._tsig is not None:
            name, algorithm_name, key = self._tsig
            keyring = dns.tsigkeyring.from_text({name: key})
            keyalgorithm = dns.name.from_text(algorithm_name)
        else:
            keyring = None
            keyalgorithm = None

        return dns.update.Update(zone, keyring=keyring, keyalgorithm=keyalgorithm)

    def update_ds(self, zone, ds_set):
        update = self._init_update(self._origin)
        update.delete(zone, dns.rdatatype.DS)
        for ds in ds_set:
            update.add(zone, self._ttl, dns.rdatatype.DS, ds)
        response = dns.query.tcp(update, self._server, port=self._port)
        return response.rcode() == 0

#source = cdsmon.source.ZonefileSource("example.com", "examples/zones/example.com.zone")
source = cdsmon.source.AXFRSource("example.com", "::2")

resolver = dns.resolver.Resolver(configure=False)
resolver.nameservers = [ "::1" ]
resolver.port = 53000

cdsfetch = CDSFetch(resolver)

dsupdate = DDNSUpdate("::2", 53, "example.com", 10)

for (zone, ds_list) in source.get_delegations():
    print("# %s" % zone)
    for ds in ds_list:
        print("- parent %s" % ds)

    cds_list = cdsfetch.get_cds(zone)
    for cds in cds_list:
        print("- client %s" % cds)

    if len(cds_list) == 0:
        continue

    if not sorted(ds_list) == sorted(cds_list):
        print("- need update")
        dsupdate.update_ds(zone, cds_list)
