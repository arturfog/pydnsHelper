from django.shortcuts import render
from django.http import Http404
from django.contrib.auth.decorators import login_required

from libs.hosts_sources import HostsSourcesUtils
from libs.hosts_manager import HostsManager
from libs.dnsserver import SecureDNSServer

from webui.models import Host
from webui.models import HostSources
from webui.models import Logs
#####################################################################################
def index(request):
    """View function for home page of site."""

    num_hosts = Host.objects.all().count()
    hosts = Host.objects.all() 
    num_logs = Logs.objects.all().count()
    context = {
        'num_hosts': num_hosts,
        'hosts': hosts,
        'num_logs': num_logs
    }
    return render(request, 'index.html', context=context)
#####################################################################################
def genhosts(request):
    hm = HostsManager()
    hm.generate_host_file("/tmp/hosts.txt")
    return index(request)
#####################################################################################
def isServerRunning(request):
    isRunning = SecureDNSServer.isRunning()
    return HttpResponse(str(isRunning))
#####################################################################################
def isTTLRunning(request):
    isRunning = SecureDNSServer.isRunning()
    return HttpResponse(str(isRunning))
#####################################################################################
@login_required
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
    logs = Logs.objects.all()
    num_logs = Logs.objects.all().count()
    context = {
        'logs': logs,
        'num_logs': num_logs
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
    sources = HostSources.objects.all()
    context = {
        'num_hosts': num_hosts,
        'sources': sources
    }
    return render(request, 'hosts.html', context=context)