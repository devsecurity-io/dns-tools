# dns-zone-transfer-to-csv

`dns-zone-transfer-to-csv` is a tool to dump DNS zones to CSV files. For that
the tool initiates a DNS zone transfer with the specified server and writes the
records received into a CSV file.

## Getting Started

The instructions below will guide you through the process of installing
`dns-zone-transfer-to-csv` and its dependencies on your local system. If you
intend to use the Docker container, you can skip this section and go directly
to the [usage](#usage) section.


### Prerequisites

First install the prerequisites:

#### Python 2

```bash
python -m pip install dnspython
```

#### Python 3

```bash
python3 -m pip install dnspython
```

### Download Source Code

Then download **DNS Tools** to your system:

```bash
git clone https://github.com/devsecurity-io/dns-tools.git
```

### Usage

In order to download a DNS zone from a server and to write it to a CSV file
executing `dns-zone-transfer-to-csv` on your local system the command syntax is as follows:

```bash
python dns-zone-transfer-to-csv.py --server <server> --zone <zone name> --csv-file <filename>
```

When using the Docker image, the command syntax is as follows:

```bash
docker run --rm -i -t -v <local volume>:<container volume> devsecurity/dns-tools:latest dns-zone-transfer-to-csv --server <server> --zone <zone name> --csv-file <filename>
```

## Known Limitations

- At the moment `dns-zone-transfer-to-csv` can only handle the following DNS
record types:
  - A
  - AAAA
  - CNAME
  - NS
  - SOA
- TSIG protected zone transfers are not yet supported.

In case you have modified `dns-zone-transfer-to-csv` to support more record
types please share it with the community and create a pull request.

## Contributing

If you consider `dns-zone-transfer-to-csv` to be useful and would like to
contribute please create a pull request. This especially makes sense if you are
facing the following error message:

`Record type not implemented.`

## Authors

- **[Matthias Dettling](mailto:md@devsecurity.io)**

## License

This project is licensed under the MIT License - see the [LICENSE](../LICENSE)
file for details.
