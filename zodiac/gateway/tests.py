from django.test import Client, TestCase
from django.urls import reverse
from zodiac import settings

from .models import ServiceRegistry, TaskResult
from .tasks import delete_successful, queue_callbacks


class GatewayTestCase(TestCase):
    fixtures = ['initial_data.json']

    def setUp(self):
        self.client = Client()

    def queue_tasks(self):
        queued = queue_callbacks()
        self.assertTrue(
            isinstance(queued, dict), "queue_callbacks() did not return JSON.")
        self.assertTrue(
            len(queued["detail"]["callbacks"]) <= settings.MAX_SERVICES, "Too many services were called.")

        for service in ServiceRegistry.objects.all():
            trigger = self.client.get(reverse('services-trigger', kwargs={'pk': service.id}))
            self.assertEqual(trigger.status_code, 200, "Error triggering service: {}".format(trigger.json()))

        delete_successful()
        self.assertEqual(len(TaskResult.objects.filter(status="SUCCESS")), 0, "Not all successful Tasks were deleted.")

    def test_gateway(self):
        self.queue_tasks()
