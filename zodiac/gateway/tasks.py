# Create your tasks here
from __future__ import absolute_import, unicode_literals
import requests
from django.apps import apps

from celery import shared_task, current_task

from .models import ServiceRegistry

method_map = {
    'get': requests.get,
    'post': requests.post,
    # 'put': requests.put,
    # 'patch': requests.patch,
    # 'delete': requests.delete
}


@shared_task()
def queue_callbacks():
    completed = []
    for registry in ServiceRegistry.objects.filter(callback_service__isnull=False):
        if registry.service_active(): # TODO: also check to see if last service run was okay
            callback = ServiceRegistry.objects.get(pk=registry.callback_service.pk)
            # TODO: is there a way to do this without hardcoding?
            url = 'http://localhost:8001{}'.format(callback.get_trigger_url())
            r = requests.get(url)
            if r:
                completed.append(callback.name)
    return {'detail': 'Callbacks completed: {}'.format(', '.join(completed))}


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
