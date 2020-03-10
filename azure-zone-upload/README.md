# azure-zone-upload

*azure-zone-upload* is a tool to add zone information to Azure DNS zones. It
reads records from a CSV file and adds them to a DNS zone via the Azure API. 
To avoid harm records already existing in the zone are skipped and a warning
message is shown.

## Getting Started

The instructions below will help you to run *azure-zone-upload* on your system.

### Prerequisites

First install the prerequisites:

**TODO**

### Download Source Code

Download **DNS Tools** to your system:

```bash
git clone https://github.com/devsecurity-io/dns-tools.git
```

### Usage

Before *azure-zone-upload* can be used, a service principal with appropriate
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

In order to upload zone information to an Azure DNS zone execute
*azure-zone-upload* and supply it with the CSV file to be uploaded and the
respective Azure DNS zone as parameters:

```bash
python azure-zone-upload.py --tenant-id <tenant id> --subscription-id <subscription id> --resource-group <resource group> --client-id <client id> --zone <zone name> --csv-file <filename>
```

## Known Limitations

- *azure-zone-upload* can only handle the following DNS record types:
  - A
  - AAAA
  - CNAME

  Other record types are not supported by *azure-zone-upload*. If such records
  exist in a CSV file provided a warning is displayed.

In case you have modified *azure-zone-upload* to support more record types
please share it with the community and create a pull request.

## Contributing

If you consider *azure-zone-upload* to be useful and would like to contribute
please create a pull request. This especially makes sense if you are facing the following error message:

``Record(s) of type <type> in CSV file which is currently not supported by the tool. Please handle records manually.``

## Authors

- **[Matthias Dettling](md@devsecurity.io)**

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE)
file for details.
