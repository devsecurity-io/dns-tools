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
import re
import sys

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


def create_zone_dict_from_csv_file(csv_filename):
    f = open(csv_filename, "r")
    lines = f.readlines()
    f.close()

    lines = [ x.rstrip() for x in lines ]

    zone_dict = {}
    for line in lines:
        x = line.split(';')

        if len(x) != 4:
            print_error("Invalid CSV provided!")
            sys.exit(1)

        dns_name = x[0]
        ttl = x[1]
        rtype = x[2]
        data = x[3]

        if dns_name in zone_dict:
            zone_dict[dns_name].append({"ttl": ttl, "type": rtype, "data": data})
        else:
            zone_dict[dns_name] = [ {"ttl": ttl, "type": rtype, "data": data} ]

    return zone_dict


def main():
    # Parse arguments
    parser = argparse.ArgumentParser(description="Tool to upload DNS records to Azure DNS zones.", add_help=True)
    parser.add_argument("--tenant-id", type=str, required=False, help="Azure tenant ID.")
    parser.add_argument("--subscription-id", type=str, required=False, help="Azure subscription ID.")
    parser.add_argument("--resource-group", type=str, required=True, help="Azure resource group of the DNS zone.")
    parser.add_argument("--client-id", type=str, required=False, help="Client ID of service principal.")
    parser.add_argument("--zone", type=str, required=True, help="Name of the DNS zone to create records in.")
    parser.add_argument("--csv-file", type=str, required=True, help="CSV file with DNS records to be created.")
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
    errors = []
    records_created = []


    credentials = ServicePrincipalCredentials(client_id=client_id, secret=client_secret, tenant=tenant_id)
    dns_client = DnsManagementClient(credentials, subscription_id)

    # Check if zone exists
    try:
        dns_client.zones.get(args.resource_group, zone_name)
    except CloudError as e:
        print(e)
        sys.exit(1)
    
    # Read zone from CSV file and create dict
    zone_dict = create_zone_dict_from_csv_file(args.csv_file)

    dns_names_sorted = zone_dict.keys()

    # Filter records in CSV file. Keep only those matching zone postfix.
    dns_names_filtered = []
    for dns_name in dns_names_sorted:
        m = re.search(r"(^|\.)%s$" % zone_name, dns_name)
        if m is not None:
            dns_names_filtered.append(dns_name)
    dns_names_sorted = dns_names_filtered

    # Sort names
    dns_names_sorted.sort()

    # Check record types in CSV file
    record_types_in_zone = set([])
    for dns_name in dns_names_sorted:
        records = zone_dict[dns_name]
        for record in records:
            record_types_in_zone.add(record["type"])
    
    record_types_supported = [ "A", "AAAA", "CNAME" ]

    for record_type in record_types_in_zone:
        if record_type not in record_types_supported:
            warnings.append("Record(s) of type %s in CSV file which is currently not supported by the tool. Please handle records manually." % record_type)

    # Update Azure zone
    for dns_name in dns_names_sorted:
        name = re.sub(r"(^|\.)%s$" % zone_name, r"", dns_name)
        if name == "":
            name = "@"

        a_record_set = { "ttl": 0, "data": [] }
        aaaa_record_set = { "ttl": 0, "data": [] }
        cname_record_set = { "ttl": 0, "data": [] }

        records = zone_dict[dns_name]
        for record in records:
            if record["type"] == "A":
                # Assumption: TTL is the same for each entry of a DNS record set.
                # Thus, we take the last occurence.
                a_record_set["ttl"] = record["ttl"]
                a_record_set["data"].append(record["data"])

            elif record["type"] == "AAAA":
                # Assumption: TTL is the same for each entry of a DNS record set.
                # Thus, we take the last occurence.
                aaaa_record_set["ttl"] = record["ttl"]
                aaaa_record_set["data"].append(record["data"])

            elif record["type"] == "CNAME":
                # Assumption: TTL is the same for each entry of a DNS record set.
                # Thus, we take the last occurence.
                cname_record_set["ttl"] = record["ttl"]

                ref_name = record["data"]
                # Azure DNS seems to not support relative names
                if not ref_name.endswith("."):
                    ref_name_old = ref_name
                    ref_name = "%s.%s." % (ref_name, zone_name)
                    warnings.append("Name %s referenced by CNAME record %s is not terminated with a dot (\".\"). This might cause unexpected behavior in Azure DNS. Hence, zone name was added to the name: %s" % (ref_name_old, name, ref_name))
                
                cname_record_set["data"].append(ref_name)
            
        if a_record_set["data"] != []:
            data = [ { "ipv4_address": x } for x in a_record_set["data"] ]

            record_set = {
                "ttl": a_record_set["ttl"],
                "arecords": data
            }

            # Get record to check if it is already existing
            record_exists = False
            try:
                dns_client.record_sets.get(args.resource_group, zone_name, name, "A")
                record_exists = True
            except CloudError as e:
                pass
            
            # Create record
            if record_exists == False:
                try:
                    dns_client.record_sets.create_or_update(args.resource_group, zone_name, name, "A", record_set)
                except CloudError as e:
                    errors.append("Error while creating record set A for name %s." % name)

                for x in a_record_set["data"]:
                    records_created.append("%s;%s;A;%s" % (name, a_record_set["ttl"], x))
            else:
                warnings.append("Record set A for name %s already exists. Skipping record set." % name)
        

        if aaaa_record_set["data"] != []:
            data = [ { "ipv6_address": x } for x in aaaa_record_set["data"] ]

            record_set = {
                "ttl": aaaa_record_set["ttl"],
                "aaaarecords": data
            }

            # Get record to check if it is already existing
            record_exists = False
            try:
                dns_client.record_sets.get(args.resource_group, zone_name, name, "AAAA")
                record_exists = True
            except CloudError as e:
                pass
            
            # Create record
            if record_exists == False:
                try:
                    dns_client.record_sets.create_or_update(args.resource_group, zone_name, name, "AAAA", record_set)
                except CloudError as e:
                    errors.append("Error while creating record set AAAA for name %s." % name)

                for x in aaaa_record_set["data"]:
                    records_created.append("%s;%s;AAAA;%s" % (name, aaaa_record_set["ttl"], x))
            else:
                warnings.append("Record set AAAA for name %s already exists. Skipping record set." % name)
        

        if cname_record_set["data"] != []:
            if len(cname_record_set["data"]) > 1:
                errors.append("More than one alias in CNAME record set for name %s. This is not valid! Record set skipped." % name)
            else:
                record_set = {
                    "ttl": cname_record_set["ttl"],
                    "cname_record": {
                        "cname": cname_record_set["data"][0]
                    }
                }

                # Get record to check if it is already existing
                record_exists = False
                try:
                    dns_client.record_sets.get(args.resource_group, zone_name, name, "CNAME")
                    record_exists = True
                except CloudError as e:
                    pass
                
                # Create record
                if record_exists == False:
                    try:
                        dns_client.record_sets.create_or_update(args.resource_group, zone_name, name, "CNAME", record_set)
                    except CloudError as e:
                        errors.append("Error while creating record set CNAME for name %s." % name)

                    records_created.append("%s;%s;CNAME;%s" % (name, cname_record_set["ttl"], cname_record_set["data"][0]))
                else:
                    warnings.append("Record set CNAME for name %s already exists. Skipping record set." % name)

    # Output
    if len(records_created) > 0:
        print("")
        print(bcolors.OKGREEN + bcolors.BOLD + "Record sets successfully created:" + bcolors.ENDC)
        for line in records_created:
            print(line)

    if len(warnings) > 0:
        print("")
        print(bcolors.WARNING + bcolors.BOLD + "Warnings:" + bcolors.ENDC)
        for line in warnings:
            print(line)
    
    if len(errors) > 0:
        print("")
        print(bcolors.FAIL + bcolors.BOLD + "Errors:" + bcolors.ENDC)
        for line in errors:
            print(line)


if __name__ == "__main__":
    main()
