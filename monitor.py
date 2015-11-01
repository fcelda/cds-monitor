#!/usr/bin/env python3

import logging

import cdsmon.source
import cdsmon.fetch
import cdsmon.update

#source = cdsmon.source.ZonefileSource("example.com", "examples/zones/example.com.zone")
source = cdsmon.source.AXFRSource("example.com", "::2")

import dns.resolver
resolver = dns.resolver.Resolver(configure=False)
resolver.nameservers = [ "::1" ]
resolver.port = 53000
cdsfetch = cdsmon.fetch.ResolverFetch(resolver)

dsupdate = cdsmon.update.DDNSUpdate("::2", 53, "example.com", 10)

for (zone, ds_list) in source.get_delegations():
    print("# %s" % zone)
    for ds in ds_list:
        print("- parent %s" % ds)

    cds_list = cdsfetch.get_cds(zone)
    for cds in cds_list:
        print("- client %s" % cds)

    if len(cds_list) == 0:
        print("- skip update")
        continue

    if not sorted(ds_list) == sorted(cds_list):
        print("- need update")
        dsupdate.update_ds(zone, cds_list)
