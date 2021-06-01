# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.http import HttpResponse #HttpResponse is an object
from django import forms


def index(request):
    return render(request, "homepage/index.html")
