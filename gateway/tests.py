import json
import random
from unittest.mock import patch

from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse

from zodiac import settings

from .cron import QueueRequests
from .models import (Application, RequestLog, ServiceRegistry, Source,
                     TaskResult, User)
from .signals import (get_task_result_status, on_task_postrun, on_task_prerun,
                      update_service_status)
from .tasks import delete_successful
from .views_library import render_service_path


class CronTestCase(TestCase):

    def setUp(self):
        call_command("setup_services", "--reset")

    @patch("gateway.tasks.queue_request.delay")
    def test_queue_services(self, mock_queue):
        queued = QueueRequests().do()
        self.assertTrue(
            isinstance(queued, str), "queue_services() did not return a string.")
        self.assertTrue(
            len(json.loads(queued)["detail"]["services"]) == settings.MAX_SERVICES, "Incorrect number of services called.")

        for service in ServiceRegistry.objects.all():
            trigger = self.client.get(reverse('services-trigger', kwargs={'pk': service.id}))
            self.assertEqual(trigger.status_code, 200, "Error triggering service: {}".format(trigger.json()))
            self.assertEqual(trigger.json(), {"SUCCESS": 1})
            mock_queue.assert_called_with(
                'post',
                render_service_path(service, ""),
                data={},
                files={},
                headers={'content-type': 'application/json'},
                params={},
                service_id=service.pk)


class GatewayTestCase(TestCase):

    def setUp(self):
        call_command("setup_services", "--reset")

    def test_active_task(self):
        """Ensures a service with an active task is not triggered."""
        service = random.choice(ServiceRegistry.objects.all())
        service.has_active_task = True
        service.save()
        trigger = self.client.get(reverse('services-trigger', kwargs={'pk': service.id}))
        self.assertEqual(trigger.status_code, 200, "Error triggering service with active task: {}".format(trigger.json()))
        self.assertEqual(trigger.json(), {"SUCCESS": 0})

    def test_delete_tasks(self):
        deleted = delete_successful()
        self.assertIsNot(deleted, False)

    @patch('gateway.signals.update_service_status')
    def test_on_task_prerun(self, mock_update_service_status):
        """Asserts that signals call the appropriate methods."""
        task = TaskResult.objects.create(task_id=1)
        service = random.choice(ServiceRegistry.objects.all())

        on_task_prerun(task_id=task.id, kwargs={"service_id": service.pk})
        mock_update_service_status.assert_called_once()
        mock_update_service_status.assert_called_with({"kwargs": {"service_id": service.pk}}, True)

    @patch('gateway.signals.update_service_status')
    @patch('gateway.signals.get_task_result_status')
    def test_on_task_postrun(self, mock_get_task_result_status, mock_update_service_status):
        task = TaskResult.objects.create(task_id=2)
        service = random.choice(ServiceRegistry.objects.filter(has_external_trigger=False))

        mock_get_task_result_status.return_value = "Idle"
        mock_update_service_status.return_value = service
        previous_len = len(RequestLog.objects.all())
        on_task_postrun(task_id=task.task_id, kwargs={"service_id": service.pk}, args=[{"detail": "success"}])
        mock_update_service_status.assert_called_once()
        mock_update_service_status.assert_called_with(
            {"kwargs": {"service_id": service.pk},
             "args": [{"detail": "success"}]},
            False)
        self.assertEqual(mock_get_task_result_status.call_count, 0)
        self.assertEqual(len(RequestLog.objects.all()), previous_len)
        mock_update_service_status.reset_mock()
        mock_get_task_result_status.reset_mock()

        on_task_postrun(
            task_id=task.task_id,
            kwargs={"service_id": service.pk},
            args=[{"detail": "success"}, service.service_route])
        mock_update_service_status.assert_called_once()
        mock_update_service_status.assert_called_with(
            {"kwargs": {"service_id": service.pk},
             "args": [{"detail": "success"}, service.service_route]},
            False)
        mock_get_task_result_status.assert_called_once()
        self.assertEqual(len(RequestLog.objects.all()), previous_len)
        mock_update_service_status.reset_mock()
        mock_get_task_result_status.reset_mock()

        task = TaskResult.objects.create(task_id=3)  # need to recreate here since previous test deleted the task
        mock_get_task_result_status.return_value = "Success"
        on_task_postrun(
            task_id=task.task_id,
            kwargs={"service_id": service.pk},
            args=[{"detail": "success"}, service.service_route])
        mock_update_service_status.assert_called_once()
        mock_update_service_status.assert_called_with(
            {"kwargs": {"service_id": service.pk},
             "args": [{"detail": "success"}, service.service_route]},
            False)
        mock_get_task_result_status.assert_called_once()
        self.assertEqual(len(RequestLog.objects.all()), previous_len + 1)
        mock_update_service_status.reset_mock()
        mock_get_task_result_status.reset_mock()

    def test_update_service_status(self):
        """Asserts the update_service_status signal correctly updates a service."""
        updated = update_service_status({"kwargs": {}}, True)
        self.assertEqual(updated, None)
        service = random.choice(ServiceRegistry.objects.all())
        updated = update_service_status({"kwargs": {"service_id": service.pk}}, True)
        self.assertTrue(isinstance(updated, ServiceRegistry))
        self.assertEqual(updated.has_active_task, True)

    def test_get_task_result_status(self):
        """Asserts the get_task_result_status signal returns expected values."""
        task_result = TaskResult.objects.create(status="FAILURE")
        self.assertEqual(get_task_result_status(task_result), "Error")

        task_result.status = "SUCCESS"
        task_result.result = "{}"
        self.assertEqual(get_task_result_status(task_result), "Idle")

        task_result.status = "SUCCESS"
        task_result.result = "{\"count\": 1}"
        self.assertEqual(get_task_result_status(task_result), "Success")

    @patch("gateway.tasks.queue_request.delay")
    def test_gateway_views(self, mock_queue):
        for service in ServiceRegistry.objects.filter(
                plugin=ServiceRegistry.REMOTE_AUTH, external_uri__isnull=False).exclude(application__name="Aurora"):
            url = "http://localhost/api/{}/".format(service.external_uri.rstrip("/"))
            resp = self.client.post(url)
            self.assertEqual(resp.status_code, 200, "{} returned an error: {}".format(service, resp.json()))
            self.assertEqual(mock_queue.call_args[0], ("post", render_service_path(service, "")))
            self.assertEqual(mock_queue.call_args[1]["data"], {})

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
        if not len(RequestLog.objects.all()):
            RequestLog.objects.create(
                service=random.choice(ServiceRegistry.objects.all())
            )
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
            "results-data returned error: {}".format(datatable_resp.json()))
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

    def test_delete_service(self):
        service = random.choice(ServiceRegistry.objects.all())
        initial_len = len(ServiceRegistry.objects.all())
        service.delete()
        self.assertEqual(
            len(ServiceRegistry.objects.all()), initial_len - 1,
            "More than one service was deleted.")

    def test_error_messages(self):
        """Tests the error_messages model method of RequestLog"""
        for task_id, result, expected in [
                (1, "{\"exc_message\": [\"foo\", {\"detail\": \"bar\"}]}", ["foo", "bar"]),
                (2, "{\"exc_message\": [\"<Response [500]>\"]}", ["Response [500]: Internal Server Error"])]:
            task_result = TaskResult.objects.create(task_id=task_id, result=result)
            service = random.choice(ServiceRegistry.objects.all())
            request_log = RequestLog.objects.create(service=service, task_result=task_result)
            self.assertEqual(request_log.error_messages, expected)

    def tearDown(self):
        TaskResult.objects.all().delete()
