from django.shortcuts import render
from django.http import Http404

from libs.hosts_sources import HostsSourcesUtils
from libs.hosts_manager import HostsManager
from libs.dnsserver import SecureDNSServer

from webui.models import Host
#####################################################################################
def index(request):
    """View function for home page of site."""

    num_hosts = Host.objects.all().count()
    hosts = Host.objects.all()
    context = {
        'num_hosts': num_hosts,
        'hosts': hosts
    }
    return render(request, 'index.html', context=context)
#####################################################################################
def genhosts(request):
    hm = HostsManager()
    hm.generate_host_file("/tmp/hosts.txt")
    return index(request)
#####################################################################################
def startttl(request):
    hm = HostsManager()
    hm.start_ttl_monitoring()
    return index(request)
#####################################################################################
def status(request):
    """View function for home page of site."""
    num_hosts = Host.objects.all().count()
    context = {
        'num_hosts': num_hosts,
    }
    return render(request, 'status.html', context=context)
#####################################################################################
def logs(request):
    """View function for home page of site."""
    num_hosts = Host.objects.all().count()
    context = {
        'num_hosts': num_hosts,
    }
    return render(request, 'logs.html', context=context)
#####################################################################################
def about(request):
    """View function for home page of site."""
    num_hosts = Host.objects.all().count()
    context = {
        'num_hosts': num_hosts,
    }
    return render(request, 'about.html', context=context)
#####################################################################################
def hosts(request):
    """View function for home page of site."""
    num_hosts = Host.objects.all().count()
    context = {
        'num_hosts': num_hosts,
    }
    return render(request, 'hosts.html', context=context)