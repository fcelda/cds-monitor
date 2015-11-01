# CDS/CDNSKEY Monitoring Prototype

This is a prototype application created during IETF 94 Hackathon in Yokohama.

The application fetches delegations from a zone, queries for the CDS/CDNSKEY
records in the child zone, and compares these two sets. If these sets are
different, an update of the parent zone is triggered.

## Architecture

There update process is separated into three stages. For each stage, a simple
abstract interface is defined allowing to implement custom adapters.

1. The `Source` component is responsible for fetching delgations from the parent zone.
2. The `Fetch` component is responsible for fetching CDS/CNDKEY records from the child zone.
3. The `Update` component is responsible for updating the parent zone.

For the first stage, two adapters have been implemented. The delegations can be
fetched form a zone file (`dnsmon.source.ZonefileSource`) or using AXFR from
the master server (`dnsmon.source.AXFRSource`).

For the second stage, there is a `ResolverFetch` function which uses a stub
resolver to get the records. Make sure the validator is configured to perform
the DNSSEC validation.

For the last stage, the DDNS update mechanism was implemented.

## Requirements

- Python 3
- dnspython (patched to support CDS/CDNSKEY)

## Setup

1. `mkvirtualenv -p /usr/bin/python3 cds-monitor`
2. `workon cds-monitor`
3. `pip install -r requirements.txt`
4. `./monitor.py`

## Configuration

There is no configuration file. The configuration is currently hard-coded
in the main script.

## Authors

- Jan Včelák
- Shumon Huque

## TODO

- Configuration file support.
- CDNSKEY support
- Semantic checks on the data retrieved from the child zone
- ...
