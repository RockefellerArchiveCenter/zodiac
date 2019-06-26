# Create your tasks here
from __future__ import absolute_import, unicode_literals
import json
import requests
from django.apps import apps
from django.urls import reverse
from django.utils import timezone
import urllib.parse as urlparse

from celery import shared_task, current_task
from django_celery_results.models import TaskResult

from zodiac import settings
from .models import ServiceRegistry
from .views_library import render_service_path

method_map = {
    'get': requests.get,
    'post': requests.post,
    # 'put': requests.put,
    # 'patch': requests.patch,
    # 'delete': requests.delete
}


@shared_task()
def queue_callbacks():
    completed = {'detail': {'callbacks': []}}
    for registry in ServiceRegistry.objects.filter(callback_service__isnull=False,
                                                   has_active_task=False, is_active=True,
                                                   application__is_active=True).order_by('callback_service__modified_time')[:settings.MAX_SERVICES]:
        callback = ServiceRegistry.objects.get(pk=registry.callback_service.pk)
        if not callback.has_active_task:
            url = render_service_path(callback, '')
            r = queue_request.delay(
                'post',
                url,
                headers={'Content-Type': 'application/json'},
                data=None,
                files=None,
                params={'post_service_url': render_service_path(callback.post_service)},
                service_id=callback.id
            )
            if r:
                completed['detail']['callbacks'].append({callback.name: r.id})
    return completed


@shared_task()
def queue_request(method, url, headers, data, files, params, service_id):
    r = method_map[method](url, headers=headers, data=data, files=files, params=params)
    if r.status_code == 200:
        return r.json()
    raise Exception(r.json())


@shared_task()
def fetch_archivesspace_changes():
    service = ServiceRegistry.objects.get(name="Fetch ArchivesSpace Changes") #this is janky
    if service.service_active():
        url = render_service_path(service, '')
        for object_type in ['resource', 'subject', 'archival_object', 'person', 'organization', 'family']:
            # We call apply_async(), which is a more verbose version of delay(), in order to add callback argument
            r = queue_request.apply_async(
                args=('post', url),
                kwargs={'headers': {'Content-Type': 'application/json'},
                        'data': json.dumps({'object_type': object_type}),
                        'files': None,
                        'params': {'post_service_url': render_service_path(service.post_service)},
                        'service_id': service.id},
                link=process_archivesspace_changes.s())


@shared_task()
def process_archivesspace_changes(data):
    for obj in data.get('updated'):
        print("UPDATE", obj)
    for obj in data.get('deleted'):
        print("DELETE", obj)
    # service = ServiceRegistry.objects.get(name="Process ArchivesSpace Changes")
    #
    # if service.service_active():
    #     url = render_service_path(registry, '')
    #     for object_type in ['resource', 'subject', 'archival_object', 'person', 'organization', 'family']:
    #         r = queue_request.delay(
    #             'post',
    #             url,
    #             headers={'Content-Type': 'application/json'},
    #             data=json.dumps({'object_type': object_type}),
    #             files=None,
    #             params={'post_service_url': render_service_path(service.post_service)},
    #             service_id=service.id
    #         )


@shared_task()
def delete_successful():
    TaskResult.objects.filter(status="SUCCESS", date_done__lte=timezone.now()-timezone.timedelta(days=1)).delete()
