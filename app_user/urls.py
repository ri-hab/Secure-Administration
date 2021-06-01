from django.urls import re_path, include
from app_user import views

app_name ="app_user"

urlpatterns = [
    re_path(r'^error', views.access_denied, name='access_denied'),
    re_path(r'^(?P<username>[\w.@+-]+)/$', views.switcher_user, name='switcher_user'),
    re_path(r'^(?P<username>[\w.@+-]+)/profile', views.ProfileView.as_view(), name='user_profile'),
    re_path(r'^(?P<username>[\w.@+-]+)/groups', views.GroupsView.as_view(), name='user_groups'),
    re_path(r'^(?P<username>[\w.@+-]+)/items', views.ServerListView.as_view(), name='user_items'),
    re_path(r'^(?P<username>[\w.@+-]+)/history/ssh', views.SSHhistoryView.as_view(), name='ssh_history'),
    re_path(r'^(?P<username>[\w.@+-]+)/history/telnet', views.TELNEThistoryView.as_view(), name='telnet_history'),
    re_path(r'^(?P<username>[\w.@+-]+)/history/rdp', views.RDPhistoryView.as_view(), name='rdp_history'),
    re_path(r'^(?P<username>[\w.@+-]+)/history/vnc', views.VNChistoryView.as_view(), name='vnc_history'),
    re_path(r'^(?P<username>[\w.@+-]+)/connect/ssh', views.SSHconnectView.as_view(), name='ssh_connect'),
    re_path(r'^(?P<username>[\w.@+-]+)/connect/telnet', views.TELNETconnectView.as_view(), name='telnet_connect'),
    re_path(r'^(?P<username>[\w.@+-]+)/connect/rdp', views.RDPconnectView.as_view(), name='rdp_connect'),
    re_path(r'^(?P<username>[\w.@+-]+)/connect/vnc', views.VNCconnectView.as_view(), name='vnc_connect'),


]
