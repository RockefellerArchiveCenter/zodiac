# -*- coding: utf-8 -*-
import requests, json
from django.db import models
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from rest_framework.authentication import get_authorization_header, BasicAuthentication
from rest_framework import HTTP_HEADER_ENCODING
import urllib.parse as urlparse
from django.urls import reverse

from .tasks import queue_request


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
    is_active = models.BooleanField(default=True)
    app_host = models.CharField(max_length=40)
    app_port = models.PositiveSmallIntegerField(null=True, blank=True)
    created_time = models.DateTimeField(auto_now_add=True)
    modified_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.app_host

    def get_update_url(self):
        return reverse('systems-update', args=[self.pk])

    def get_absolute_url(self):
        return reverse('systems-detail', args=[self.pk])


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
    is_active = models.BooleanField(default=True)
    is_private = models.BooleanField(default=False)
    method = models.CharField(max_length=10,choices=HTTP_REQUESTS_METHODS)
    callback_service = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    post_service = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="poster",
        related_query_name="poster",
    )
    created_time = models.DateTimeField(auto_now_add=True)
    modified_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def get_update_url(self):
        return reverse('services-update', args=[self.pk])

    def get_absolute_url(self):
        return reverse('services-detail', args=[self.pk])

    def get_trigger_url(self):
        return reverse('services-trigger', args=[self.pk])

    def get_async_results_data_url(self):
        return reverse('services-async-results', args=[self.pk])

    def retrieve_async_result_logs(self):
        data = []
        # can do a flat query here
        tasks = ServiceRegistryTask.objects.filter(service=self)
        for task in tasks:

            data.append([task.async_result_id])
        return data

    def store_async_result(self, async_result_id):
        record = ServiceRegistryTask(
            service = self,
            async_result_id = async_result_id
        ).save()


    def service_active(self):
        return True if (self.is_active and self.application.is_active) else False

    def can_safely_execute(self):
        # check actives for service and system
        if not self.service_active():
            return False
        # if self.callback_service:
        #     if not self.callback_service.service_active():
        #         return False
        return True

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

    def render_path(self, uri=''):

        app_port = (':{}'.format(self.application.app_port) if self.application.app_port > 0 else '')
        url = 'http://{}{}/{}{}'.format(
            self.application.app_host, app_port, self.service_route, uri)

        parsed_url = urlparse.urlparse(url)
        parsed_url_parts = list(parsed_url)

        query = dict(urlparse.parse_qsl(parsed_url_parts[4]))
        query['format'] = 'json'

        parsed_url_parts[4] = urlparse.urlencode(query)

        return urlparse.urlunparse(parsed_url_parts)

    def send_request(self, request={}):
        headers = {}
        files = {}

        if request:
            files = request.FILES

            if self.plugin != 1 and request.META.get('HTTP_AUTHORIZATION'):
                headers['authorization'] = request.META.get('HTTP_AUTHORIZATION')
            # headers['content-type'] = request.content_type

            strip = '/api/' + self.external_uri
            full_path = request.get_full_path()[len(strip):]

            url = self.render_path(full_path)

            method = request.method.lower()

            for k,v in request.FILES.items():
                request.data.pop(k)

            #force json

            if request.content_type and request.content_type.lower()=='application/json':
                data = json.dumps(request.data)
                headers['content-type'] = request.content_type
            else:
                data = request.data

        else:
            headers['content-type'] = 'application/json'
            method = 'get'
            data = {}
            url = self.render_path('')

        # chain exceptions
        async_result = queue_request.delay(
            method,
            url,
            headers=headers,
            data=data,
            files=files,
            params={'post_service_url': self.render_post_service_url()}
        )
        print(async_result, 'this is async')

        return async_result.id

    def render_post_service_url(self):
        if not self.post_service:
            return ''
        return self.post_service.render_path()




class RequestLog(models.Model):
    service = models.ForeignKey(
        ServiceRegistry,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    #consumer
    status_code = models.CharField(max_length=4, blank=True, null=True)
    request_url = models.URLField(blank=True, null=True)
    async_result_id = models.CharField(max_length=30, blank=True, null=True)
    created_time = models.DateTimeField(auto_now_add=True)

    @classmethod
    def create(cls, service, status_code, request_url, async_result_id=None):
        record = cls(
            service = service,
            status_code = status_code,
            request_url = request_url,
            async_result_id = async_result_id
        ).save()
        return record


class ServiceRegistryTask(models.Model):
    service = models.ForeignKey(
        ServiceRegistry,
        on_delete=models.CASCADE
    )
    async_result_id = models.CharField(max_length=40)

    def __str__(self):
        return self.async_result_id