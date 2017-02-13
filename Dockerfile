FROM python:3.6.0-alpine

ENV DOCUMENT_PATH=/var/lib/mayan

COPY . /tmp/mayan-deduplicate/

RUN set -ex \
 && pip install /tmp/mayan-deduplicate/ \
 && rm -rf /tmp/mayan-deduplicate

ENTRYPOINT ["mayan-deduplicate"]
