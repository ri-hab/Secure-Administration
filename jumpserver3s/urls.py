"""jumpserver3s URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import re_path, include, path
from . import views
from app_manager import views as managerviews
from django.views.static import serve
from django.conf import settings
from django.conf.urls.static import static
import os

#jumpserver3s api
from rest_framework import routers
from jumpserver3s.api import ServerGroupViewSet,ServerViewSet,CommandsSequenceViewSet,CredentialViewSet

#Register jumpserver3s api
router = routers.DefaultRouter()
router.register('servergroup', ServerGroupViewSet)
router.register('serverinfo', ServerViewSet)
router.register('commandssequence', CommandsSequenceViewSet)
router.register('credential', CredentialViewSet)

urlpatterns = [
    re_path('admin/', admin.site.urls),
    re_path(r'^$', views.index, name='index'),
    # re_path(r'^login', managerviews.login_page, name="login"),
    re_path(r'^login', managerviews.LoginView.as_view(), name="login"),
    re_path(r'^send-otp', managerviews.send_otp, name='opt-verify'),
    re_path(r'^notactive', managerviews.notactive, name="notactive" ),
    re_path(r'^invalid', managerviews.invalid, name="invalid" ),
    #re_path(r'^verify', managerviews.verify_view, name="verify_view")
    # # re_path(r'^signup', managerviews.register_page, name='signup'),
    re_path(r'^signupAdmin', managerviews.RegisterViewAdmin.as_view(), name='signupAdmin'),
    re_path(r'^signupAuditor', managerviews.RegisterViewAuditor.as_view(), name='signupAuditor'),
    re_path(r'^signupUser', managerviews.RegisterViewUser.as_view(), name='signupUser'),
    re_path(r'^registered', managerviews.registered, name='registered'),
    re_path(r'^admin/',include('app_admin.urls', namespace="app_admin")),
    re_path(r'^user/', include('app_user.urls', namespace="app_user")),
    re_path(r'^auditor/', include('app_auditor.urls', namespace="app_auditor")),
    re_path(r'^guacamole/', include('guacamole.urls', namespace="guacamole")),
    path('activate/<uidb64>/<token>', managerviews.VerificationView.as_view(), name='activate'),

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


if settings.DEBUG:
    # import debug_toolbar
    urlpatterns = [
        # re_path(r'^__debug__/', include(debug_toolbar.urls)),
        re_path(r'^records/(?P<path>.*)$', serve,{'document_root': '/home/rawdha/django-dev/PFE_project/jumpserver3s/media/'}),
    ] + urlpatterns
