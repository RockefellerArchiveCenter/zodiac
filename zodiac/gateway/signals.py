from celery.signals import task_prerun, task_postrun
from django_celery_results.models import TaskResult
from .models import ServiceRegistry, RequestLog

@task_prerun.connect
def on_task_prerun(task_id=None, task=None, *args, **kwargs):
    # Mark service as active
    if 'service_id' in kwargs['kwargs']:
        service = ServiceRegistry.objects.get(pk=kwargs['kwargs']['service_id'])
        service.has_active_task = True
        service.save()

@task_postrun.connect
def on_task_postrun(task_id=None, task=None, retval=None, state=None, *args, **kwargs):
    # Mark service as inactive
    def update_service(kwargs):
        if 'service_id' in kwargs['kwargs']:
            service = ServiceRegistry.objects.get(pk=kwargs['kwargs']['service_id'])
            service.has_active_task = False
            service.save()
            return service
        return None

    # Add result to request log
    if len(kwargs['args']) > 1:
        task_result = TaskResult.objects.get(task_id=task_id)
        task_result_status = 'Error'
        if task_result.status == 'SUCCESS':
            task_result_status = 'Idle'
            if task_result.result.get('count') > 0:
                task_result_status = 'Success'
        request_log = RequestLog.objects.create(
            service=update_service(kwargs),
            status_code=None,
            request_url=kwargs['args'][1],
            async_result_id=task_id,
            task_result=task_result,
            task_result_status=task_result_status,
        )
