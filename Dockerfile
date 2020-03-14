FROM python:3-alpine

MAINTAINER devsecurity.io <dns-tools@devsecurity.io>

WORKDIR /opt

COPY azure-zone-download/azure-zone-download.py \
azure-zone-upload/azure-zone-upload.py \
dns-zone-transfer-to-csv/dns-zone-transfer-to-csv.py \
exec-python /opt/

RUN chmod 755 /opt/exec-python

RUN for i in /opt/*.py; do ln /opt/exec-python ${i%.*}; done; rm -f /opt/exec-python

COPY usage.py /opt/

RUN apk add --update --no-cache --virtual .build-deps build-base gcc python3-dev libffi-dev openssl-dev && \
python3 -m pip install dnspython && \
python3 -m pip install azure-mgmt-dns && \
apk del .build-deps

ENV PATH="/opt:${PATH}"

CMD [ "python", "usage.py" ]
