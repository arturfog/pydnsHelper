FROM python:3.6-alpine

LABEL maintainer "Artur Fogiel"

RUN pip install certifi>=2018.10.15
RUN pip install chardet>=3.0.4
RUN pip install Django>=2.1.5
RUN pip install dnslib==0.9.7
RUN pip install getdns==1.0.0b1
RUN pip install idna==2.7
RUN pip install pkg-resources==0.0.0
RUN pip install pytz>=2018.7
RUN pip install requests>=2.20.1
RUN pip install urllib3>=1.24.1

RUN mkdir /home/root/pyDNSHelper
ADD ./dnsserver /home/root/pyDNSHelper/

EXPOSE 53/tcp
EXPOSE 53/udp

#default password: 'dnsmanager'
CMD ["/home/root/pyDNSHelper/dnsserver/manage.py", "runserver"]
