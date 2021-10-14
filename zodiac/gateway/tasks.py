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

    for registry in ServiceRegistry.objects.filter(
            is_active=True, has_active_task=False,
            application__is_active=True).order_by('modified_time'):
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
            if count >= settings.MAX_SERVICES:
                break
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


@shared_task()
def trigger_first_services():
    """Calls Services which are not triggered by another service.

    The FILTER_PARAMS variable is a list of filter params values which should
    match one or more ServiceRegistry objects.
    """

    QUERY_PARAMS = [{"is_active": True, "application__is_active": True,
                     "has_active_task": False,
                     "application__name__icontains": "zorya",
                     "name__icontains": "download objects"},
                    {"is_active": True, "application__is_active": True,
                     "has_active_task": False,
                     "application__name__icontains": "pictor",
                     "name__icontains": "bag preparer"}
                    ]

    completed = {'detail': {'services': []}}
    count = 0
    for params in QUERY_PARAMS:
        if ServiceRegistry.objects.filter(**params).exists():
            for registry in ServiceRegistry.objects.filter(**params):
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
                    completed['detail']['services'].append({registry.name: r.id})
                count += 1
    return completed
