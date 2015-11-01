#!/usr/bin/env python
#
# Given a zone, master server, and child CDS rrset, generate DNS
# update message to replace the DS rrset with the CDS rrset contents.
# 
# Warning: yet untested
#

import dns.name, dns.query, dns.tsigkeyring, dns.update


def update_cds_ds(zone, server, cds_rrset, tsig=None):

    if tsig:
        tsigname, tsigalg, tsigkey = tsig
        keyring = dns.tsigkeyring.from_text({tsigname : tsigkey})
        keyalg = dns.name.from_text(tsigalg)
        update = dns.update.Update(zone, keyring=keyring, 
                                   keyalgorithm=keyalg)
    else:
        update = dns.update.Update(zone)

    update.delete(cds_rrset.name, dns.rdatatype.DS)
    for rr in cds_rrset:
        update.add(cds_rrset.name, cds_rrset.ttl, dns.rdatatype.DS, 
                   rr.to_text())

    response = dns.query.tcp(update, server)
    if response.rcode() == 0:
        return True
    else:
        return False

