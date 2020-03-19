# azure-zone-download

`azure-zone-download` is a tool to dump Azure DNS zones into CSV files. The
tool uses the Azure API to retrieve zone information from Azure DNS and writes
the records received into a CSV file.

## Getting Started

The instructions below will guide you through the process of installing
`azure-zone-download` and its dependencies on your local system. If you intend
to use the Docker container, you can skip this section and go directly to the
[usage](#usage) section.

### Prerequisites

First install the prerequisites:

#### Python 2

```bash
python -m pip install  azure-mgmt-dns
```

#### Python 3

```bash
python3 -m pip install azure-mgmt-dns
```

### Download Source Code

Then download **DNS Tools** to your system:

```bash
git clone https://github.com/devsecurity-io/dns-tools.git
```

### Usage

Before `azure-zone-download` can be used, a service principal with appropriate
permissions is need. The following command creates a service principal with the
role "DNS Zone Contributor" scoped to a given subscription:

```bash
SERVICE_PRINCIPAL_NAME="dns-zone-contributor"
SUBSCRIPTION_ID="<id of the subscription>"
SP_PASSWD=$(az ad sp create-for-rbac --name "http://${SERVICE_PRINCIPAL_NAME}" --role "DNS Zone Contributor" --scopes /subscriptions/${SUBSCRIPTION_ID} --query password --output tsv)
SP_APP_ID=$(az ad sp show --id "http://${SERVICE_PRINCIPAL_NAME}" --query appId --output tsv)
echo "Client ID: ${SP_APP_ID}"
echo "Client Secret: ${SP_PASSWD}"
```

In order to download a zone from Azure DNS and to write it to a CSV file executing `azure-zone-download` on your local system the command syntax is as follows:

```bash
python azure-zone-download.py --tenant-id <tenant id> --subscription-id <subscription id> --resource-group <resource group> --client-id <client id> --zone <zone name> --csv-file <filename>
```

When using the Docker image, the command syntax is as follows:

```bash
docker run --rm -i -t -v <local volume>:<container volume> devsecurity/dns-tools:latest azure-zone-download --tenant-id <tenant id> --subscription-id <subscription id> --resource-group <resource group> --client-id <client id> --zone <zone name> --csv-file <filename>
```

## Known Limitations

- `azure-zone-download` can only handle the following DNS record types:
  - A
  - AAAA
  - CNAME
  - NS
  - SOA

- Additionally, the following record types are supported by Azure DNS:
  - CAA
  - MX
  - PTR
  - SRV
  - TXT

  These record types are recognized by `azure-zone-download` but are not
  supported. If such a record exists in a zone downloaded then a warning is
  displayed.

In case you have modified `azure-zone-download` to support more record types
please share it with the community and create a pull request.

## Contributing

If you consider `azure-zone-download` to be useful and would like to contribute
please create a pull request. This especially makes sense if you are facing one
of the following error messages:

- `CAA records exist in the zone but CAA records are not supported by this tool. Hence this record types are missing in the CSV file.`
- `MX records exist in the zone but MX records are not supported by this tool. Hence this record types are missing in the CSV file.`
- `PTR records exist in the zone but PTR records are not supported by this tool. Hence this record types are missing in the CSV file.`
- `SRV records exist in the zone but SRV records are not supported by this tool. Hence this record types are missing in the CSV file.`
- `TXT records exist in the zone but TXT records are not supported by this tool. Hence this record types are missing in the CSV file.`

## Authors

- **[Matthias Dettling](mailto:md@devsecurity.io)**

## License

This project is licensed under the MIT License - see the [LICENSE](../LICENSE)
file for details.
