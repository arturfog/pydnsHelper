from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('hosts/', views.HostListView.as_view(), name='hosts'),
    path('hosts/<int:pk>', views.HostDetailView.as_view(), name='host-detail'),
    path('hosts/new/', views.post_new, name='post_new'),
]
