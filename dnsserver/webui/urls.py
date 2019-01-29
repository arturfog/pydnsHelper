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
    path('hostsmgr', views.hosts, name='hostsmgr')
]
