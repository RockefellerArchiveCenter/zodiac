# Create your tasks here
from __future__ import absolute_import, unicode_literals
from celery import shared_task, current_task
from celery.result import AsyncResult

import requests

# from gateway.models import ServiceRegistryTask

@shared_task()
def queue_request(method, url, headers, data, files, params):
    method_map = {
        'get': requests.get,
        'post': requests.post,
        # 'put': requests.put,
        # 'patch': requests.patch,
        # 'delete': requests.delete
    }

    r = method_map[method](url, headers=headers, data=data, files=files, params=params)

    # VALIDATE REsponse
    #   check for json
    #   if request OK
    #       save ServiceRegistryTask with result

    # print(current_task.request.id, 'id of current task')
    # print(async_result_id)
    return r.text
