import time
from contextlib import contextmanager

import requests
from celery import shared_task
from django.core.cache import cache
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


LOCK_EXPIRE = 60 * 10  # Lock expires in 10 minutes


@contextmanager
def memcache_lock(lock_id, oid):
    timeout_at = time.monotonic() + LOCK_EXPIRE - 3
    status = cache.add(lock_id, oid, LOCK_EXPIRE)
    try:
        yield status
    finally:
        if time.monotonic() < timeout_at and status:
            cache.delete(lock_id)


@shared_task(bind=True)
def queue_services(self):
    """Queues tasks for regularly scheduled services.

    The maximum number of services to trigger at once can be changed by
    setting the `MAX_SERVICES` config value. Services which have been triggered
    least recently are triggered first. Services which are externally triggered
    are excluded from this task.
    """
    completed = {'detail': {'services': []}}

    for registry in ServiceRegistry.objects.filter(
            is_active=True,
            has_active_task=False,
            application__is_active=True,
            has_external_trigger=False).order_by('modified_time')[:settings.MAX_SERVICES]:
        url = render_service_path(registry, '')
        with memcache_lock(registry.name.replace(" ", "_"), self.app.oid) as acquired:
            if acquired:
                queue_request.delay(
                    'post',
                    url,
                    headers={'Content-Type': 'application/json'},
                    data=None,
                    files=None,
                    params={},
                    service_id=registry.id)
                completed['detail']['services'].append(registry.name)
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
    """Deletes expired success messages."""
    expired_time = timezone.now() - timezone.timedelta(days=settings.DELETE_SUCCESSFUL_AFTER)
    TaskResult.objects.filter(status="SUCCESS", date_done__lte=expired_time).delete()
