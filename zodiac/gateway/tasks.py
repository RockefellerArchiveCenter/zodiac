import requests
from celery import shared_task
from django.utils import timezone
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
    count = 0

    while count < settings.MAX_SERVICES:
        registry = ServiceRegistry.objects.filter(
            is_active=True, has_active_task=False,
            application__is_active=True).order_by('modified_time')[0]
        if registry.is_callback:
            url = render_service_path(registry, '')
            r = queue_request.delay(
                'post',
                url,
                headers={'Content-Type': 'application/json'},
                data=None,
                files=None,
                params={},
                service_id=registry.id
            )
            if r:
                completed['detail']['callbacks'].append({registry.name: r.id})
            count += 1
        else:
            registry.save()
    return completed


@shared_task()
def queue_request(method, url, headers, data, files, params, service_id):
    r = method_map[method](url, headers=headers, data=data, files=files, params=params)
    if r.status_code in [200, 201]:
        return r.json()
    else:
        try:
            message = r.json()
        except Exception:
            message = str(r)
        raise Exception(message)


@shared_task()
def delete_successful():
    TaskResult.objects.filter(status="SUCCESS",
                              date_done__lte=timezone.now() - timezone.timedelta(hours=settings.DELETE_SUCCESSFUL_AFTER)).delete()
