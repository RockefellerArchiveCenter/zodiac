import json

from celery.signals import task_postrun, task_prerun
from django_celery_results.models import TaskResult

from .models import RequestLog, ServiceRegistry


def update_service_status(kwargs, status):
    """Sets `has_active_task` property on Service"""
    if 'service_id' in kwargs['kwargs']:
        service = ServiceRegistry.objects.get(pk=kwargs['kwargs']['service_id'])
        service.has_active_task = status
        service.save()
        return service
    return None


def get_task_result_status(task_result):
    """Returns custom category of task result status"""
    task_result_status = 'Error'
    if task_result.status == 'SUCCESS':
        task_result_status = 'Idle'
        if json.loads(task_result.result).get('count', 0) > 0:
            task_result_status = 'Success'
    return task_result_status


@task_prerun.connect
def on_task_prerun(task_id=None, task=None, *args, **kwargs):
    """Marks service as active"""
    update_service_status(kwargs, True)


@task_postrun.connect
def on_task_postrun(task_id=None, task=None, retval=None, state=None, *args, **kwargs):
    """Marks service as inactive and saves TaskResult"""
    service = update_service_status(kwargs, False)
    if len(kwargs['args']) > 1:
        task_result = TaskResult.objects.get(task_id=task_id)
        RequestLog.objects.create(
            service=service,
            status_code=None,
            request_url=kwargs['args'][1],
            async_result_id=task_id,
            task_result=task_result,
            task_result_status=get_task_result_status(task_result),
        )
