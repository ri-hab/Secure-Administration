from django.urls import re_path, include
from . import views

app_name="app_auditor"

urlpatterns = [
    # re_path(r'^$', views.user_index.as_view(), name='user_index'),
    re_path(r'^error', views.access_denied, name='access_denied'),
    re_path(r'^(?P<username>[\w.@+-]+)/$', views.switcher_auditor, name='switcher_auditor'),
    re_path(r'^(?P<username>[\w.@+-]+)/profil',views.ProfilView.as_view(), name='auditor_profile'),
    re_path(r'^(?P<username>[\w.@+-]+)/records/ssh', views.SSHRecordView.as_view(), name='ssh_record'),
    re_path(r'^(?P<username>[\w.@+-]+)/records/telnet', views.TELNETRecordView.as_view(), name='telnet_record'),
    re_path(r'^(?P<username>[\w.@+-]+)/records/rdp', views.RDPRecordView.as_view(), name='rdp_record'),
    re_path(r'^(?P<username>[\w.@+-]+)/records/vnc', views.VNCRecordView.as_view(), name='vnc_record'),
    re_path(r'^(?P<username>[\w.@+-]+)/monitor/ssh', views.SSHConnectionView.as_view(), name='ssh_connection'),
    re_path(r'^(?P<username>[\w.@+-]+)/monitor/telnet', views.TELNETConnectionView.as_view(), name='telnet_connection'),
    re_path(r'^(?P<username>[\w.@+-]+)/monitor/rdp', views.RDPConnectionView.as_view(), name='rdp_connection'),
    re_path(r'^(?P<username>[\w.@+-]+)/monitor/vnc', views.VNCConnectionView.as_view(), name='vnc_connection'),

]
