 # -*- coding: utf-8 -*-
from django import forms
from django.urls import reverse
from django.shortcuts import render
from django.views.generic import TemplateView, DetailView, ListView
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout, get_user_model
from app_manager.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from jumpserver3s.models import Log

User = get_user_model()


@login_required
def switcher_auditor(request, username):
    print(username)
    qs = User.objects.filter(username=username)
    print(qs)
    if not qs.exists():
        print("user not found")
        return HttpResponseRedirect(reverse('app_auditor:access_denied'))
    else:
        print("user already exists")
        return auditor_index.as_view()(request)

class auditor_index(LoginRequiredMixin,TemplateView):
    template_name = "app_auditor/auditor_index.html"
    model = User
    context_object_name = 'user'

class ProfilView(LoginRequiredMixin,TemplateView):
    template_name = "app_auditor/auditor_profile.html"

class SSHRecordView(LoginRequiredMixin,ListView):
    template_name = "app_auditor/ssh_record.html"
    queryset = Log.objects.all()
    context_object_name = 'logs'

class TELNETRecordView(LoginRequiredMixin,ListView):
    template_name = "app_auditor/telnet_record.html"
    queryset = Log.objects.all()
    context_object_name = 'logs'

class RDPRecordView(LoginRequiredMixin,ListView):
    template_name = "app_auditor/rdp_record.html"
    queryset = Log.objects.all()
    context_object_name = 'logs'

class VNCRecordView(LoginRequiredMixin,ListView):
    template_name = "app_auditor/vnc_record.html"
    queryset = Log.objects.all()
    context_object_name = 'logs'

class SSHConnectionView(LoginRequiredMixin,ListView):
    template_name = "app_auditor/ssh_connection.html"
    queryset = Log.objects.all()
    context_object_name = 'logs'

class TELNETConnectionView(LoginRequiredMixin,ListView):
    template_name = "app_auditor/telnet_connection.html"
    queryset = Log.objects.all()
    context_object_name = 'logs'

class RDPConnectionView(LoginRequiredMixin,ListView):
    template_name = "app_auditor/rdp_connection.html"
    queryset = Log.objects.all()
    context_object_name = 'logs'

class VNCConnectionView(LoginRequiredMixin,ListView):
    template_name = "app_auditor/vnc_connection.html"
    queryset = Log.objects.all()
    context_object_name = 'logs'


def access_denied(request):
    return render(request,"registration/error.html")

@login_required
def user_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse('index'))
