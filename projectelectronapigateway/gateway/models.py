# -*- coding: utf-8 -*-
import requests, json
from django.db import models
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from rest_framework.authentication import get_authorization_header, BasicAuthentication
from rest_framework import HTTP_HEADER_ENCODING
import urllib.parse as urlparse


class Consumer(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    apikey = models.CharField(max_length=32)

    def __str__(self):
        return self.user.username


class Application(models.Model):
    name = models.CharField(max_length=64, unique=True)
    service_path = models.CharField(max_length=40)
    service_port = models.PositiveSmallIntegerField(null=True)

    def __str__(self):
        return self.service_path


class ServiceRegistry(models.Model):
    PLUGIN_CHOICE_LIST = (
        (0, _('Remote auth')),
        (1, _('Basic auth')),
        (2, _('Key auth')),
        (3, _('Server auth'))
    )
    HTTP_REQUESTS_METHODS = (
        ('GET', 'GET'),
        ('POST', 'POST'),
    )
    name = models.CharField(max_length=128, unique=True)
    application = models.ForeignKey(
        Application,
        on_delete=models.CASCADE,
    )
    description = models.TextField()
    external_uri = models.CharField(max_length=40)
    service_route = models.CharField(max_length=40)
    plugin = models.IntegerField(choices=PLUGIN_CHOICE_LIST, default=0)
    consumers = models.ManyToManyField(Consumer, blank=True)
    is_active = models.BooleanField(default=False)
    is_private = models.BooleanField(default=False)
    method = models.CharField(max_length=10,choices=HTTP_REQUESTS_METHODS)

    def check_plugin(self, request):
        if self.plugin == 0:
            return True, ''
            
        elif self.plugin == 1:
            auth = BasicAuthentication()
            try:
                user, password = auth.authenticate(request)
            except:
                return False, 'Authentication credentials were not provided'

            if self.consumers.filter(user=user):
                return True, ''
            else:
                return False, 'permission not allowed'
        elif self.plugin == 2:
            apikey = request.META.get('HTTP_APIKEY')
            consumers = self.consumers.all()
            for consumer in consumers:
                if apikey == consumer.apikey:
                    return True, ''
            return False, 'apikey need'
        elif self.plugin == 3:
            consumer = self.consumers.all()
            if not consumer:
                return False, 'consumer need'
            request.META['HTTP_AUTHORIZATION'] = requests.auth._basic_auth_str(consumer[0].user.username, consumer[0].apikey)
            return True, ''
        else:
            raise NotImplementedError("plugin %d not implemented" % self.plugin)

    def send_request(self, request):
        headers = {}
        if self.plugin != 1 and request.META.get('HTTP_AUTHORIZATION'):
            headers['authorization'] = request.META.get('HTTP_AUTHORIZATION')
        # headers['content-type'] = request.content_type

        strip = '/api/' + self.external_uri
        full_path = request.get_full_path()[len(strip):]
        service_port = (':{}'.format(self.application.service_port) if self.application.service_port > 0 else '')
        url = 'http://{}{}/{}{}'.format(
            self.application.service_path, service_port, self.service_route, full_path)
        parsed_url = urlparse.urlparse(url)
        parsed_url_parts = list(parsed_url)

        query = dict(urlparse.parse_qsl(parsed_url_parts[4]))
        query['format'] = 'json'

        parsed_url_parts[4] = urlparse.urlencode(query)
        url = urlparse.urlunparse(parsed_url_parts)

        print(url)

        method = request.method.lower()
        method_map = {
            'get': requests.get,
            'post': requests.post,
            # 'put': requests.put,
            # 'patch': requests.patch,
            # 'delete': requests.delete
        }

        for k,v in request.FILES.items():
            request.data.pop(k)
        
        if request.content_type and request.content_type.lower()=='application/json':
            data = json.dumps(request.data)
            headers['content-type'] = request.content_type
        else:
            data = request.data

        return method_map[method](url, headers=headers, data=data, files=request.FILES)

    def __str__(self):
        return self.name
