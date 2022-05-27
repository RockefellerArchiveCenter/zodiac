from django_cron import CronJobBase, Schedule

from zodiac import settings

from .models import ServiceRegistry
from .tasks import queue_request
from .views_library import render_service_path


class QueueRequests(CronJobBase):
    code = "gateway.queue_services"
    RUN_EVERY_MINS = 0
    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)

    def do(self):
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
