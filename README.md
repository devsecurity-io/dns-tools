# DNS Tools

**DNS Tools** is a collection of tools which were created while executing a
migration of a larger DNS system.

| Tool                     | Purpose |
|:-------------------------|:--------|
| azure-zone-download      | Download DNS records sets from an Azure DNS zone and save them to a CSV file. |
| azure-zone-upload        | Upload DNS records sets to an Azure DNS zone from a CSV file. |
| dns-zone-transfer-to-csv | Download DNS record sets from a DNS server which supports DNS zone transfers and save them to a CSV file. |

Each tool is located in an individual sub directory of this repository.

## Getting Started

In order to get started please refer to the README file of the respective tool.
There is described how to install each tool on your local system and how to use
it.

Please note that there is also a Docker container available which bundles all
the tools above, together with their dependencies:

`devsecurity/dns-tools`

## Usage

Depending if executed locally or via Docker the call syntax is different. If
executed locally then tools are usually called as follows:

```bash
python <script name> <script parameters>
```

The exact call syntax for each tool is described in the respective README file
of the tool.

If you prefer to use the Docker container then execution syntax is as follows:

```bash
$ docker run --rm -i -t -v <local volume>:<container volume> devsecurity/dns-tools:latest
Usage: docker run --rm -i -v <local volume>:<container volume> devsecurity/dns-tools:<tag> <command> <command parameters>

Tags:
	latest

Commands:
	dns-zone-transfer-to-csv
	azure-zone-upload
	azure-zone-download
```

Please note the parameter `-t`. It implies that Docker will allocate a
pseudo-tty for the container. If this parameter is omitted then passwords will
be echoed to the terminal.

Since most of the tools deal with CSV files on your local system also don't
forget to map a local volume into the Docker container. Otherwiese Docker will
not be able to access files on your local system. Syntax for that is:

```
-v <local volume>:<container volume>
```

Example:

```
-v /Users:/Users
```

Similarly as when executed locally, the exact script paramters for each tool
can be found in the respective README file.

### CSV File Format

Most of the **DNS Tools** deal with CSV files. They expect CSV files with
records adhering to the following format (in EBNF syntax):

```CSV_ROW = DNS_NAME, ";", <TTL>, ";", RECORD_TYP, ";", RECORD_DATA ;```

#### DNS_NAME

Fully Qualified DNS Name (FQDN) wihtout a trailing dot "."

#### TTL

Time to Live (TTL) of the corresponding DNS record set

#### RECORD_TYPE

Record type, e.g. A, AAAA, CNAME, NS, SOA, ...

#### RECORD_DATA

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
