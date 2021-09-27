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
def discover_bags_zorya():
    """Calls the Discover Bags service in Zorya, if it exists."""
    if ServiceRegistry.objects.get(
            is_active=True,
            application__is_active=True,
            has_active_task=False,
            application__name__icontains="zorya",
            name__icontains="discover bags").exists():
        registry = ServiceRegistry.objects.get(
            is_active=True,
            application__is_active=True,
            has_active_task=False,
            application__name__icontains="zorya",
            name__icontains="discover bags")
        url = render_service_path(registry, '')
        return queue_request.delay(
            'post',
            url,
            headers={'Content-Type': 'application/json'},
            data=None,
            files=None,
            params={},
            service_id=registry.id
        )
    else:
        return {"detail": "No service matching the query parameters found."}
