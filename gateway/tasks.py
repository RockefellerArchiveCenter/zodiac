import requests
from celery import shared_task
from django.utils import timezone
from django_celery_results.models import TaskResult

from zodiac import settings

method_map = {
    'get': requests.get,
    'post': requests.post,
    # 'put': requests.put,
    # 'patch': requests.patch,
    # 'delete': requests.delete
}


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
