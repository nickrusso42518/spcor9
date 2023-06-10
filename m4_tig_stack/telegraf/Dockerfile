FROM telegraf:latest
MAINTAINER Mateusz Trojak <mateusz.trojak@gmail.com>
LABEL version="1.1"
LABEL description="Telegraf docker image with custom setup"

USER root

ADD telegraf.conf /etc/telegraf/telegraf.conf
RUN chmod 0666 /etc/telegraf/telegraf.conf

ADD mibs /usr/share/snmp/mibs

#CMD ["telegraf -config /etc/telegraf/telegraf.conf"]
CMD ["telegraf"]
