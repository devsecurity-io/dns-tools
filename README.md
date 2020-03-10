# DNS Tools

**DNS Tools** is a collection of tools which were created while executing a
migration of a larger DNS system.

| Tool                         | Purpose |
|:-----------------------------|:--------|
| **azure-zone-download**      | Download DNS records sets from an Azure DNS zone and save it as CSV file. |
| **azure-zone-upload**        | Upload DNS records sets to an Azure DNS zone from a CSV file. |
| **dns-zone-transfer-to-csv** | Download DNS record sets from a DNS server which supports DNS zone transfers and saves them in a CSV file. |

Each tool is located in its own sub directory of this repository and contains a
dedicated README file with details about the tool.

## CSV File Format

Most of the **DNS Tools** deal with CSV files. They expect CSV files with
records adhering to the following format (in EBNF syntax):

```CSV_ROW = DNS_NAME, ";", <TTL>, ";", RECORD_TYP, ";", RECORD_DATA ;```

- **DNS_NAME**

  Fully Qualified DNS Name (FQDN) wihtout a trailing dot "."

- **TTL**

  Time to Live (TTL) of the corresponding DNS record set

- **RECORD_TYPE**

  Record type, e.g. A, AAAA, CNAME, NS, SOA, ...

- **RECORD_DATA**

  The format of the data associated with a DNS record is specific to the record
  type.

  | Record Type | Format of Record Data                                            |
  |:------------|:-----------------------------------------------------------------|
  | A           | IP Address                                                       |
  | AAAA        | IPv6 Address                                                     |
  | CNAME       | Fully Qualified DNS Name (FQDN) terminated with trailing dot "." |
  | NS          | Fully Qualified DNS Name (FQDN) terminated with trailing dot "." |
  | SOA         | SOA_RECORD_DATA = SOA_HOST, " ", SERIAL_NUMBER, " ", REFRESH_TIME, " ", RETRY_TIME, " ", EXPIRE_TIME, " ", MINIMUM_TTL ; |

Please note: If references in CNAME and NS record sets are not terminated with
a trailing dot then unexpected results can occur.

## Contributing

If you consider the tools in this repository to be useful and would like to
contribute please create a pull request.

## Authors

- **[Matthias Dettling](mailto:md@devsecurity.io)**

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE)
file for details.
