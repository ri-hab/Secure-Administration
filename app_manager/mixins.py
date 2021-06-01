# -*- coding: utf-8 -*-
from django.contrib.auth.mixins import AccessMixin
from django.shortcuts import render, redirect


class LoginRequiredMixin(AccessMixin):
    """Verify that the current user is authenticated."""
    def dispatch(self, request, *args, **kwargs):
        print("user is authenticated: {}".format(request.user.is_authenticated))
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)
