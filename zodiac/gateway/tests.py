import random
from unittest.mock import patch

from django.core.management import call_command
from django.test import Client, TestCase
from django.urls import reverse
from zodiac import settings

from .models import (Application, RequestLog, ServiceRegistry, Source,
                     TaskResult, User)
from .signals import on_task_postrun, on_task_prerun
from .tasks import delete_successful, queue_callbacks


class GatewayTestCase(TestCase):
    fixtures = ['initial_data.json']

    def setUp(self):
        self.client = Client()
        call_command("setup_services", "--reset")

    def test_queue_tasks(self):
        queued = queue_callbacks()
        self.assertTrue(
            isinstance(queued, dict), "queue_callbacks() did not return JSON.")
        self.assertTrue(
            len(queued["detail"]["callbacks"]) <= settings.MAX_SERVICES, "Too many services were called.")

        for service in ServiceRegistry.objects.all():
            trigger = self.client.get(reverse('services-trigger', kwargs={'pk': service.id}))
            self.assertEqual(trigger.status_code, 200, "Error triggering service: {}".format(trigger.json()))

    def test_delete_tasks(self):
        deleted = delete_successful()
        self.assertIsNot(deleted, False)

    @patch('gateway.signals.update_service_status')
    def test_signals(self, mock_update_service_status):
        task = TaskResult.objects.create()
        service = random.choice(ServiceRegistry.objects.all())

        on_task_prerun(task_id=task.id, kwargs={"service_id": service.pk})
        mock_update_service_status.assert_called_once()
        mock_update_service_status.assert_called_with({"kwargs": {"service_id": service.pk}}, True)

        mock_update_service_status.reset_mock()

        task.status = "SUCCESS"
        task.save()
        on_task_postrun(task_id=task.id, kwargs={"service_id": service.pk}, args=[{"detail": "success"}])
        mock_update_service_status.assert_called_once()
        mock_update_service_status.assert_called_with({"kwargs": {"service_id": service.pk}, "args": [{"detail": "success"}]}, False)

    def test_gateway_views(self):
        for service in ServiceRegistry.objects.filter(
                plugin=ServiceRegistry.REMOTE_AUTH).exclude(application__name="Aurora"):
            url = "http://localhost/api/{}/{}".format(service.external_uri.rstrip("/"), service.service_route)
            resp = self.client.post(url)
            self.assertEqual(resp.status_code, 200, "{} returned an error: {}".format(service, resp.json()))

    def test_missing_service(self):
        url = "http://localhost/api/missing/not-here"
        resp = self.client.post(url)
        self.assertEqual(
            resp.status_code, 400,
            "Did not return expected error code, got {} instead.".format(resp.status_code))
        self.assertEqual(
            resp.json(),
            {"detail": "No service registry matching path missing and method POST."})

    def test_apikey_auth(self):
        for service in ServiceRegistry.objects.filter(plugin=ServiceRegistry.KEY_AUTH):
            source = random.choice(service.sources.all())
            apikey = source.apikey
            url = "http://localhost/api/{}/{}".format(service.external_uri.rstrip("/"), service.service_route)
            resp = self.client.post(url, HTTP_APIKEY=apikey)
            self.assertEqual(resp.status_code, 200, "{} returned an error: {}".format(service, resp.json()))

    def test_list_views(self):
        for list_view in [
                "dashboard", "services-list", "applications-list",
                "results-list", "sources-list", "users-list",
                "users-login"]:
            response = self.client.get(reverse(list_view))
            self.assertEqual(response.status_code, 200, "{} returned error: {}".format(list_view, response))

    def test_detail_views(self):
        for detail_view, cls in [
                ("services-detail", ServiceRegistry), ("applications-detail", Application),
                ("results-detail", RequestLog), ("sources-detail", Source),
                ("users-detail", User)]:
            obj = random.choice(cls.objects.all())
            response = self.client.get(reverse(detail_view, kwargs={"pk": obj.pk}))
            self.assertEqual(response.status_code, 200)

    def test_datatable_view(self):
        datatable_resp = self.client.get(reverse("results-data"))
        self.assertEqual(
            datatable_resp.status_code, 200,
            "results-data returned error:".format(datatable_resp.json()))
        self.assertTrue(isinstance(
            datatable_resp.json()["data"], list),
            "Expected `data` to be a list, got {} instead".format(type(datatable_resp.json()["data"])))

    def test_clear_errors_view(self):
        service = random.choice(ServiceRegistry.objects.all())
        clear_resp = self.client.get(reverse("services-clear-errors", kwargs={"pk": service.pk}))
        self.assertEqual(
            clear_resp.status_code, 200,
            "services-clear-errors returned error: {}".format(clear_resp.json()))
        self.assertEqual(
            clear_resp.json()["SUCCESS"], 1,
            "services-clear-errors did not return a successful response")
