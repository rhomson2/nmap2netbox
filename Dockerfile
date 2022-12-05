FROM python:alpine

WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
RUN apk add --no-cache nmap
COPY parser.py parser.py
COPY nmap2netbox-cron /etc/cron.d/nmap2netbox

RUN chmod 0644 /etc/cron.d/nmap2netbox
RUN crontab /etc/cron.d/nmap2netbox

#CMD crond -f -d 0
CMD crond -f -l 2
