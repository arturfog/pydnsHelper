FROM python:3.7-stretch

LABEL maintainer "Artur Fogiel"

RUN apt-get update
RUN apt-get install -y gcc g++
RUN apt-get install -y libgetdns-dev
RUN pip install certifi>=2018.10.15
RUN pip install chardet>=3.0.4
RUN pip install Django>=2.1.5
RUN pip install dnslib>=0.9.7
RUN pip install getdns>=1.0.0b1
RUN pip install idna>=2.7
RUN pip install pytz>=2018.7
RUN pip install requests>=2.20.1
RUN pip install urllib3>=1.24.1

RUN mkdir /pyDNSHelper
ADD ./dnsserver /pyDNSHelper

# webui
EXPOSE 8000/tcp
# dns
EXPOSE 5053/udp

#default password: 'dnsmanager'
CMD ["/home/root/pyDNSHelper/dnsserver/manage.py", "runserver", "0.0.0.0:8000"]

