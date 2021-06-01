# -*- coding: utf-8 -*-
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.utils.timezone import now
from django.contrib.auth import get_user_model
from channels.generic.websockets import WebsocketConsumer
try:
    from django.utils.encoding import smart_unicode
except ImportError:
    from django.utils.encoding import smart_text as smart_unicode
try:
    import simplejson as json
except ImportError:
    import json
import uuid
import sys
import os
import traceback
from jumpserver3s.models import Log
from app_user.models import Server
from jumpserver3s.interactive import get_redis_instance, mkdir_p, WebsocketAuth
from guacamole.client import GuacamoleClient
from guacamole.guacamolethreading import GuacamoleThread, GuacamoleThreadWrite
from guacamole.instruction import GuacamoleInstruction as Instruction


User = get_user_model()


class GuacamoleWebsocket(WebsocketConsumer, WebsocketAuth):

    http_user = True
    #http_user_and_session = True
    channel_session = True
    channel_session_user = True

    @property
    def authenticate(self):
        if self.message.user.is_authenticated:
            print("authenticate: {}".format(self.message.user.is_authenticated))
            return True
        else:
            return False

    def connect(self, message, id):
        self.message.reply_channel.send({"accept": True})
        prefix, label = message['path'].strip('/').split('/')
        # print("prefix: {}".format(prefix))
        # print("label: {}".format(label))
        id = label
        print("id: {}".format(id))
        # print("server: {}".format(server))
        user = self.message.user
        print("user: {}".format(user))
        if not self.authenticate:
            self.message.reply_channel.send({"text": json.dumps(
                {'status': False, 'message': 'You must login to the system!'})}, immediately=True)
            self.message.reply_channel.send({"accept": False})
        else:
            # permission auth
            username = user.username
            client = GuacamoleClient(
                settings.GUACD_HOST, settings.GUACD_PORT)
            print("client: {}".format(client))
            try:
                data = Server.objects.get(id=id)
                print("data: {}".format(data))
                print("data.credential.protocol: {}".format(data.credential.protocol))
                if data.credential.protocol in ['vnc', 'rdp', 'telnet']:
                    pass
                else:
                    self.message.reply_channel.send({"accept": False})
            except ObjectDoesNotExist:
                # server info not exist
                self.message.reply_channel.send({"accept": False})
            cache_key = str(uuid.uuid4())
            print("cache_key: {}".format(cache_key))
            directory_date_time = now()
            record = os.path.join(settings.MEDIA_DIR,"records")
            print("record: {}".format(record))
            recording_path = os.path.join(record, '{0}-{1}-{2}'.format(
                directory_date_time.year, directory_date_time.month, directory_date_time.day))
            print("recording_path: {}".format(recording_path))
            if isinstance(username, bytes):
                username = username.decode()
            drive_path = os.path.join(record, str(username), 'Download')
            print("drive_path: {}".format(drive_path))
            print("protocol: {}".format(data.credential.protocol))
            """
            Create recording media file and drive path
            """
            mkdir_p(recording_path)
            mkdir_p(drive_path)

            try:
                client.handshake(width=data.credential.width,
                                 height=data.credential.height,
                                 protocol=data.credential.protocol,
                                 hostname=data.ip,
                                 port=data.credential.port,
                                 username=data.credential.user.username,
                                 password=data.credential.password,
                                 recording_path=recording_path,
                                 recording_name=cache_key,
                                 create_recording_path='true',
                                 enable_wallpaper='true',
                                 ignore_cert='true',
                                 enable_drive='true',
                                 drive_path=drive_path,
                                 create_drive_path='true',
                                 security="tls",
                                 # console_audio='true',
                                 # enable_audio_input='true',
                                 # disable_audio='false',
                                 # console='true',
                                 enable_full_window_drag='true',
                                 resize_method="reconnect"  # display-update
                                 )
            except Exception as e:
                print(e)
                print(traceback.print_exc())
                self.message.reply_channel.send({"accept": False})
                return
            self.message.reply_channel.send(
                {"text": '0.,{0}.{1};'.format(len(cache_key), cache_key)}, immediately=True)

            audit_log = Log.objects.create(user=User.objects.get(username=username), server=data, channel=self.message.reply_channel.name,
                                           width=data.credential.width, height=data.credential.height, log=cache_key, gucamole_client_id=client._id)
            audit_log.save()
            guacamolethread = GuacamoleThread(self.message, client)
            guacamolethread.setDaemon = True
            guacamolethread.start()

            guacamolethreadwrite = GuacamoleThreadWrite(self.message, client)
            guacamolethreadwrite.setDaemon = True
            guacamolethreadwrite.start()

    def disconnect(self, message, id):
        # close threading
        print('disconnect')
        try:
            audit_log = Log.objects.get(
                channel=self.message.reply_channel.name)
            audit_log.is_finished = True
            audit_log.end_time = now()
            audit_log.save()
            cache_key = audit_log.gucamole_client_id
            client = GuacamoleClient(
                settings.GUACD_HOST, settings.GUACD_PORT)
            client.send_instruction(Instruction('select', cache_key))
            instruction = client.read_instruction()
            kwargs = {'width': 1024, 'height': 768, 'read_only': 'true'}
            connection_args = [
                kwargs.get(arg.replace('-', '_'), '') for arg in instruction.args
            ]
            client.send_instruction(Instruction('size', 1024, 768, 96))
            client.send_instruction(Instruction('audio', *list()))
            client.send_instruction(Instruction('video', *list()))
            client.send_instruction(Instruction('image', *list()))
            client.send_instruction(Instruction('connect', *connection_args))
            client.send_instruction(Instruction('disconnect', *connection_args))
        except:
            pass
        finally:
            get_redis_instance().delete(id)
            self.message.reply_channel.send({"accept": False})

    def queue(self):
        queue = get_redis_instance()
        channel = queue.pubsub()
        return queue

    def receive(self, text=None, bytes=None, **kwargs):
        self.queue().publish(self.message.reply_channel.name, text)


