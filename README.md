pdns-register
=============

## Overview
pdns-registration is a Python script that interacts with the PowerDNS MySQL backend to add and delete DNS records.

## CLI Usage

```bash
usage: pdns-register [-h] [-f INPUT_FILE] [-d DOMAIN] [-n NAME] [-c CONTENT]
                     [-r {A,PTR,CNAME}] [-x DELETE] [-t TTL] [-p]

optional arguments:
  -h, --help            show this help message and exit
  -f INPUT_FILE, --file INPUT_FILE
                        YAML file input
  -d DOMAIN, --domain DOMAIN
                        Domain of record
  -n NAME, --name NAME  Record name
  -c CONTENT, --content CONTENT
                        Content of record
  -r {A,PTR,CNAME}, --rec-type {A,PTR,CNAME}
                        Record type
  -x DELETE, --delete DELETE
                        Delete record
  -t TTL, --ttl TTL     TTL
  -p, --no-ptr          Do not add a corresponding PTR record when adding an A
                        record
```

## DNS Server Settings
By default, pdns-register looks at /etc/pdns-register.yaml for the PowerDNS server configuration settings. These include the DNS server name, database username, password, port, and PowerDNS database name. For example:
```yaml
---
server:
  name: 'mypdns.example.com'
  username: 'powerdns'
  password: 'changeme'
  port: 3306
  database: 'powerdns'
```

The YAML file can be specified as a command-line parameter as well if the default path isn't desirable:
```bash
$ pdns-register --file /usr/local/etc/pdns.yaml --name test.example.com --content 10.2.3.4 --rectype A --domain example.com
```
