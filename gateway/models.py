import json
from http.client import responses

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
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
        return "{} ({}:{})".format(self.name, self.app_host, self.app_port)

    def get_update_url(self):
        return reverse('applications-update', args=[self.pk])

    def get_absolute_url(self):
        return reverse('applications-detail', args=[self.pk])

    @classmethod
    def get_list_url(self):
        return reverse('applications-list')


class ServiceRegistry(models.Model):
    REMOTE_AUTH = 0
    KEY_AUTH = 2
    PLUGIN_CHOICE_LIST = (
        (REMOTE_AUTH, _('Remote auth')),
        (KEY_AUTH, _('Key auth')),
    )
    HTTP_REQUESTS_METHODS = (
        ('GET', 'GET'),
        ('POST', 'POST'),
    )
    name = models.CharField(max_length=128)
    application = models.ForeignKey(
        Application,
        on_delete=models.CASCADE,
    )
    description = models.TextField()
    external_uri = models.CharField(max_length=40, blank=True, null=True)
    service_route = models.CharField(max_length=40)
    plugin = models.IntegerField(choices=PLUGIN_CHOICE_LIST, default=0)
    sources = models.ManyToManyField(Source, blank=True)
    is_active = models.BooleanField(default=True)
    is_private = models.BooleanField(default=False)
    has_active_task = models.BooleanField(default=False)
    has_external_trigger = models.BooleanField(default=False)
    method = models.CharField(max_length=10, choices=HTTP_REQUESTS_METHODS)
    created_time = models.DateTimeField(auto_now_add=True)
    modified_time = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["application__name", "name"]

    # TODO: validation
    # - unique together: application__app_host, application__app_port, service_route
    # - external_uri required when has_external_trigger == True

    def __str__(self):
        return self.name

    @property
    def full_name(self):
        return "{}: {}".format(self.application.name, self.name)

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

    @property
    def error_messages(self):
        # todo fix it here.
        errors = []
        if self.task_result:
            for e in json.loads(self.task_result.result).get('exc_message'):
                try:
                    emess = e.get('detail')
                except BaseException:
                    try:
                        code = int(e[e.find("[") + 1:e.find("]")]).replace("<", "").replace(">", "")
                        emess = f"{e}: {responses[code]}"
                    except BaseException:
                        emess = e
                errors.append(emess)
        return errors
