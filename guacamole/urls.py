from django.urls import re_path

from guacamole import views

app_name = "guacamole"
urlpatterns = [
    re_path(r'^(?P<id>[0-9]+)/$', views.Index.as_view(), name='guacamole_index'),
    re_path(r'^logplay/(?P<pk>[0-9]+)/',views.LogPlay.as_view(),name='guacamolelogplay'),
    re_path(r'^guacamolemonitor/(?P<pk>[0-9]+)/',views.GuacmoleMonitor.as_view(),name='guacamolemonitor'),
    re_path(r'^guacamolekill/',views.GuacamoleKill.as_view(),name='guacamolekill'),
    re_path(r'^sshlogplay/(?P<pk>[0-9]+)/',views.SshLogPlay.as_view(),name='sshlogplay'),
    re_path(r'^sshterminalmonitor/(?P<pk>[0-9]+)/',views.SshTerminalMonitor.as_view(),name='sshterminalmonitor'),
    re_path(r'^sshterminalkill/$',views.SshTerminalKill.as_view(),name='sshterminalkill'),
]
