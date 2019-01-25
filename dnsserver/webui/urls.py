from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('genhosts', views.genhosts, name='genhosts'),
    path('startttl', views.startttl, name='startttl'),

    path('status', views.status, name='status'),
    path('logs', views.logs, name='logs'),
    path('about', views.about, name='about'),
    path('hostsmgr', views.hosts, name='hostsmgr')
]
