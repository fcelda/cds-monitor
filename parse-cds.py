#!/usr/bin/env python
#

import os, sys, struct
import dns.resolver, dns.rdatatype, dns.rdataclass
from io import BytesIO

r = dns.resolver.Resolver()
r.nameservers = [ '127.0.0.1' ]
a = r.query('nlnetlabs.nl.', 'TYPE59')

for rrset in a.response.answer:
    for rr in rrset:
        f = BytesIO()
        rr.to_wire(f, None)
        wire_rdata = f.getvalue()
        f.close()
        keytag, alg, digest_type = struct.unpack('!Hbb', wire_rdata[0:4])
        print("%s %d %s %s %d %d %d %s" % 
              (rrset.name, rrset.ttl, \
               dns.rdataclass.to_text(rrset.rdclass), \
               dns.rdatatype.to_text(rrset.rdtype), \
               keytag, alg, digest_type, wire_rdata[4:].encode('hex')))



