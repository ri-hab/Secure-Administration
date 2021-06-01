# -*- coding: utf-8 -*-
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .forms import UserAdminCreationForm, UserAdminChangeForm
from .models import UserGroup


User = get_user_model()

class UserAdmin(BaseUserAdmin):
    # The forms to add and change user instances
    form = UserAdminChangeForm
    add_form = UserAdminCreationForm

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = ('id','email', 'first_name', 'last_name', 'Phone','username','type', 'active', 'staff', 'admin')
    list_filter = ('active', 'admin', 'type')
    fieldsets = [
        ('User credentials', {'fields': ('email', 'password', 'type')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'Phone','image')}),
        ('Permissions', {'fields': ('active', 'staff','admin')}),
        ('Extra information', {'fields': ('date_joined', 'last_login',)}),
    ]
    readonly_fields = ('last_login',)
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2','username','type')}
        ),
    )
    search_fields = ['email','type']
    ordering = ('email',)
    filter_horizontal = ()

admin.site.register(User, UserAdmin)

class UserGroupAdmin(admin.ModelAdmin):

    list_display = ('name', 'createdatetime', 'updatedatetime')
    list_filter = ('user', 'createdatetime', 'updatedatetime')
    fieldsets = [
        ('User Group Description', {'fields': ('name', 'user',)}),
        ('Extra information', {'fields': ('createdatetime', 'updatedatetime',)}),
    ]
    readonly_fields = ('createdatetime','updatedatetime',)
    search_fields = ['user',]
    ordering = ('name',)
    filter_horizontal = ()

admin.site.register(UserGroup, UserGroupAdmin)
