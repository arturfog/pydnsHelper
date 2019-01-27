from django.contrib import admin
from django.http import HttpResponseRedirect
from django.urls import include, path

from webui.models import Host
from webui.models import HostSources
from webui.models import Logs
from webui.models import Traffic
from libs.hosts_sources import HostsSourcesUtils
from libs.hosts_manager import HostsManager
from libs.dnsserver import SecureDNSServer
# Register your models here.

class HostSourcesAdmin(admin.ModelAdmin):
    #change_list_template = "entities/host_sources_changelist.html"
    search_fields = ('url',)

class HostAdmin(admin.ModelAdmin):
    list_display = ('url', 'ip', 'ttl', 'hits')
    #list_filter = ('url', 'ttl')
    search_fields = ('url', )

class LogsAdmin(admin.ModelAdmin):
    list_display = ('msg', 'timestamp')
    search_fields = ('msg', )

class TrafficAdmin(admin.ModelAdmin):
    list_display = ('hits', 'date')
    search_fields = ('date', )

admin.site.register(Host, HostAdmin)
admin.site.register(HostSources, HostSourcesAdmin)
admin.site.register(Logs, LogsAdmin)
admin.site.register(Traffic, TrafficAdmin)
#admin.site.add_action(HostsSourcesUtils.download_hosts)