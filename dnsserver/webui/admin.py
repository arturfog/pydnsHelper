from django.contrib import admin
from django.http import HttpResponseRedirect
from django.urls import include, path

from webui.models import Host
from webui.models import HostSources
from libs.hosts_sources import HostsSourcesUtils
# Register your models here.


class HostAdmin(admin.ModelAdmin):
    list_display = ('url', 'ip', 'ttl')
    list_filter = ('url', 'ttl')
    change_list_template = "entities/hosts_changelist.html"

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('immortal/', self.set_immortal),
            path('mortal/', self.set_mortal),
        ]
        return my_urls + urls

    def set_immortal(self, request):
        self.model.objects.all().update(is_immortal=True)
        self.message_user(request, "All heroes are now immortal")
        return HttpResponseRedirect("../")

    def set_mortal(self, request):
        self.model.objects.all().update(is_immortal=False)
        self.message_user(request, "All heroes are now mortal")
        return HttpResponseRedirect("../")

admin.site.register(Host, HostAdmin)
admin.site.register(HostSources)
admin.site.add_action(HostsSourcesUtils.download_hosts)
