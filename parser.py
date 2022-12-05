from libnmap.parser import NmapParser
import pynetbox
from os import environ,path
from datetime import datetime

now = datetime.now()
day = now.strftime("%d/%m/%Y")
day_slug = now.strftime("%d-%m-%Y")
print("Start Execution at: {}".format(now))

if not path.isfile('scan'):
    print("Scan file is not available")
    print("Exiting. Waiting for next execution")
    exit()
print("Parsing Nmap Report")
report = NmapParser.parse_fromfile('scan')
print("Connecting to Netbox")
nb = pynetbox.api(environ.get('NETBOX_ADDRESS'), environ.get('NETBOX_TOKEN'))
print("Checking for netbox tag")
if not nb.extras.tags.get(name="nmap2netbox"):
    print("Creating nmap2netbox tag!")
    n2n_tag = nb.extras.tags.create(name="nmap2netbox", slug="n2n")
    print ("Created new tag for nmap2netbox with id: {}".format(n2n_tag.id))
else:
    n2n_tag = nb.extras.tags.get(name="nmap2netbox")
if not nb.extras.tags.get(name=day):
    print("Daily tag does not exist. Creating new")
    tag = nb.extras.tags.create(name=day, slug=day_slug)
    print("Created new daily tag with ID: {}".format(tag.id))
else:
    tag = nb.extras.tags.get(name=day)
    print("Daily tag already exists. Using tag with id: {}".format(tag.id))
for hosts in report.hosts:
    print("Working on IP: "+hosts.address)
    address_cidr = hosts.address+"/32"
    try:
        nb_ip_obj = nb.ipam.ip_addresses.get(q=address_cidr)
    except:
        print("Could not get IP from Netbox")
    if address_cidr == str(nb_ip_obj):
        if not n2n_tag in nb_ip_obj.tags:
            print("Address manually added to netbox. Doing nothing")
        else:
            print("Address already in netbox. Updating")
            nb_ip_obj.tags += [{'name': day}]
            nb_ip_obj.description = str(hosts.get_open_ports())
            nb_ip_obj.save()
    else:
        print("Address not in Netbox Creating new")
        nb_ip_obj =  nb.ipam.ip_addresses.create(address=address_cidr, tags=[{"id": tag.id},{"id": n2n_tag.id}], description=str(hosts.get_open_ports()))

    if hosts.hostnames:
        nb_ip_obj.dns_name = str(hosts.hostnames[0])
        nb_ip_obj.save()

print("Execution finished")

