#!/usr/bin/env python3

import logging
import sched
import time

import cdsmon.source
import cdsmon.fetch
import cdsmon.update

class Monitor:
    def __init__(self, source, fetch, update):
        self._source = source
        self._fetch = fetch
        self._update = update
        self._next = 0

    def exec(self):
        time_start = time.time()
        for zone, ds_list in self._source.get_delegations():
            for ds in ds_list:
                logging.debug("%s, DS '%s'" % (zone, ds))

            cds_list = self._fetch.get_cds(zone)
            for cds in cds_list:
                logging.debug("%s, CDS '%s'" % (zone, cds))

            if len(cds_list) == 0:
                logging.info("%s, CDS not present" % zone)
                continue

            if not sorted(ds_list) != sorted(cds_list):
                logging.info("%s, is up-to-date" % zone)
            else:
                logging.info("%s, sending update" % zone)
                self._update(zone, cds_list)

        self._next = time_start + self._source.refresh_seconds()

    def next(self):
        return self._next

# setup logging
logging_format = "%(asctime)s %(levelname)s: %(message)s"
logging.basicConfig(format=logging_format, level=logging.DEBUG)

# setup interfaces
axfr_source = cdsmon.source.AXFRSource("example.com", "::2")
#zone_source = cdsmon.source.ZonefileSource("example.com", "examples/zones/example.com.zone")

import dns.resolver
resolver = dns.resolver.Resolver(configure=False)
resolver.nameservers = [ "::1" ]
resolver.port = 53000
cds_fetch = cdsmon.fetch.ResolverFetch(resolver)

ds_update = cdsmon.update.DDNSUpdate("::2", 53, "example.com", 10)

# execution loop
loop = sched.scheduler()
monitor = Monitor(axfr_source, cds_fetch, ds_update)

def run_and_reschedule():
    monitor.exec()
    next_abs = monitor.next()
    next_rel = max(0, next_abs - time.time())
    logging.debug("refresh in %.2f seconds" % next_rel)
    loop.enter(next_rel, 0, run_and_reschedule)

loop.enter(0, 0, run_and_reschedule)
loop.run()
