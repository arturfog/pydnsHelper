FROM python:3.6-alpine

LABEL maintainer "Artur Fogiel"

RUN pip install dnslib==0.9.7
RUN pip install getdns==1.0.0b1
RUN pip install urllib3==1.22

RUN mkdir /home/root/pyDNSHelper
#ADD ./main.py /home/root/main.py

EXPOSE 53/tcp
EXPOSE 53/udp
CMD ["/home/root/main.py"]
