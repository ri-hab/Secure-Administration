 # -*- coding: utf-8 -*-
from django import forms
from django.urls import reverse
from django.shortcuts import render
from django.views.generic import TemplateView, ListView
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout, get_user_model
from app_manager.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from app_user.models import Server

User = get_user_model()

def switcher_admin(request, username):
    print(username)
    qs = User.objects.filter(username=username)
    print(qs)
    if not qs.exists():
        print("user not found")
        return HttpResponseRedirect(reverse('app_admin:access_denied'))
    else:
        print("user already exists")
        return admin_index.as_view()(request)

class admin_index(LoginRequiredMixin,TemplateView):
    template_name = "app_admin/admin_index.html"
    model = User
    context_object_name = 'user'

class ProfileView(LoginRequiredMixin,TemplateView):
    template_name = "app_admin/admin_profile.html"

class UsersListView(LoginRequiredMixin,ListView):
    template_name = "app_admin/admin_users_list.html"
    queryset = User.objects.all()
    context_object_name = 'users'

class GroupsView(LoginRequiredMixin,TemplateView):
    template_name = "app_admin/admin_groups.html"

class ItemsListView(LoginRequiredMixin,ListView):
    template_name = "app_admin/admin_items.html"
    queryset = Server.objects.all()
    context_object_name = 'servers'

class ItemsGroupsListView(LoginRequiredMixin,TemplateView):
    template_name = "app_admin/admin_items_groups.html"

class AlertsView(LoginRequiredMixin,TemplateView):
    template_name = "app_admin/admin_alerts.html"

def access_denied(request):
    return render(request,"registration/error.html")

@login_required
def user_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse('index'))
