#!/usr/bin/env python

import argparse
import sys
import MySQLdb
import yaml
from collections import defaultdict
from iptools.ipv4 import validate_ip

class DnsServer(object):
    """Class for holding DNS server information to passing to functions"""
    def __init__(self, name, port, user, password, database):
        self.name = name
        self.port = port
        self.user = user
        self.password = password
        self.database = database

def get_server_yaml(yaml_file=None):
    """Get DNS server information from YAML file"""
    if yaml_file is None:
        yaml_file = '/etc/pdns-register.yaml'
    try:
        f = open(yaml_file)
    except IOError as e:
        if e[0] == 2:
            print 'File not found.'
        elif e[0] == 13:
            print 'Could not open configuration file. Permission denied.'
        else:
            print 'There was an issue opening the configuration file.'
        sys.exit()
    data = yaml.safe_load(f)
    f.close()
    try:
        server_info = DnsServer(data['server']['name'],data['server']['port'],data['server']['username'],data['server']['password'],data['server']['database'])
    except NameError:
        print 'Error loading attributes in %s.' % yaml_file
        sys.exit()
    return server_info

def perform_query(dns_server, db_port, db_user, db_pw, database, query, op_type):
    """This builds a query or insert to perform on a PowerDNS database"""
    try:
        db_conn = MySQLdb.connect(host=dns_server, port=db_port, user=db_user, passwd=db_pw, db=database)
        cursor = db_conn.cursor()
        if op_type == 'query':
            cursor.execute(query)
            return_data = cursor.fetchall()
            db_conn.close()
            return return_data
        if op_type == 'insert':
            try:
                cursor.execute(query)
                db_conn.commit()
            except:
                db_conn.rollback()
    except MySQLdb.Error as e:
        if e[0] == 1045:
            print 'Access denied access the MySQL database on %s. Exiting...' % dns_server
            sys.exit(5)
        else:
            print 'Database does not exist.'
            sys.exit(6)

def get_domain_id(domain, server):
    """Get a domain ID given a domain and a PowerDNS server"""
    domain_id_query = "SELECT * FROM domains WHERE name='%s'" % domain
    try:
        domain_id = perform_query(server.name, server.port, server.user, server.password, server.database, domain_id_query, 'query')[0]
    except IndexError:
        print 'There are no domains with the name %s in the database.' % domain
        sys.exit()
    return domain_id[0]

def record_name_exist(domain, server, name):
    """Check existance of a record name"""
    this_domain_id = get_domain_id(domain, server)
    record_name_query = "SELECT * FROM records where domain_id={0} and name='{1}'".format(this_domain_id, name)
    record_name = perform_query(server.name, server.port, server.user, server.password, server.database, record_name_query, 'query')
    if any(record_name):
        return True
    else:
        return False

def get_domain_records(domain, server):
    """Return all records for a domain from a given server"""
    this_domain_id = get_domain_id(domain, server)
    domain_records_query = 'SELECT * FROM records where domain_id=%s' % this_domain_id
    domain_records = perform_query(server.name, server.port, server.user, server.password, server.database, domain_records_query, 'query')
    return domain_records

def get_reverse_domains(server):
    """Return all reverse domains and their ids in a dictionary from a given server"""
    reverse_domains_query = "SELECT * FROM domains where name like '%.in-addr.arpa'"
    reverse_domains = perform_query(server.name, server.port, server.user, server.password, server.database, reverse_domains_query, 'query')
    reverse_domains_dict = {}
    reverse_domains_dict = defaultdict(list)
    for i in reverse_domains:
        reverse_domains_dict[i[1]].append(i[0])
    return reverse_domains_dict

def find_reverse_domain_id(server, ip):
    """Find a reverse domain id given an ip and server"""
    #rev_domains = get_reverse_domains(server)
    if validate_ip(ip):
    #in_addr_ip = convert_ip_to_addr(ip)
    # Look for reverse zone in order of most specific to least specifc
        reverse_ip = ip.split('.')[::-1]
        print reverse_ip
        next_reverse_zone = '.'.join(split_ip[::-3]) + '.in-addr.arpa'
        print next_reverse_zone

def convert_ip_to_addr(ip):
    if validate_ip(ip):
        split_ip = ip.split('.')
        reverse_ip = '.'.join(split_ip[::-1]) + '.in-addr.arpa'
        return reverse_ip
    else:
        raise Exception('The IP address is not in dotted-quad format.')

# TODO: Add function param to disable auto-adding of PTR
def insert_record(domain, server, rec_type, name, content, ttl=None, add_reverse=None):
    """Insert record into PDNS records database"""
    if ttl is None:
        ttl = 3600
    record_domain_id = get_domain_id(domain, server)
    # Check to see if record exists
    if record_name_exist(domain, server, name):
        raise Exception('This record already exists')
    # Validate dotted-quad ip address
    elif rec_type == 'A' and not validate_ip(content):
        raise Exception('The IP address used as content is not in dotted-quad format.')
    else:
        insert_query = "INSERT INTO records (domain_id,name,type,content,ttl) VALUES ({0},'{1}','{2}','{3}',{4})".format(record_domain_id, name, rec_type, content, ttl)
        perform_query(server.name, server.port, server.user, server.password, server.database, insert_query, 'insert')
        print "DNS Registration successful."
    # TODO: insert reverse record (need a way to find reverse domain), also add error-checking to make sure reverse record is not already present
    # Add reverse record
    #if add_reverse:
    #    if rec_type == 'A':


def main():
    """Get command-line inputs"""
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--file', help='YAML file input', dest='input_file')
    parser.add_argument('-d', '--domain', help='Domain of record', dest='domain')
    parser.add_argument('-n', '--name', help='Record name', dest='name')
    parser.add_argument('-c', '--content', help='Content of record', dest='content')
    parser.add_argument('-r', '--rectype', help='Record type (A, CNAME, PTR, etc)', dest='rectype')
    parser.add_argument('-t', '--ttl', help='TTL', dest='ttl', default=3600)
    args = parser.parse_args()

    # Check for command-line input
    if args.input_file:
        input_file = args.input_file
    else:
        try:
            input_file = raw_input('Please enter the path to the YAML file containing DNS server data: ')
        except KeyboardInterrupt:
            sys.exit()
    server_obj = get_server_yaml(input_file)
    if args.domain:
        domain = args.domain
    else:
        try:
            domain = raw_input('Please enter the domain of the record you are inserting: ')
        except KeyboardInterrupt:
            sys.exit()
    if args.name:
        name = args.name
    else:
        try:
            name = raw_input('Please enter the name of the record you are inserting: ')
        except KeyboardInterrupt:
            sys.exit()
    if args.content:
        content = args.content
    else:
        try:
            content = raw_input('Please enter the content of the record you are inserting: ')
        except KeyboardInterrupt:
            sys.exit()
    if args.rectype:
        rectype = args.rectype
    else:
        try:
            rectype = raw_input('Please enter the record type you are inserting (A, CNAME, PTR): ')
        except KeyboardInterrupt:
            sys.exit()
    if args.ttl:
        # TODO: check to ensure TTL is between 0 and 2147483647 (RFC 2181)
        ttl = args.ttl
    else:
        try:
            ttl = raw_input('Please enter the ttl of the record you are inserting: ')
        except KeyboardInterrupt:
            sys.exit()

    insert_record(domain, server_obj, rectype, name, content, ttl)

if __name__ == '__main__':
    main()
