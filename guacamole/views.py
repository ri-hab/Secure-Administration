# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.conf import settings
from django.http import HttpResponse, StreamingHttpResponse, JsonResponse
from django.shortcuts import render, render_to_response
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.views.generic import View, DetailView
from django.core.exceptions import ObjectDoesNotExist
from django.utils.timezone import now
import logging
import threading
import uuid
import os
import traceback
try:
    import simplejson as json
except ImportError:
    import json
from jumpserver3s.settings import MEDIA_URL
from jumpserver3s.models import Log
from app_user.models import Server
from app_manager.mixins import LoginRequiredMixin
from guacamole.client import GuacamoleClient
from guacamole.guacamolethreading  import get_redis_instance
from guacamole.instruction import GuacamoleInstruction as Instruction

logger = logging.getLogger(__name__)
sockets = {}
sockets_lock = threading.RLock()
read_lock = threading.RLock()
write_lock = threading.RLock()
pending_read_request = threading.Event()

class Index(LoginRequiredMixin,View):
    model = Server
    id = Server.id
    def get(self,request,id):
        print("this is form views id: {}".format(id))
        return render(request,'guacamole/index.html', locals())

class LogPlay(LoginRequiredMixin,DetailView):
    model = Log
    template_name = 'guacamole/logplay.html'

    def get_context_data(self, **kwargs):
        context = super(LogPlay, self).get_context_data(**kwargs)
        objects = kwargs['object']
        print("objects: {}".format(objects))
        record = os.path.join(settings.MEDIA_DIR,"records")
        context['logpath'] = '{0}/{1}-{2}-{3}/{4}'.format("/media/records",objects.start_time.year,objects.start_time.month,objects.start_time.day,objects.log)
        print("logpath: {}".format(context['logpath']))
        return context

class SshLogPlay(LoginRequiredMixin,DetailView):
    model = Log
    def get(self,request,pk):
        return render(request,'guacamole/sshlogplay.html')

    def get_context_data(self, **kwargs):
        context = super(SshLogPlay, self).get_context_data(**kwargs)
        objects = kwargs['object']
        context['logpath'] = '{0}{1}-{2}-{3}/{4}.json'.format("/media/records",objects.start_time.year,objects.start_time.month,objects.start_time.day,objects.log)
        return context

class SshTerminalMonitor(LoginRequiredMixin,DetailView):
    model = Log
    template_name = 'guacamole/sshterminalmonitor.html'
    queryset = Log.objects.all()
    context_object_name = 'logs'


class SshTerminalKill(LoginRequiredMixin,View):
    def post(self,request):
        print("hi this from sshterminal kill")
        if request.is_ajax():
            channel_name = request.POST.get('channel_name',None)
            print("channel_name: {}".format(channel_name))

            try:
                data = Log.objects.get(channel=channel_name)
                print("data: {}".format(data))
                if data.is_finished:
                    return JsonResponse({'status':False,'message':'Ssh terminal does not exist!'})
                else:
                    data.end_time = now()
                    data.is_finished = True
                    data.save()

                    queue = get_redis_instance()
                    redis_channel = queue.pubsub()
                    queue.publish(channel_name, json.dumps(['close']))

                    return JsonResponse({'status':True,'message':'Terminal has been killed !'})
            except ObjectDoesNotExist:
                return JsonResponse({'status':False,'message':'Request object does not exist!'})

class GuacmoleMonitor(LoginRequiredMixin,DetailView):
    model = Log
    template_name = 'guacamole/guacamolemonitor.html'

    def get_context_data(self, **kwargs):
        context = super(GuacmoleMonitor, self).get_context_data(**kwargs)
        objects = kwargs['object']
        return context

class GuacamoleKill(LoginRequiredMixin,View):
    def post(self,request):
        if request.is_ajax():
            print('request: {}'.format(request.POST))
            id = request.POST.get('id',None)
            print('id: {}'.format(id))
            try:
                log_object = Log.objects.get(id=id)
                queue = get_redis_instance()
                queue.pubsub()
                queue.publish(log_object.channel, '10.disconnect;')
                log_object.end_time = now()
                log_object.is_finished = True
                log_object.save()
                return JsonResponse({'status':True,'message':'Session has been killed !'})
            except ObjectDoesNotExist:
                return JsonResponse({'status':True,'message':'Request object does not exist!'})
            except Exception as e:
                log_object = Log.objects.get(id=id)
                log_object.end_time = now()
                log_object.is_finished = True
                log_object.save()
                return JsonResponse({'status':False,'message':str(e)})

@csrf_exempt
def tunnel(request):
    qs = request.META['QUERY_STRING']
    logger.info('tunnel {}'.format(qs))
    if qs == 'connect':
        return _do_connect(request)
    else:
        tokens = qs.split(':')
        if len(tokens) >= 2:
            if tokens[0] == 'read':
                return _do_read(request, tokens[1])
            elif tokens[0] == 'write':
                return _do_write(request, tokens[1])

    return HttpResponse(status=400)


def _do_connect(request):
    # Connect to guacd daemon
    client = GuacamoleClient(settings.GUACD_HOST, settings.GUACD_PORT)
    client.handshake(protocol='rdp',
                     hostname=settings.SSH_HOST,
                     port=settings.SSH_PORT,
                     username=settings.SSH_USER,
                     password=settings.SSH_PASSWORD)
    # security='any',)

    cache_key = str(uuid.uuid4())
    with sockets_lock:
        logger.info('Saving socket with key {}'.format(cache_key))
        sockets[cache_key] = client

    response = HttpResponse(content=cache_key)
    response['Cache-Control'] = 'no-cache'

    return response


def _do_read(request, cache_key):
    pending_read_request.set()

    def content():
        with sockets_lock:
            client = sockets[cache_key]

        with read_lock:
            pending_read_request.clear()

            while True:
                instruction = client.receive()
                if instruction:
                    yield instruction
                else:
                    break

                if pending_read_request.is_set():
                    logger.info('Letting another request take over.')
                    break

            # End-of-instruction marker
            yield '0.;'

    response = StreamingHttpResponse(content(),
                                     content_type='application/octet-stream')
    response['Cache-Control'] = 'no-cache'
    return response


def _do_write(request, cache_key):
    with sockets_lock:
        client = sockets[cache_key]

    with write_lock:
        while True:
            chunk = request.read(8192)
            if chunk:
                client.send(chunk)
            else:
                break

    response = HttpResponse(content_type='application/octet-stream')
    response['Cache-Control'] = 'no-cache'
    return response
