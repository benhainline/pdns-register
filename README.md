# pdns_register

## Overview
pdns_registration is a Python script that interacts with PowerDNS's MySQL backend to add and delete DNS records.

## CLI Usage

```bash
usage: pdns_register.py [-h] [-f INPUT_FILE] [-d DOMAIN] [-n NAME]
                        [-c CONTENT] [-r RECTYPE] [-t TTL]

optional arguments:
  -h, --help            show this help message and exit
  -f INPUT_FILE, --file INPUT_FILE
                        YAML file input
  -d DOMAIN, --domain DOMAIN
                        Domain of record
  -n NAME, --name NAME  Record name
  -c CONTENT, --content CONTENT
                        Content of record
  -r RECTYPE, --rectype RECTYPE
                        Record type (A, CNAME, PTR, etc)
  -t TTL, --ttl TTL     TTL
```