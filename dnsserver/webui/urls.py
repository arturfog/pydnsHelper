from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('gen_hosts', views.gen_hosts, name='gen_hosts'),
    path('start_ttl', views.start_ttl, name='start_ttl'),
    path('start_server', views.start_server, name='start_server'),
    path('status', views.status, name='status'),
    path('logs', views.logs, name='logs'),
    path('about', views.about, name='about'),
    path('hostsmgr', views.hosts, name='hostsmgr'),
    path('clear_logs', views.clear_logs, name='clear_logs'),
    path('export_logs', views.export_logs, name="export_logs"),
    path('download_hosts', views.download_hosts, name="download_hosts"),
    path('import_hosts', views.import_hosts, name="import_hosts"),
    path('import_sources', views.import_sources, name="import_sources")
]
