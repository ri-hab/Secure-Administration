# -*- coding: utf-8 -*-
import paramiko
import socket
import ast
import sys
import time
import os
import traceback
import logging
from django.conf import settings
from django.utils.timezone import now
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from channels.generic.websockets import WebsocketConsumer
from channels import Group
try:
    import simplejson as json
except ImportError:
    import json
try:
    from django.utils.encoding import smart_unicode
except ImportError:
    from django.utils.encoding import smart_text as smart_unicode

from .interactive import WebsocketAuth,interactive_shell,get_redis_instance, SshTerminalThread, InterActiveShellThread
from app_user.models import ServerGroup, Server
from .models import CommandsSequence, Log
from .sudoterminal import ShellHandlerThread
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO
logger = logging.getLogger(__name__)
import uuid
from six import string_types as basestring
try:
    unicode
except NameError:
    unicode = str

User = get_user_model()


class webterminal(WebsocketConsumer, WebsocketAuth):

    ssh = paramiko.SSHClient()
    http_user = True
    #http_user_and_session = True
    channel_session = True
    channel_session_user = True

    def connect(self, message):
        self.message.reply_channel.send({"accept": True})
        directory_date_time = now()
        record = os.path.join(settings.MEDIA_DIR,"records")
        recording_path = os.path.join(record, 'SSH_Records-{0}-{1}-{2}-'.format(
            directory_date_time.year, directory_date_time.month, directory_date_time.day))

        if not self.authenticate:
            self.message.reply_channel.send({"text": json.dumps(
                {'status': False, 'message': 'You must login to the system!'})}, immediately=True)
            self.message.reply_channel.send({"accept": False})

    def disconnect(self, message):
        # close threading
        self.closessh()
        self.message.reply_channel.send({"accept": False})
        audit_log = Log.objects.get(user=User.objects.get(
            username=self.message.user.username), channel=self.message.reply_channel.name)
        audit_log.is_finished = True
        audit_log.end_time = now()
        audit_log.save()
        self.close()


    @property
    def queue(self):
        queue = get_redis_instance()
        channel = queue.pubsub()
        return queue

    def closessh(self):
        # close threading
        self.queue.publish(self.message.reply_channel.name,
                           json.dumps(['close']))

    def receive(self, text=None, bytes=None, **kwargs):
        try:
            if text:
                data = json.loads(text)
                begin_time = time.time()
                if isinstance(data, list) and data[0] == 'ip' and len(data) == 5:
                    ip = data[1]
                    width = data[2]
                    height = data[3]
                    id = data[4]
                    self.ssh.set_missing_host_key_policy(
                        paramiko.AutoAddPolicy())
                    try:
                        data = Server.objects.get(
                            ip=ip, credential__protocol__contains='ssh')
                        port = data.credential.port
                        method = data.credential.method
                        hostname = data.hostname
                        if method == 'password':
                            password = data.credential.password
                        else:
                            key = data.credential.key
                    except ObjectDoesNotExist:
                        # self.message.reply_channel.send({"text": json.dumps(
                            # ['stdout', '\033[1;3;31mConnect to server! Server ip doesn\'t exist!\033[0m'])}, immediately=True)
                        self.message.reply_channel.send(
                            {"bytes": 'Connect to server! Server ip doesn\'t exist!'}, immediately=True)
                        self.message.reply_channel.send({"accept": False})
                        logger.error(
                            "Connect to server! Server ip {0} doesn\'t exist!".format(ip))
                    try:
                        if method == 'password':
                            self.ssh.connect(
                                ip, port=port, username=hostname, password=password, timeout=3)
                        else:
                            private_key = StringIO(key)
                            if 'RSA' in key:
                                private_key = paramiko.RSAKey.from_private_key(
                                    private_key)
                            elif 'DSA' in key:
                                private_key = paramiko.DSSKey.from_private_key(
                                    private_key)
                            elif 'EC' in key:
                                private_key = paramiko.ECDSAKey.from_private_key(
                                    private_key)
                            elif 'OPENSSH' in key:
                                private_key = paramiko.Ed25519Key.from_private_key(
                                    private_key)
                            else:
                                # self.message.reply_channel.send({"text": json.dumps(
                                    # ['stdout', '\033[1;3;31munknown or unsupported key type, only support rsa dsa ed25519 ecdsa key type\033[0m'])}, immediately=True)
                                self.message.reply_channel.send({"bytes":
                                                                 'Unknown or unsupported key type, only support rsa dsa ed25519 ecdsa key type'}, immediately=True)
                                self.message.reply_channel.send(
                                    {"accept": False})
                                logger.error(
                                    "unknown or unsupported key type, only support rsa dsa ed25519 ecdsa key type!")
                            self.ssh.connect(
                                ip, port=port, username=hostname, pkey=private_key, timeout=3)
                        # when connect server sucess record log
                        audit_log = Log.objects.create(user=User.objects.get(
                            username=self.message.user.username), server=data, channel=self.message.reply_channel.name, width=width, height=height)
                        audit_log.save()
                    except socket.timeout:
                        # self.message.reply_channel.send({"text": json.dumps(
                            # ['stdout', '\033[1;3;31mConnect to server time out\033[0m'])}, immediately=True)
                        self.message.reply_channel.send(
                            {"bytes": 'Connect to server time out'}, immediately=True)
                        logger.error(
                            "Connect to server {0} time out!".format(ip))
                        self.message.reply_channel.send({"accept": False})
                        return
                    except Exception as e:
                        # self.message.reply_channel.send({"text": json.dumps(
                            # ['stdout', '\033[1;3;31mCan not connect to server: {0}\033[0m'.format(e)])}, immediately=True)
                        self.message.reply_channel.send(
                            {"bytes": 'Can not connect to server: {0}'.format(e)}, immediately=True)
                        self.message.reply_channel.send({"accept": False})
                        logger.error(
                            "Can not connect to server {0}: {1}".format(ip, e))
                        return

                    chan = self.ssh.invoke_shell(
                        width=width, height=height, term='xterm')

                    # open a new threading to handle ssh to avoid global variable bug
                    sshterminal = SshTerminalThread(self.message, chan)
                    sshterminal.setDaemon = True
                    sshterminal.start()

                    directory_date_time = now()
                    log_name = os.path.join('{0}-{1}-{2}'.format(directory_date_time.year,
                                                                 directory_date_time.month, directory_date_time.day), '{0}'.format(audit_log.log))

                    # open ssh terminal
                    interactivessh = InterActiveShellThread(
                        chan, self.message.reply_channel.name, log_name=log_name, width=width, height=height)
                    interactivessh.setDaemon = True
                    interactivessh.start()

                elif isinstance(data, list) and data[0] in ['stdin', 'stdout']:
                    self.queue.publish(
                        self.message.reply_channel.name, json.loads(text)[1])
                elif isinstance(data, list) and data[0] == u'set_size':
                    self.queue.publish(self.message.reply_channel.name, text)
                elif isinstance(data, list) and data[0] == u'close':
                    self.disconnect(self.message)
                    return
                else:
                    # self.message.reply_channel.send({"text": json.dumps(
                        # ['stdout', '\033[1;3;31mUnknow command found!\033[0m'])}, immediately=True)
                    #self.message.reply_channel.send({"bytes": '\033[1;3;31mUnknow command found!\033[0m'}, immediately=True)
                    self.queue.publish(self.message.reply_channel.name, text)
                    self.message.reply_channel.send({"text":json.dumps(['stdout','Unknown command found!'])},immediately=True)

                    #logger.error("Unknow command found!")
            elif bytes:
                self.queue.publish(
                    self.message.reply_channel.name, bytes)
        except socket.error:
            audit_log = Log.objects.get(user=User.objects.get(
                username=self.message.user.username), channel=self.message.reply_channel.name)
            audit_log.is_finished = True
            audit_log.end_time = now()
            audit_log.save()
            self.closessh()
            self.close()
        except ValueError:
            self.queue.publish(
                self.message.reply_channel.name, smart_unicode(text))
        except Exception as e:
            logger.error(traceback.print_exc())
            self.closessh()
            self.close()

class SshTerminalMonitor(WebsocketConsumer, WebsocketAuth):

    http_user = True
    http_user_and_session = True
    channel_session = True
    channel_session_user = True

    def connect(self, message, channel):
        """
        User authenticate to monitor user ssh action!
        """
        print("this is from consumer")
        if not self.authenticate:
            self.message.reply_channel.send({"text": json.dumps(
                {'status': False, 'message': 'You must login to the system!'})}, immediately=True)
            self.message.reply_channel.send({"accept": False})
        else:
            self.message.reply_channel.send({"accept": True})
            Group(channel).add(self.message.reply_channel.name)
            print("Group")
            print(Group(channel))

    def disconnect(self, message, channel):
        Group(channel).discard(self.message.reply_channel.name)
        self.message.reply_channel.send({"accept": False})
        self.close()

    def receive(self, text=None, bytes=None, **kwargs):
        pass
