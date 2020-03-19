# azure-zone-upload

`azure-zone-upload` is a tool to add zone information to Azure DNS zones. It
reads records from a CSV file and adds them to a DNS zone via the Azure API. 
To avoid harm records already existing in the zone are skipped and a warning
is displayed.

## Getting Started

The instructions below will guide you through the process of installing
`azure-zone-upload` and its dependencies on your local system. If you intend
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

Before `azure-zone-upload` can be used, a service principal with appropriate
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

In order to upload zone information from a CSV file to Azure DNS executing
`azure-zone-upload` on your local system the command syntax is as follows:

```bash
python azure-zone-upload.py --tenant-id <tenant id> --subscription-id <subscription id> --resource-group <resource group> --client-id <client id> --zone <zone name> --csv-file <filename>
```

When using the Docker image, the command syntax is as follows:

```bash
docker run --rm -i -t -v <local volume>:<container volume> devsecurity/dns-tools:latest azure-zone-upload --tenant-id <tenant id> --subscription-id <subscription id> --resource-group <resource group> --client-id <client id> --zone <zone name> --csv-file <filename>
```

## Known Limitations

- At the moment `azure-zone-upload` can only handle the following DNS record
types:
  - A
  - AAAA
  - CNAME

  Other record types are not supported at the moment. If such records exist in
  the CSV file provided, a warning is displayed.

In case you have modified `azure-zone-upload` to support more record types,
please share it with the community and create a pull request.

## Contributing

If you consider `azure-zone-upload` to be useful and would like to contribute,
please create a pull request. This especially makes sense if you are facing the following error message:

`Record(s) of type <type> in CSV file which is currently not supported by the tool. Please handle records manually.`

## Authors

- **[Matthias Dettling](mailto:md@devsecurity.io)**

## License

This project is licensed under the MIT License - see the [LICENSE](../LICENSE)
file for details.
