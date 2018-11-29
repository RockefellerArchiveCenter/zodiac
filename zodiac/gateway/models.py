# -*- coding: utf-8 -*-
import ast

from django.db import models
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.urls import reverse

from django_celery_results.models import TaskResult


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
        return reverse('applications-update', args=[self.pk])

    def get_absolute_url(self):
        return reverse('applications-detail', args=[self.pk])


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

    def service_active(self):
        return True if (self.is_active and self.application.is_active) else False

    def has_active_task(self):
        for task in TaskResult.objects.filter(status__in=["PENDING", "STARTED", "RETRY"]):
            if (ast.literal_eval(task.task_kwargs).get('service_id') == self.pk):
                print("Active task discovered", task)
                return True
        return False

    def can_safely_execute(self):
        # check actives for service and system
        if not self.service_active():
            return False
        # if self.callback_service:
        #     if not self.callback_service.service_active():
        #         return False
        return True


class RequestLog(models.Model):
    service = models.ForeignKey(
        ServiceRegistry,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    status_code = models.CharField(max_length=4, blank=True, null=True)
    request_url = models.URLField(blank=True, null=True)
    async_result_id = models.CharField(max_length=30, blank=True, null=True)
    created_time = models.DateTimeField(auto_now_add=True)

    @classmethod
    def create(cls, service, status_code, request_url, async_result_id=None):
        record = cls(
            service=service,
            status_code=status_code,
            request_url=request_url,
            async_result_id=async_result_id
        ).save()
        return record
