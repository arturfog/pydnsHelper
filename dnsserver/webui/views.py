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
from django.shortcuts import redirect
from django.db import connection

def db_table_exists(table_name):
    return table_name in connection.introspection.table_names()
#####################################################################################
def index(request):
    """View function for home page of site."""

    num_hosts = 0
    num_logs = 0
    hosts = None
    if db_table_exists("webui_host"):
        num_hosts = Host.objects.all().count()
        hosts = Host.objects.filter(hits__gt=1).order_by('-hits')
        num_logs = Logs.objects.all().count()

    context = {
        'num_hosts': num_hosts,
        'hosts': hosts,
        'num_logs': num_logs,
        'server_status': SecureDNSServer.isRunning(),
        'ttl_status': HostsManager.isTTLThreadRunning()
    }
    return render(request, 'index.html', context=context)
#####################################################################################
def gen_hosts(request):
    filename = "/tmp/__hosts.txt"
    hm = HostsManager()
    hm.generate_host_file(filename)

    from wsgiref.util import FileWrapper

    with open(filename, "r", encoding="utf-8") as myfile:
        # generate the file
        response = HttpResponse(FileWrapper(myfile), content_type='text/plain')
        response['Content-Disposition'] = 'attachment; filename=hosts.txt'
        return response
    return HttpResponse("error")
#####################################################################################
def download_hosts(request):
    HostsSourcesUtils.download_hosts()
    return HttpResponse("done")
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

    logs = None
    num_logs = 0
    if db_table_exists("webui_logs"):
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
    return render(request, 'about.html')
#####################################################################################
def hosts(request):
    """View function for home page of site."""
    num_hosts = 0
    sources = None
    if db_table_exists("webui_host") == True:
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
#####################################################################################
@login_required
def clear_logs(request):
    Logs.objects.all().delete()
    return HttpResponse("done")
#####################################################################################
@login_required
def export_logs(request):
    logs = Logs.objects.all()

    from io import StringIO
    myfile = StringIO()
    for log in logs:
        myfile.write(str(log))

    print(myfile.getvalue())
    # generate the file
    response = HttpResponse(myfile.getvalue(), content_type='text/plain')
    response['Content-Disposition'] = 'attachment; filename=logs.txt'
    return response
