from django.contrib import admin
from django.http import HttpResponseRedirect
from django.urls import include, path

from webui.models import Host, IPv4, IPv6
from webui.models import HostSources
from webui.models import Logs, Client, Stats, BlockedClients, StatsHosts
from libs.hosts_sources import HostsSourcesUtils
from libs.hosts_manager import HostsManager
from libs.dnsserver import SecureDNSServer
# Register your models here.

class HostSourcesAdmin(admin.ModelAdmin):
    #change_list_template = "entities/host_sources_changelist.html"
    search_fields = ('url',)

class HostAdmin(admin.ModelAdmin):
    list_display = ('url', 'comment', 'created', 'hits', 'blocked')
    search_fields = ('url', )

class IPv4Admin(admin.ModelAdmin):
    list_display = ('host', 'ip', 'ttl', 'last_updated')
    search_fields = ('ip', )

class IPv6Admin(admin.ModelAdmin):
    list_display = ('host', 'ip', 'ttl', 'last_updated')
    search_fields = ('ip', )

class LogsAdmin(admin.ModelAdmin):
    list_display = ('msg', 'timestamp')
    search_fields = ('msg', )

class StatsHostsAdmin(admin.ModelAdmin):
    using = 'stats'

    def save_model(self, request, obj, form, change):
        # Tell Django to save objects to the 'other' database.
        obj.save(using=self.using)

    def delete_model(self, request, obj):
        # Tell Django to delete objects from the 'other' database
        obj.delete(using=self.using)

    def get_queryset(self, request):
        # Tell Django to look for objects on the 'other' database.
        return super().get_queryset(request).using(self.using)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        # Tell Django to populate ForeignKey widgets using a query
        # on the 'other' database.
        return super().formfield_for_foreignkey(db_field, request, using=self.using, **kwargs)

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        # Tell Django to populate ManyToMany widgets using a query
        # on the 'other' database.
        return super().formfield_for_manytomany(db_field, request, using=self.using, **kwargs)

    list_display = ('host', )
    search_fields = ('host', )

class ClientAdmin(admin.ModelAdmin):
    using = 'stats'

    def save_model(self, request, obj, form, change):
        # Tell Django to save objects to the 'other' database.
        obj.save(using=self.using)

    def delete_model(self, request, obj):
        # Tell Django to delete objects from the 'other' database
        obj.delete(using=self.using)

    def get_queryset(self, request):
        # Tell Django to look for objects on the 'other' database.
        return super().get_queryset(request).using(self.using)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        # Tell Django to populate ForeignKey widgets using a query
        # on the 'other' database.
        return super().formfield_for_foreignkey(db_field, request, using=self.using, **kwargs)

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        # Tell Django to populate ManyToMany widgets using a query
        # on the 'other' database.
        return super().formfield_for_manytomany(db_field, request, using=self.using, **kwargs)

    list_display = ('ip', )
    search_fields = ('ip', )

class StatsAdmin(admin.ModelAdmin):
    using = 'stats'

    def save_model(self, request, obj, form, change):
        # Tell Django to save objects to the 'other' database.
        obj.save(using=self.using)

    def delete_model(self, request, obj):
        # Tell Django to delete objects from the 'other' database
        obj.delete(using=self.using)

    def get_queryset(self, request):
        # Tell Django to look for objects on the 'other' database.
        return super().get_queryset(request).using(self.using)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        # Tell Django to populate ForeignKey widgets using a query
        # on the 'other' database.
        return super().formfield_for_foreignkey(db_field, request, using=self.using, **kwargs)

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        # Tell Django to populate ManyToMany widgets using a query
        # on the 'other' database.
        return super().formfield_for_manytomany(db_field, request, using=self.using, **kwargs)

    list_display = ('host', 'client', 'timestamp')
    search_fields = ('host', )

admin.site.register(Host, HostAdmin)
admin.site.register(HostSources, HostSourcesAdmin)
admin.site.register(Logs, LogsAdmin)
admin.site.register(IPv4, IPv4Admin)
admin.site.register(IPv6, IPv6Admin)
admin.site.register(Stats, StatsAdmin)
admin.site.register(Client, ClientAdmin)
admin.site.register(StatsHosts, StatsHostsAdmin)