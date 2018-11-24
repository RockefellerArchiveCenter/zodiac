from django.test import TestCase

from .models import Application, ServiceRegistry

APPLICATIONS = [
    {'name': 'Ursa Major', 'host': 'ursa-major-web', 'port': 8005},
    {'name': 'Fornax', 'host': 'fornax-web', 'port': 8003},
]

SERVICES = [
    {'name': 'Store Accessions', 'application': 'Ursa Major',
     'description': 'Stores incoming accession data and creates associated transfer objects.',
     'external_uri': 'store-accessions', 'service_route': 'accessions',
     'plugin': 0, 'method': 'POST', 'callback_service': 'Ursa Major.Discover Bags', 'post_service': None,},
    {'name': 'Discover Bags', 'application': 'Ursa Major',
     'description': 'Checks for transfer files and, if found, moves them to storage.',
     'external_uri': 'discover-bags/', 'service_route': 'bagdiscovery/',
     'plugin': 0, 'method': 'POST', 'callback_service': None, 'post_service': 'Fornax.Approve Transfer',},
    {'name': 'Approve Transfer', 'application': 'Fornax',
     'description': 'Approves transfer in Archivematica',
     'external_uri': 'approve-transfer/', 'service_route': 'approve/',
     'plugin': 0, 'method': 'POST', 'callback_service': 'Fornax.Request Bag Cleanup', 'post_service': 'Ursa Major.Discover Bags',},
    {'name': 'Request Bag Cleanup', 'application': 'Fornax',
     'description': 'Requests deletion of processed bags from source directory.',
     'external_uri': 'request-bag-cleanup/', 'service_route': 'request-cleanup/',
     'plugin': 0, 'method': 'POST', 'callback_service': None, 'post_service': None,},
]


class GatewayTestCase(TestCase):

    def create_applications(self):
        for application in APPLICATIONS:
            Application.objects.create(
                name=application['name'],
                is_active=True,
                app_host=application['host'],
                app_port=application['port'],
            )
            print("Created application: {}".format(application['name']))
        self.assertEqual(len(Application.objects.all()), len(APPLICATIONS))

    def create_services(self):
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
            print("Created service: {}".format(service['name']))
        self.assertEqual(len(ServiceRegistry.objects.all()), len(SERVICES))

    def test_gateway(self):
        self.create_applications()
        self.create_services()
