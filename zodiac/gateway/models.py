import json

from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.utils.translation import ugettext_lazy as _
from django.urls import reverse

from django_celery_results.models import TaskResult


class User(AbstractUser):
    pass


class Source(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    apikey = models.CharField(max_length=32)

    def __str__(self):
        return self.user.username

    def get_absolute_url(self):
        return reverse('sources-detail', args=[self.pk])

    def get_update_url(self):
        return reverse('sources-update', args=[self.pk])

    @classmethod
    def get_list_url(self):
        return reverse('sources-list')


class Application(models.Model):
    name = models.CharField(max_length=64, unique=True)
    is_active = models.BooleanField(default=True)
    app_host = models.CharField(max_length=40)
    app_port = models.PositiveSmallIntegerField(null=True, blank=True)
    health_check_path = models.CharField(max_length=255, null=True, blank=True)
    created_time = models.DateTimeField(auto_now_add=True)
    modified_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.app_host

    def get_update_url(self):
        return reverse('applications-update', args=[self.pk])

    def get_absolute_url(self):
        return reverse('applications-detail', args=[self.pk])

    @classmethod
    def get_list_url(self):
        return reverse('applications-list')


class ServiceRegistry(models.Model):
    REMOTE_AUTH = 0
    BASIC_AUTH = 1
    KEY_AUTH = 2
    SERVER_AUTH = 3
    PLUGIN_CHOICE_LIST = (
        (REMOTE_AUTH, _('Remote auth')),
        (BASIC_AUTH, _('Basic auth')),
        (KEY_AUTH, _('Key auth')),
        (SERVER_AUTH, _('Server auth'))
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
    sources = models.ManyToManyField(Source, blank=True)
    is_active = models.BooleanField(default=True)
    is_private = models.BooleanField(default=False)
    has_active_task = models.BooleanField(default=False)
    method = models.CharField(max_length=10, choices=HTTP_REQUESTS_METHODS)
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

    @classmethod
    def get_list_url(self):
        return reverse('services-list')

    def get_clear_errors_url(self):
        return reverse('services-clear-errors', args=[self.pk])

    def get_trigger_url(self):
        return reverse('services-trigger', args=[self.pk])

    def service_active(self):
        return True if (self.is_active and self.application.is_active) else False


class RequestLog(models.Model):
    service = models.ForeignKey(
        ServiceRegistry,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='requestlog'
    )
    status_code = models.CharField(max_length=4, blank=True, null=True)
    request_url = models.URLField(blank=True, null=True)
    async_result_id = models.CharField(max_length=36, blank=True, null=True)
    created_time = models.DateTimeField(auto_now_add=True)
    task_result = models.ForeignKey(TaskResult, on_delete=models.CASCADE, blank=True, null=True, related_name='request_log')
    task_result_status = models.CharField(max_length=100, choices=(('success', 'Success'), ('error', 'Error'), ('idle', 'Idle')), blank=True, null=True)

    def error_messages(self):
        errors = []
        for e in json.loads(self.task_result.result).get('exc_message'):
            try:
                emess = e.get('detail')
            except:
                emess = e
            errors.append(emess)
        return errors
