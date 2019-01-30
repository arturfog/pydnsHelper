from django.shortcuts import render
from django.http import Http404
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required

from libs.hosts_sources import HostsSourcesUtils
from libs.hosts_manager import HostsManager
from libs.dnsserver import SecureDNSServer

from webui.models import Host
from webui.models import HostSources
from webui.models import Logs
from webui.models import Traffic

from django.shortcuts import redirect

#####################################################################################
def index(request):
    """View function for home page of site."""

    num_hosts = Host.objects.all().count()
    hosts = Host.objects.filter(hits__gt=0).order_by('hits')
    num_logs = Logs.objects.all().count()
    traffic = Traffic.objects.all()
    context = {
        'num_hosts': num_hosts,
        'hosts': hosts,
        'num_logs': num_logs,
        'traffic': traffic
    }
    return render(request, 'index.html', context=context)
#####################################################################################
def gen_hosts(request):
    hm = HostsManager()
    hm.generate_host_file("/tmp/hosts.txt")
    return index(request)
#####################################################################################
def download_hosts(request):
    HostsSourcesUtils.download_hosts()
    return HttpResponse("downloaded")
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
def start_ttl(request):
    hm = HostsManager()
    hm.start_ttl_monitoring()
    return HttpResponse("done")
#####################################################################################
def status(request):
    """View function for home page of site."""
    context = {
        'server_status': SecureDNSServer.isRunning(),
        'ttl_status': HostsManager.isTTLThreadRunning()
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
#####################################################################################
def import_sources(request):
    HostsSourcesUtils.load_sources_urls()
    return HttpResponse("done")
#####################################################################################
def import_hosts(request):
    hm = HostsManager()
    hm.import_host_files("/tmp/hosts/")
    return HttpResponse("done")
#####################################################################################
@login_required
def start_server(request):
    SecureDNSServer.start()
    return HttpResponse("done")