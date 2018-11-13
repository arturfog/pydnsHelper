from django.contrib import admin
from django.http import HttpResponseRedirect
from django.urls import include, path

from webui.models import Host
from webui.models import HostSources
from libs.hosts_sources import HostsSourcesUtils
from libs.hosts_manager import HostsManager
from libs.dnsserver import SecureDNSServer
# Register your models here.


class HostSourcesAdmin(admin.ModelAdmin):
    change_list_template = "entities/host_sources_changelist.html"
    search_fields = ('url',)

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('importsources/', self.import_sources),
            path('importhosts/', self.import_hosts),
            path('downloadhosts/', self.download_hosts),
            path('genhosts/', self.gen_hosts),
            path('ttlmonitor/', self.start_ttlmonitor),
            path('start/', self.start_server),
        ]

        return my_urls + urls

    def import_sources(self, request):
        #self.model.objects.all().update(is_immortal=True)
        HostsSourcesUtils.load_sources_urls()
        self.message_user(request, "All hosts files URL's imported")
        return HttpResponseRedirect("../")

    def gen_hosts(self, request):
        hm = HostsManager()
        hm.generate_host_file("/tmp/hosts.txt")
        self.message_user(request, "Hosts file generated")
        return HttpResponseRedirect("../")

    def import_hosts(self, request):
        hm = HostsManager()
        hm.import_host_files("/tmp/hosts/")
        self.message_user(request, "All hosts entries imported")
        return HttpResponseRedirect("../")

    def download_hosts(self, request):
        HostsSourcesUtils.download_hosts()
        self.message_user(request, "Hosts downloaded")
        return HttpResponseRedirect("../")

    def start_ttlmonitor(self, request):
        hm = HostsManager()
        hm.start_ttl_monitoring()
        self.message_user(request, "TTL monitor started")
        return HttpResponseRedirect("../")

    def start_server(self, request):
        self.message_user(request, "Server started")
        SecureDNSServer.start()
        return HttpResponseRedirect("../")


class HostAdmin(admin.ModelAdmin):
    list_display = ('url', 'ip', 'ttl')
    #list_filter = ('url', 'ttl')
    search_fields = ('url', )


admin.site.register(Host, HostAdmin)
admin.site.register(HostSources, HostSourcesAdmin)
#admin.site.add_action(HostsSourcesUtils.download_hosts)
