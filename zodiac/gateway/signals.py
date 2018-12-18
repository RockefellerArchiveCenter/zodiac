from celery.signals import *
from .models import ServiceRegistry

@task_prerun.connect
def on_task_prerun(task_id=None, task=None, *args, **kwargs):
    if 'service_id' in kwargs['kwargs']:
        service = ServiceRegistry.objects.get(pk=kwargs['kwargs']['service_id'])
        service.has_active_task = True
        service.save()

@task_postrun.connect
def on_task_postrun(task_id=None, task=None, retval=None, state=None, *args, **kwargs):
    if 'service_id' in kwargs['kwargs']:
        service = ServiceRegistry.objects.get(pk=kwargs['kwargs']['service_id'])
        service.has_active_task = False
        service.save()
