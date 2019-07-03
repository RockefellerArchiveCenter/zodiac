# Create your tasks here
from __future__ import absolute_import, unicode_literals
import json
import requests
from django.utils import timezone

from celery import shared_task, current_task, group, chain
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
        for object_type in ['resource', 'subject', 'archival_object', 'person', 'organization', 'family']:
            # We call apply_async(), which is a more verbose version of delay(), in order to add `link` argument
            r = queue_request.apply_async(
                args=('post', render_service_path(service, '')),
                kwargs={'headers': {'Content-Type': 'application/json'},
                        'data': json.dumps({'object_type': object_type}),
                        'files': None,
                        'params': {'post_service_url': render_service_path(service.post_service, '')},
                        'service_id': service.id},
                link=process_archivesspace_changes.s())


@shared_task()
def process_archivesspace_changes(data):
    if len(data.get('updated')) > 0:
            uri = data.get('updated')[0]
            updated = group(
                        chain(queue_request_by_id.s(uri, ServiceRegistry.objects.get(name="Fetch ArchivesSpace URI").pk),
                              queue_request_by_id.s(ServiceRegistry.objects.get(name="Transform ArchivesSpace Data").pk),
                              queue_request_by_id.s(ServiceRegistry.objects.get(name="Add to Index").pk))() for uri in data.get('updated'))
            updated.delay()
    if len(data.get('deleted')) > 0:
        deleted = group(queue_request_by_name.s(uri, "Delete from Index", service_id=ServiceRegistry.objects.get(name="Delete From Index").pk) for uri in data.get('deleted'))
        deleted.delay()


@shared_task()
def queue_request_by_id(data, service_id):
    service = ServiceRegistry.objects.get(pk=service_id)
    if service.service_active():
        r = method_map['post'](
            render_service_path(service, ''),
            headers={'Content-Type': 'application/json'},
            data=json.dumps({'data': data}),
            files=None,
            params={'post_service_url': render_service_path(service.post_service)},
            )
        if r.status_code == 200:
            return r.json()
        raise Exception(r.json())


@shared_task()
def delete_successful():
    TaskResult.objects.filter(status="SUCCESS", date_done__lte=timezone.now()-timezone.timedelta(days=1)).delete()
