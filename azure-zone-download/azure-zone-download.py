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
import csv
import getpass
import os
import sys
import re

from azure.common.credentials import ServicePrincipalCredentials
from azure.mgmt.dns import DnsManagementClient
from msrestazure.azure_exceptions import CloudError


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def print_error(msg):
    sys.stderr.write(bcolors.FAIL + bcolors.BOLD + "Error:" + bcolors.ENDC + " %s\n" % msg)


def main():
    # Parse arguments
    parser = argparse.ArgumentParser(description="Tool to download DNS zones from Azure.", add_help=True)
    parser.add_argument("--tenant-id", type=str, required=False, help="Azure tenant ID.")
    parser.add_argument("--subscription-id", type=str, required=False, help="Azure subscription ID.")
    parser.add_argument("--resource-group", type=str, required=True, help="Azure resource group of the DNS zone.")
    parser.add_argument("--client-id", type=str, required=False, help="Client ID of service principal.")
    parser.add_argument("--zone", type=str, required=True, help="Name of the DNS zone to dump.")
    parser.add_argument("--csv-file", type=str, required=True, help="CSV file name to write the records to.")
    args = parser.parse_args()

    if "AZURE_SUBSCRIPTION_ID" in os.environ:
        subscription_id = os.environ['AZURE_SUBSCRIPTION_ID']
    elif args.subscription_id is not None:
        subscription_id = args.subscription_id
    else:
        print_error("AZURE_SUBSCRIPTION_ID is a required parameter.")
        sys.exit(1)

    if "AZURE_CLIENT_ID" in os.environ:
        client_id = os.environ['AZURE_CLIENT_ID']
    elif args.client_id is not None:
        client_id = args.client_id
    else:
        print_error("AZURE_CLIENT_ID is a required parameter.")
        sys.exit(1)

    if "AZURE_CLIENT_SECRET" in os.environ:
        client_secret = os.environ['AZURE_CLIENT_SECRET']
    else:
        client_secret = getpass.getpass("client-secret: ")

    if "AZURE_TENANT_ID" in os.environ:
        tenant_id = os.environ['AZURE_TENANT_ID']
    elif args.tenant_id is not None:
        tenant_id = args.tenant_id
    else:
        print_error("AZURE_TENANT_ID is a required parameter.")
        sys.exit(1)

    # Make sure that zone name does not start with "." nor ends with "."
    zone_name = args.zone
    if zone_name.startswith("."):
        zone_name = re.sub(r"^\.", r"", zone_name)
    
    if zone_name.endswith("."):
        zone_name = re.sub(r"\.$", r"", zone_name)

    warnings = []

    credentials = ServicePrincipalCredentials(client_id=client_id, secret=client_secret, tenant=tenant_id)
    dns_client = DnsManagementClient(credentials, subscription_id)

    # Check if zone exists
    try:
        zone = dns_client.zones.get(args.resource_group, zone_name)
    except CloudError as e:
        print(e)
        sys.exit(1)

    try:
        record_sets = dns_client.record_sets.list_all_by_dns_zone(args.resource_group, zone_name)
    except CloudError as e:
        print(e)
        sys.exit(1)

    f = open(args.csv_file, "w")
    
    for record_set in record_sets:
        if record_set.name == "@":
            dns_name = zone_name
        else:
            dns_name = "%s.%s" % (record_set.name, zone_name)
        
        if record_set.arecords is not None:
            for arecord in record_set.arecords:
                csv_row = "%s;%s;A;%s\n" % (dns_name, record_set.ttl, arecord.ipv4_address)
                f.write(csv_row)
        
        if record_set.aaaa_records is not None:
            for aaaa_record in record_set.aaaa_records:
                csv_row = "%s;%s;AAAA;%s\n" % (dns_name, record_set.ttl, aaaa_record.ipv6_address)
                f.write(csv_row)
        
        if record_set.mx_records is not None:
            warnings.append("MX records exist in the zone but MX records are not supported by this tool. Hence this record types are missing in the CSV file.")
        
        if record_set.ns_records is not None:
            for ns_record in record_set.ns_records:
                ref_name = ns_record.nsdname
                if not ref_name.endswith("."):
                    ref_name = "%s.%s." % (ref_name, zone_name)
                
                csv_row = "%s;%s;NS;%s\n" % (dns_name, record_set.ttl, ref_name)
                f.write(csv_row)
        
        if record_set.ptr_records is not None:
            warnings.append("PTR records exist in the zone but PTR records are not supported by this tool. Hence this record types are missing in the CSV file.")
        
        if record_set.srv_records is not None:
            warnings.append("SRV records exist in the zone but SRV records are not supported by this tool. Hence this record types are missing in the CSV file.")
        
        if record_set.txt_records is not None:
            warnings.append("TXT records exist in the zone but TXT records are not supported by this tool. Hence this record types are missing in the CSV file.")
        
        if record_set.cname_record is not None:
            ref_name = record_set.cname_record.cname
            if not ref_name.endswith("."):
                ref_name = "%s.%s." % (ref_name, zone_name)

            csv_row = "%s;%s;CNAME;%s\n" % (dns_name, record_set.ttl, ref_name)
            f.write(csv_row)
        
        if record_set.soa_record is not None:
            host          = record_set.soa_record.host
            email         = record_set.soa_record.email
            serial_number = record_set.soa_record.serial_number
            refresh_time  = record_set.soa_record.refresh_time
            retry_time    = record_set.soa_record.retry_time
            expire_time   = record_set.soa_record.expire_time
            minimum_ttl   = record_set.soa_record.minimum_ttl

            if not host.endswith("."):
                host = "%s.%s." % (host, zone_name)
            
            data = "%s %s %d %d %d %d %d" % (host, email, serial_number, refresh_time, retry_time, expire_time, minimum_ttl)
            csv_row = "%s;%s;SOA;%s\n" % (dns_name, record_set.ttl, data)
            f.write(csv_row)

        if record_set.caa_records is not None:
            warnings.append("CAA records exist in the zone but CAA records are not supported by this tool. Hence this record types are missing in the CSV file.")
    
    f.close()

    if len(warnings) > 0:
        print("")
        print(bcolors.WARNING + bcolors.BOLD + "Warnings:" + bcolors.ENDC)
        for line in warnings:
            print(line)


if __name__ == "__main__":
    main()
