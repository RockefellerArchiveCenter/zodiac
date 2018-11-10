# Create your tasks here
from __future__ import absolute_import, unicode_literals
import requests
from django.apps import apps
import urllib.parse as urlparse

from celery import shared_task, current_task

from .models import ServiceRegistry
from .views_library import render_service_path, render_post_service_url

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
    for registry in ServiceRegistry.objects.filter(callback_service__isnull=False):
        if registry.service_active(): # TODO: also check to see if last service run was okay
            callback = ServiceRegistry.objects.get(pk=registry.callback_service.pk)
            url = render_service_path(callback, '')
            r = queue_request.delay(
                'post',
                url,
                headers={'Content-Type': 'application/json'},
                data=None,
                files=None,
                params={'post_service_url': render_post_service_url(callback)}
            )
            if r:
                completed['detail']['callbacks'].append({callback.name: r.id})
    return completed


@shared_task()
def queue_request(method, url, headers, data, files, params):
    r = method_map[method](url, headers=headers, data=data, files=files, params=params)

    # VALIDATE REsponse
    #   check for json
    #   if request OK
    #       save ServiceRegistryTask with result

    # print(current_task.request.id, 'id of current task')
    # print(async_result_id)
    return r.text