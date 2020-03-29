from django.core.management import call_command
from django.test import Client, TestCase
from django.urls import reverse
from django_celery_beat.models import PeriodicTask

from .management.commands import setup_services as service_configs
from .models import Application, ServiceRegistry, Source, User

APPLICATIONS = [
    {'name': 'Ursa Major', 'host': 'ursa-major-web', 'port': 8005},
    {'name': 'Fornax', 'host': 'fornax-web', 'port': 8003},
]

SERVICES = [
    {'name': 'Store Accessions', 'application': 'Ursa Major',
     'description': 'Stores incoming accession data and creates associated transfer objects.',
     'external_uri': 'store-accessions', 'service_route': 'accessions',
     'plugin': 0, 'method': 'POST', 'callback_service': 'Ursa Major.Discover Bags', },
    {'name': 'Discover Bags', 'application': 'Ursa Major',
     'description': 'Checks for transfer files and, if found, moves them to storage.',
     'external_uri': 'discover-bags/', 'service_route': 'bagdiscovery/',
     'plugin': 0, 'method': 'POST', 'callback_service': None, },
    {'name': 'Approve Transfer', 'application': 'Fornax',
     'description': 'Approves transfer in Archivematica',
     'external_uri': 'approve-transfer/', 'service_route': 'approve/',
     'plugin': 0, 'method': 'POST', 'callback_service': 'Fornax.Request Bag Cleanup', },
    {'name': 'Request Bag Cleanup', 'application': 'Fornax',
     'description': 'Requests deletion of processed bags from source directory.',
     'external_uri': 'request-bag-cleanup/', 'service_route': 'request-cleanup/',
     'plugin': 0, 'method': 'POST', 'callback_service': None, },
]


class GatewayTestCase(TestCase):

    def setUp(self):
        self.client = Client()

    def create_applications(self):
        print("Creating applications")
        for application in APPLICATIONS:
            Application.objects.create(
                name=application['name'],
                is_active=True,
                app_host=application['host'],
                app_port=application['port'],
            )
        self.assertEqual(len(Application.objects.all()), len(APPLICATIONS))

    def create_services(self):
        print("Creating services")
        for service in SERVICES:
            ServiceRegistry.objects.create(
                name=service['name'],
                application=Application.objects.get(name=service['application']),
                description=service['description'],
                external_uri=service['external_uri'],
                service_route=service['service_route'],
                plugin=service['plugin'],
                is_active=True,
                is_private=False,
                method=service['method'],
            )
        for service in SERVICES:
            object = ServiceRegistry.objects.get(name=service['name'])
            object.callback_service = ServiceRegistry.objects.get(application__name=service['callback_service'].split('.')[0], name=service['callback_service'].split('.')[1]) if service['callback_service'] else None
            object.save()
        self.assertEqual(len(ServiceRegistry.objects.all()), len(SERVICES))

    def queue_tasks(self):
        print("Queueing tasks")
        for service in ServiceRegistry.objects.all():
            trigger = self.client.get(reverse('services-trigger', kwargs={'pk': service.id}))
            self.assertEqual(trigger.status_code, 200, "Wrong HTTP response code")

    def test_gateway(self):
        self.create_applications()
        self.create_services()
        self.queue_tasks()

    def test_setup_services(self):
        call_command("setup_services", "--reset")
        self.assertEqual(len(service_configs.SUPERUSERS), len(User.objects.filter(is_superuser=True)))
        self.assertEqual(len(service_configs.USERS), len(User.objects.filter(is_superuser=False)))
        self.assertEqual(len(service_configs.SOURCES), len(Source.objects.all()))
        self.assertEqual(len(service_configs.APPLICATIONS), len(Application.objects.all()))
        self.assertEqual(len(service_configs.SERVICES), len(ServiceRegistry.objects.all()))
        self.assertEqual(len(service_configs.TASKS), len(PeriodicTask.objects.all()))
