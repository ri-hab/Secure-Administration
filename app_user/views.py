 # -*- coding: utf-8 -*-
from django import forms
from django.urls import reverse
from django.shortcuts import render
from django.views.generic import TemplateView, View, ListView, DetailView
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout, get_user_model
from app_manager.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from .models import Server
from jumpserver3s.models import Log

User = get_user_model()

def switcher_user(request, username):
    print(username)
    qs = User.objects.filter(username=username)
    print(qs)
    if not qs.exists():
        print("user not found")
        return HttpResponseRedirect(reverse('app_user:access_denied'))
    else:
        print("user already exists")
        return user_index.as_view()(request)

class user_index(LoginRequiredMixin,TemplateView):
    template_name = "app_user/user_index.html"
    model = User
    context_object_name = 'user'

class ProfileView(LoginRequiredMixin,TemplateView):
    template_name = "app_user/user_profile.html"

class GroupsView(LoginRequiredMixin,TemplateView):
    template_name = "app_user/user_groups.html"
    model = Server

class ServerListView(LoginRequiredMixin,ListView):
    template_name = "app_user/user_items.html"
    queryset = Server.objects.all()
    context_object_name = 'servers'

class SSHhistoryView(LoginRequiredMixin,ListView):
    template_name = "app_user/user_ssh_history.html"
    queryset = Log.objects.all()
    context_object_name = 'logs'

class TELNEThistoryView(LoginRequiredMixin,ListView):
    template_name = "app_user/user_telnet_history.html"
    queryset = Log.objects.all()
    context_object_name = 'logs'

class RDPhistoryView(LoginRequiredMixin,ListView):
    template_name = "app_user/user_rdp_history.html"
    queryset = Log.objects.all()
    context_object_name = 'logs'

class VNChistoryView(LoginRequiredMixin,ListView):
    template_name = "app_user/user_vnc_history.html"
    queryset = Log.objects.all()
    context_object_name = 'logs'

class SSHconnectView(LoginRequiredMixin,ListView):
    template_name = "app_user/ssh_connections.html"
    queryset = Server.objects.all()
    context_object_name = 'servers'

class TELNETconnectView(LoginRequiredMixin,ListView):
    template_name = "app_user/telnet_connections.html"
    queryset = Server.objects.all()
    context_object_name = 'servers'

class RDPconnectView(LoginRequiredMixin,ListView):
    template_name = "app_user/rdp_connections.html"
    queryset = Server.objects.all()
    context_object_name = 'servers'

class VNCconnectView(LoginRequiredMixin,ListView):
    template_name = "app_user/vnc_connections.html"
    queryset = Server.objects.all()
    context_object_name = 'servers'


@login_required
def user_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse('index'))

def access_denied(request):
    return render(request,"registration/error.html")
