# Examples

This directory contains a sample configuration files and zones files which
can be used to test this prototype.

Just a few notes to make this work:

- **knot.conf**:
  - Configuration file for Knot DNS 2.x
  - Authoritative server for all testing zones (*example.com* is the parent one)
  - The server has to run on privileged port 53 as we need the recursive resolution
    (for this purpose, we the ::2 address is used)
  - Automatic DNSSEC signing is set up for the parent zone.
  - AXFR and DDNS is allowed without authentication for the parent zone

- **unbound.conf**
  - Resolver instance configured to use Knot DNS as a stub for the parent zone
  - Trust anchor is set to trust the key we use to sign the parent zone
  - Runs on ::1 port 53000 (need not be privileged)

- **keys**
  - Knot DNS DNSSEC KASP database, contains key to sign the parent zone.

- **zones**
  - Contains testing zone files
  - The parent zone is signed automatically
  - The child zones may be signed manually
