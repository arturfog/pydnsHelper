from django.shortcuts import render
from django.http import Http404

from libs.hosts_sources import HostsSourcesUtils
from libs.hosts_manager import HostsManager
from libs.dnsserver import SecureDNSServer
# Create your views here.

from webui.models import Host
def index(request):
    """View function for home page of site."""

    # Generate counts of some of the main objects
    num_hosts = Host.objects.all().count()

    context = {
        'num_hosts': num_hosts,
    }

    # Render the HTML template index.html with the data in the context variable
    return render(request, 'index.html', context=context)

def genhosts(request):

    # Generate counts of some of the main objects
    num_hosts = Host.objects.all().count()

    context = {
        'num_hosts': num_hosts,
    }

    hm = HostsManager()
    hm.generate_host_file("/tmp/hosts.txt")
    #self.message_user(request, "Hosts file generated")
    return render(request, 'index.html', context=context)

def startttl(request):

    # Generate counts of some of the main objects
    num_hosts = Host.objects.all().count()

    context = {
        'num_hosts': num_hosts,
    }

    hm = HostsManager()
    hm.start_ttl_monitoring()
    #self.message_user(request, "TTL monitor started")
    return render(request, 'index.html', context=context)