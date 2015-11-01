import dns.rdatatype
import dns.query
import dns.zone

class Source:
    def get_delegations(self):
        """
        Iterable. Return a list of (zone, ds_list) tuples from the parent zone.
        """
        raise NotImplementedError()

    def refresh_seconds(self):
        """
        Return how long we should wait before fetching new delegations.
        """
        raise NotImplementedError()

class AXFRSource(Source):
    """
    AXFR source of DS records.
    """

    def __init__(self, zone, server):
        self._zone = zone
        self._server = server
        self._refresh = None

    def get_delegations(self):
        soa = None
        zone_name = dns.name.from_text(self._zone)
        xfr = dns.query.xfr(self._server, self._zone, relativize=False)
        delegations = {}

        for msg in xfr:
            for rrset in msg.answer:
                # SOA refresh
                if rrset.rdtype == dns.rdatatype.SOA:
                    self._refresh = rrset[0].refresh
                # skip zone apex
                elif rrset.name == zone_name:
                    pass
                # delegation
                elif rrset.rdtype == dns.rdatatype.NS:
                    delegations.setdefault(rrset.name, [])
                elif rrset.rdtype == dns.rdatatype.DS:
                    delegations.setdefault(rrset.name, [])
                    rdata = rrset[0].to_text()
                    delegations[rrset.name].append(rdata)

        for (name, ds_list) in delegations.items():
            yield (name.to_text(omit_final_dot=True), ds_list)

    def refresh_seconds(self):
        return self._refresh if self._refresh else 60

class ZonefileSource(Source):
    """
    Zone file source of DS records.
    """

    def __init__(self, origin, filename):
        self._origin = origin
        self._filename = filename

    def _is_delegation(self, node):
        return node.get_rdataset(dns.rdataclass.IN, dns.rdatatype.NS) is not None

    def _get_ds(self, node):
        rrs = node.get_rdataset(dns.rdataclass.IN, dns.rdatatype.DS)
        return [rr.to_text() for rr in rrs] if rrs else []

    def get_delegations(self):
        zone = dns.zone.from_file(self._filename, origin=self._origin, relativize=False)
        for name in zone:
            if name == zone.origin:
                continue
            node = zone[name]
            if self._is_delegation(node):
                ds_list = self._get_ds(node)
                yield (name, ds_list)

    def refresh_seconds(self):
        return 10
