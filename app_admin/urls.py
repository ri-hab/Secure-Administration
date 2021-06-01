from django.urls import re_path, include
from . import views

app_name = "app_admin"

urlpatterns = [
    re_path(r'^error', views.access_denied, name='access_denied'),
    re_path(r'^(?P<username>[\w.@+-]+)/$', views.switcher_admin, name='switcher_admin'),
    re_path(r'^(?P<username>[\w.@+-]+)/profile', views.ProfileView.as_view(), name='admin_profile'),
    re_path(r'^(?P<username>[\w.@+-]+)/users/$', views.UsersListView.as_view(), name='admin_users_list'),
    re_path(r'^(?P<username>[\w.@+-]+)/users/groups', views.GroupsView.as_view(), name='admin_groups'),
    re_path(r'^(?P<username>[\w.@+-]+)/items/$', views.ItemsListView.as_view(), name='admin_items'),
    re_path(r'^(?P<username>[\w.@+-]+)/items/groups', views.ItemsGroupsListView.as_view(), name='admin_items_groups'),
    re_path(r'^(?P<username>[\w.@+-]+)/alerts', views.AlertsView.as_view(), name='admin_alerts'),




]
