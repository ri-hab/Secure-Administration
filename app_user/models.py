# -*- coding: utf-8 -*-
from django.db import models
from django.utils.text import slugify
from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError

User = get_user_model()

class Server(models.Model):
    name = models.CharField(
        unique = True,
        verbose_name = ('Server name'),
        max_length = 50,
        default = "Server name",
        blank = False
    )

    hostname = models.CharField(
        verbose_name = ('Host name'),
        max_length = 40,
        default = "hostname",
        blank = False
    )

    ip = models.GenericIPAddressField(
        verbose_name = ('IP address'),
        protocol = 'ipv4',
        blank=False
    )

    createdatetime = models.DateTimeField(
        verbose_name=('Date created'),
        default = timezone.now,
    )
    updatedatetime = models.DateTimeField(
        auto_created=True,
        auto_now=True,
        verbose_name=_('Date Updated')
    )
    credential = models.ForeignKey(
    'Credential',
    verbose_name =_('Credentials'),
    on_delete = models.CASCADE
     )

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name

    def gethostname(self):
        return slugify(self.hostname)

class ServerGroup(models.Model):
    name = models.CharField(
        max_length=40,
        verbose_name=_('Server group name'),
        blank=False,
        unique=True
    )
    servers = models.ManyToManyField(
        Server,
        related_name='servers',
        verbose_name=_('Servers')
    )
    createdatetime = models.DateTimeField(
        default = timezone.now,
        verbose_name=_('Create time')
    )
    updatedatetime = models.DateTimeField(
        auto_created=True,
        auto_now=True,
        verbose_name=_('Update time')
    )

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.name

class Credential(models.Model):
    protocol_choices = (
            ('ssh-password',_('ssh-password')),
            ('ssh-key',_('ssh-key')),
            ('vnc',_('vnc')),
            ('rdp',_('rdp')),
            ('telnet',_('telnet'))
        )
    name = models.CharField(
        max_length=40,
        verbose_name=_('Credential name'),
        blank=False,
        unique=True
    )
    user = models.ForeignKey(
        User,
        verbose_name=_('Authorised User'),
        on_delete = models.CASCADE
    )
    port = models.PositiveIntegerField(
        default=22,
        blank=False,
        verbose_name=_('Port Number')
    )
    method = models.CharField(
        max_length=40,
        choices=(
            ('password',_('password')),
            ('key',_('key'))
        ),
        blank=False,
        default='password',
        verbose_name=_('Method')
    )
    key = models.TextField(
        blank=True,
        verbose_name=_('Key')
    )
    password = models.CharField(
        max_length=40,
        blank=True,
        verbose_name=_('Password')
    )
    proxy = models.BooleanField(
        default=False,
        verbose_name=_('Proxy')
    )
    proxyserverip = models.GenericIPAddressField(
        protocol='ipv4',
        null=True,
        blank=True,
        verbose_name=_('Proxy ip')
    )
    proxyport = models.PositiveIntegerField(
        blank=True,
        null=True,
        verbose_name=_('Proxy port')
    )
    proxypassword = models.CharField(
        max_length=40,
        verbose_name=_('Proxy password'),
        blank=True)
    protocol = models.CharField(
        max_length=40,
        default='ssh-password',
        choices=protocol_choices,
        verbose_name=_('Protocol')
    )
    width = models.PositiveIntegerField(
        verbose_name=_('width'),
        default=1024
    )
    height = models.PositiveIntegerField(
        verbose_name=_('height'),
        default=768
    )
    dpi = models.PositiveIntegerField(
        verbose_name=_('dpi'),
        default=96
    )

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.name

    def clean(self):
        if self.protocol == 'ssh-password' or self.protocol == 'ssh-key':
            if self.method == 'password' and len(self.password) == 0:
                raise ValidationError(_('If you choose password auth method,You must set password!'))
            if self.method == 'password' and len(self.key) >0:
                raise ValidationError(_('If you choose password auth method,You must make key field for blank!'))
            if self.method == 'key' and len(self.key) == 0:
                raise ValidationError(_('If you choose key auth method,You must fill in key field!'))
            if self.method == 'key' and len(self.password) >0:
                raise ValidationError(_('If you choose key auth method,You must make password field for blank!'))
            if self.proxy:
                if self.proxyserverip is None or self.proxyport is None:
                    raise ValidationError(_('If you choose auth proxy,You must fill in proxyserverip and proxyport field !'))
