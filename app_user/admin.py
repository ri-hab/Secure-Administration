# -*- coding: utf-8 -*-
from django.contrib import admin
from django.contrib.auth.models import Group
from .models import Server, ServerGroup, Credential

class ServerAdmin(admin.ModelAdmin):

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = ('name','id', 'hostname', 'ip', 'createdatetime', 'credential')
    list_filter = ('credential', 'createdatetime','updatedatetime',)
    fieldsets = [
        ('Server credentials', {'fields': ('name', 'hostname', 'ip',)}),
        ('Credentials', {'fields': ('credential',)}),
        ('Extra information', {'fields': ('createdatetime','updatedatetime',)}),
    ]
    readonly_fields = ('createdatetime','updatedatetime')
    search_fields = ['credential',]
    ordering = ('name',)
    filter_horizontal = ()
admin.site.register(Server, ServerAdmin)

class ServerGroupAdmin(admin.ModelAdmin):

    list_display = ('name', 'createdatetime', 'updatedatetime')
    list_filter = ('servers', 'createdatetime',)
    fieldsets = [
        ('Server Group credentials', {'fields': ('name',)}),
        ('Credentials', {'fields': ('servers',)}),
        ('Extra information', {'fields': ('createdatetime','updatedatetime',)}),
    ]
    readonly_fields = ('createdatetime','updatedatetime')
    search_fields = ['servers',]
    ordering = ('name',)
    filter_horizontal = ()
admin.site.register(ServerGroup, ServerGroupAdmin)

class CredentialAdmin(admin.ModelAdmin):

    list_display = ('name','protocol','method','port',)
    list_filter = ('user', 'method','protocol',)
    fieldsets = [
        ('Credential Description', {'fields': ('name','user', 'protocol','port', 'method', )}),
        ('Authentication ', {'fields': ('key','password',)}),
        ('Proxy Description', {'fields': ('proxyserverip','proxyport','proxypassword',)}),
        ('Other Informations', {'fields': ('width','height','dpi',)}),
    ]
    search_fields = ['protocol','method',]
    ordering = ('name',)
    filter_horizontal = ()
admin.site.register(Credential, CredentialAdmin)

#
admin.site.unregister(Group)
# class ProtocolAdmin(admin.ModelAdmin):
#
#     list_display = ('name', 'port', 'port_sec', 'port_last')
#     fieldsets = [
#         ('Protocol Description', {'fields': ('name', 'port', 'port_sec','port_last',)}),
#         ('Extra information', {'fields': ('createdatetime',)}),
#     ]
#     readonly_fields = ('createdatetime',)
#     ordering = ('name',)
#     filter_horizontal = ()
#
#
# admin.site.register(Protocol, ProtocolAdmin)
