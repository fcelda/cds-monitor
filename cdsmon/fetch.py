import dns.resolver

class Fetch:
    """
    Get CDS/CDNSKEY records of the child zone.
    """

    def get_cds(self, zone):
        """
        Return list of CDS RDATA for a child zone.
        """
        raise NotImplementedError()

class ResolverFetch:
    def __init__(self, resolver):
        self._resolver = resolver

    def get_cds(self, zone):
        try:
            rrs = self._resolver.query(zone, "CDS", raise_on_no_answer=False).rrset
            return [rr.to_text() for rr in rrs] if rrs else []
        except dns.resolver.NoAnswer:
            return []
        except dns.resolver.NoNameservers:
            return []
