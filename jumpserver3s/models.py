from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
try:
    import simplejson as json
except ImportError:
    import json
import uuid
from django.utils.text import slugify
from django.utils.translation import ugettext_lazy as _
from app_user.models import ServerGroup, Server

User = get_user_model()
class CommandsSequence(models.Model):
    name = models.CharField(
        max_length=40,
        verbose_name=_('Task name'),
        blank=False,
        unique=True
    )
    commands = models.TextField(
        verbose_name=_('Task commands'),
        blank=False
    )
    group = models.ManyToManyField(
        ServerGroup,
        verbose_name=_('Server group you want to execute')
    )

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.name

    def clean(self):
        try:
            json.dumps(self.commands)
        except Exception:
            raise ValidationError(_('Commands sequence is not valid json type'))

    def save(self, *args, **kwargs):
        if isinstance(self.commands,(list)):
            self.commands = json.dumps(self.commands)
        super(CommandsSequence,self).save(*args, **kwargs)

class Log(models.Model):

    server = models.ForeignKey(
    Server,
    verbose_name=_('Server'),
    on_delete=models.CASCADE
    )
    channel = models.CharField(
        max_length=100,
        verbose_name=_('Channel name'),
        blank=False,
        unique=True,
        editable=False
    )
    log = models.UUIDField(
        max_length=100,
        default=uuid.uuid4,
        verbose_name=_('Log name'),
        blank=False,
        unique=True,
        editable=False
    )
    start_time = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Start time')
    )
    end_time = models.DateTimeField(
        auto_created=True,
        auto_now=True,
        verbose_name=_('End time')
    )
    is_finished = models.BooleanField(
        default=False,
        verbose_name=_('Is finished')
    )
    user = models.ForeignKey(
        User,
        verbose_name=_('User'),
        on_delete=models.CASCADE

    )
    width = models.PositiveIntegerField(
        default=90,
        verbose_name=_('Width')
    )
    height = models.PositiveIntegerField(
        default=40,
        verbose_name=_('Height')
    )
    gucamole_client_id = models.CharField(
        max_length=100,
        verbose_name=_('Gucamole channel name'),
        blank=True,
        editable=False
    )

    def __unicode__(self):
        return self.server.name

    def __str__(self):
        return self.server.name