class GuacamoleMonitor(GuacamoleWebsocket, WebsocketAuth):

    def connect(self, message, id):
        self.message.reply_channel.send({"accept": True})
        prefix, id = message['path'].strip('/').split('/')
        print("id: {}".format(id))
        if not self.authenticate:
            self.message.reply_channel.send({"text": json.dumps(
                {'status': False, 'message': 'You must login to the system!'})}, immediately=True)
            self.message.reply_channel.send({"accept": False})
        else:
            print("this is from connect")
            client = GuacamoleClient(
                settings.GUACD_HOST, settings.GUACD_PORT)
            log_object = Log.objects.get(id=id)
            print("log_object: {}".format(log_object))
            cache_key = str(log_object.gucamole_client_id)
            print("cache_key: {}".format(cache_key))
            data = log_object.server
            print("data: {}".format(data))
            # draft version for real time monitor
            client.send_instruction(Instruction('select', cache_key))
            print("this is after send instruction")
            instruction = client.read_instruction()
            print("instruction: {}".format(instruction))
            kwargs = {'width': 1024, 'height': 768, 'read_only': 'true'}
            connection_args = [
                kwargs.get(arg.replace('-', '_'), '') for arg in instruction.args
            ]
            client.send_instruction(Instruction('size', 1024, 768, 96))
            client.send_instruction(Instruction('audio', *list()))
            client.send_instruction(Instruction('video', *list()))
            client.send_instruction(Instruction('image', *list()))
            client.send_instruction(Instruction('connect', *connection_args))

            # self.message.reply_channel.send({"text":'0.,{0}.{1};'.format(len(cache_key),cache_key)},immediately=True)
            guacamolethread = GuacamoleThread(self.message, client)
            guacamolethread.setDaemon = True
            guacamolethread.start()

            guacamolethreadwrite = GuacamoleThreadWrite(self.message, client)
            guacamolethreadwrite.setDaemon = True
            guacamolethreadwrite.start()

    def disconnect(self, message, id):
        # close threading
        print('disconnect')
        try:
            log_object = Log.objects.get(id=id)
            cache_key = log_object.gucamole_client_id
            client = GuacamoleClient(
                settings.GUACD_HOST, settings.GUACD_PORT)
            client.send_instruction(Instruction('select', cache_key))
            instruction = client.read_instruction()
            kwargs = {'width': 1024, 'height': 768, 'read_only': 'true'}
            connection_args = [
                kwargs.get(arg.replace('-', '_'), '') for arg in instruction.args
            ]
            client.send_instruction(Instruction('size', 1024, 768, 96))
            client.send_instruction(Instruction('audio', *list()))
            client.send_instruction(Instruction('video', *list()))
            client.send_instruction(Instruction('image', *list()))
            client.send_instruction(Instruction('connect', *connection_args))
            client.send_instruction(Instruction('disconnect', *connection_args))
        except:
            pass
        finally:
            self.message.reply_channel.send({"accept": False})
