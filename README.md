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

## DNS Server Settings
By default, pdns_register looks at /etc/pdns-register.yaml for the PowerDNS server configuration settings. These include the DNS server name, database username, password, port, and PowerDNS database name. For example:
```yaml
---
server:
  name: 'chdns1.qa.isrealm.com'
  username: 'powerdns'
  password: 'changeme'
  port: 3306
  database: 'powerdns'
```

The YAML file can be specified as a command-line parameter as well if the default path isn't desirable:
```bash
$ pdns_register --file /usr/local/etc/pdns.yaml --name test.example.com --content 10.2.3.4 --rectype A --domain example.com
```