# -*- coding: utf-8 -*-
"""
WSGI config for jumpserver3s project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/howto/deployment/wsgi/
"""
#handling the requests on the django web server
#Connect the web site to the web server django
import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jumpserver3s.settings')

application = get_wsgi_application()
