# -*- coding: utf-8 -*-

"""
MIT License

Copyright (c) 2020 devsecurity.io <dns-tools@devsecurity.io>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import argparse
import dns.zone
import dns.query
from dns.exception import DNSException
from dns.rdatatype import *
import operator
import re
import sys


def zone_transfer(zone, server):
    try:
        zone = dns.zone.from_xfr(dns.query.xfr(server, zone))
    except DNSException as e:
        print(e.__class__, e)
        sys.exit(1)

    return zone


def create_zone_dict(zone):
    zone_dict = {}
    try:
        origin = re.sub(r"\.$", r"", str(zone.origin))
        for name, node in zone.nodes.items():
            rdatasets = node.rdatasets
            if str(name) == "@":
                dns_name = origin
            else:
                dns_name = "%s.%s" % (str(name), origin)
            for rdataset in rdatasets:
                ttl = rdataset.ttl
                for rdata in rdataset:
                    if rdataset.rdtype == SOA:
                        data = "%s %s %s %s %s %s %s" % (rdata.mname, rdata.rname, rdata.serial, rdata.refresh, rdata.retry, rdata.expire, rdata.minimum) 
                        
                        if dns_name in zone_dict:
                            zone_dict[dns_name].append({"ttl": ttl, "type": "SOA", "data": data})
                        else:
                            zone_dict[dns_name] = [ {"ttl": ttl, "type": "SOA", "data": data} ]
                    
                    elif rdataset.rdtype == NS:
                        target = str(rdata.target)
                        if target.endswith("."):
                            target = re.sub(r"\.$", r"", target)
                        else:
                            target = "%s.%s" % (target, origin)
                        
                        if dns_name in zone_dict:
                            zone_dict[dns_name].append({"ttl": ttl, "type": "NS", "data": target})
                        else:
                            zone_dict[dns_name] = [ {"ttl": ttl, "type": "NS", "data": target} ]
                    
                    elif rdataset.rdtype == CNAME:
                        target = str(rdata.target)
                        if target.endswith("."):
                            target = re.sub(r"\.$", r"", target)
                        else:
                            target = "%s.%s" % (target, origin)
                        
                        if dns_name in zone_dict:
                            zone_dict[dns_name].append({"ttl": ttl, "type": "CNAME", "data": target})
                        else:
                            zone_dict[dns_name] = [ {"ttl": ttl, "type": "CNAME", "data": target} ]
                    
                    elif rdataset.rdtype == A:
                        if dns_name in zone_dict:
                            zone_dict[dns_name].append({"ttl": ttl, "type": "A", "data": str(rdata.address)})
                        else:
                            zone_dict[dns_name] = [ {"ttl": ttl, "type": "A", "data": str(rdata.address)} ]
                    
                    elif rdataset.rdtype == AAAA:
                        if dns_name in zone_dict:
                            zone_dict[dns_name].append({"ttl": ttl, "type": "AAAA", "data": str(rdata.address)})
                        else:
                            zone_dict[dns_name] = [ {"ttl": ttl, "type": "AAAA", "data": str(rdata.address)} ]
                    
                    else:
                        print("Record type not implemented.")
                        sys.exit(1)
    except DNSException as e:
        print(e.__class__, e)
        sys.exit(1)

    return zone_dict

def write_zone_dict_to_csv_file(zone_dict, csv_filename):
    f = open(csv_filename, "w")

    dns_names_sorted = sorted(zone_dict)

    for dns_name in dns_names_sorted:
        records = zone_dict[dns_name]
        for record in records:
            csv_row = "%s;%s;%s;%s\n" % (dns_name, record["ttl"], record["type"], record["data"])
            f.write(csv_row)

    f.close()


def main():
    # Parse arguments
    parser = argparse.ArgumentParser(description="Tool to perform a DNS zone transfer and write the records to a CSV file.", add_help=True)
    parser.add_argument("--server", type=str, required=True, help="IP address of the DNS server to query.")
    parser.add_argument("--zone", type=str, required=True, help="Name of the DNS zone to transfer.")
    parser.add_argument("--csv-file", type=str, required=True, help="Name of the CSV file to write the results to.")
    args = parser.parse_args()

    zone = zone_transfer(args.zone, args.server)
    zone_dict = create_zone_dict(zone)
    write_zone_dict_to_csv_file(zone_dict, args.csv_file)


if __name__ == "__main__":
    main()
