import dns.query
import dns.tsigkeyring
import dns.update

class Update:
    """
    Perform DS record update in parent zone.
    """

    def update_ds(self, zone, ds_set):
        raise NotImplementedError()

class DDNSUpdate(Update):
    """
    Perform DS record update using DDNS mechanism.
    """

    def __init__(self, server, port, origin, ttl, tsig=None):
        self._server = server
        self._port = port
        self._origin = origin
        self._ttl = ttl
        self._tsig = tsig

    def _init_update(self):
        origin = dns.name.from_text(self._origin)
        if self._tsig is not None:
            name, algorithm_name, key = self._tsig
            keyring = dns.tsigkeyring.from_text({name: key})
            keyalgorithm = dns.name.from_text(algorithm_name)
        else:
            keyring = None
            keyalgorithm = None

        return dns.update.Update(origin, keyring=keyring, keyalgorithm=keyalgorithm)

    def update_ds(self, name, ds_set):
        update = self._init_update()
        name = dns.name.from_text(name)
        update.delete(name, dns.rdatatype.DS)
        for ds in ds_set:
            update.add(name, self._ttl, dns.rdatatype.DS, ds)
        response = dns.query.tcp(update, self._server, port=self._port)
        return response.rcode() == 0
