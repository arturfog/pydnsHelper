from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('genhosts', views.genhosts, name='genhosts'),
    path('startttl', views.startttl, name='startttl'),
]
