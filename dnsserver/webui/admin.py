from django.contrib import admin
from django.http import HttpResponseRedirect
from django.urls import include, path

from webui.models import Host, IPv4, IPv6
from webui.models import HostSources
from webui.models import Logs
from libs.hosts_sources import HostsSourcesUtils
from libs.hosts_manager import HostsManager
from libs.dnsserver import SecureDNSServer
# Register your models here.

class HostSourcesAdmin(admin.ModelAdmin):
    #change_list_template = "entities/host_sources_changelist.html"
    search_fields = ('url',)

class HostAdmin(admin.ModelAdmin):
    list_display = ('url', 'comment', 'created', 'hits', 'blocked')
    #list_filter = ('url', 'ttl')
    search_fields = ('url', )

class IPv4Admin(admin.ModelAdmin):
    list_display = ('host', 'ip', 'ttl')
    search_fields = ('ip', )

class IPv6Admin(admin.ModelAdmin):
    list_display = ('host', 'ip', 'ttl')
    search_fields = ('ip', )

class LogsAdmin(admin.ModelAdmin):
    list_display = ('msg', 'timestamp')
    search_fields = ('msg', )

admin.site.register(Host, HostAdmin)
admin.site.register(HostSources, HostSourcesAdmin)
admin.site.register(Logs, LogsAdmin)
admin.site.register(IPv4, IPv4Admin)
admin.site.register(IPv6, IPv6Admin)