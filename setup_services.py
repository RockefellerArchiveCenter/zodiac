from django.contrib.auth.models import User;
from gateway.models import Application, ServiceRegistry

APPLICATIONS = [
    {'name': 'Ursa Major', 'host': 'ursa-major-web', 'port': 8005},
    {'name': 'Fornax', 'host': 'fornax-web', 'port': 8003},
    {'name': 'Gemini', 'host': 'gemini-web', 'port': 8006},
    {'name': 'Aquarius', 'host': 'aquarius-web', 'port': 8002},
    {'name': 'Archivematica', 'host': 'archivematica', 'port': 8001},
    {'name': 'ArchivesSpace', 'host': 'archivesspace', 'port': 8089},
    {'name': 'Fedora', 'host': 'fedora', 'port': 8080},
]

SERVICES = [
    {'name': 'Store Accessions', 'application': 'Ursa Major',
     'description': 'Stores incoming accession data and creates associated transfer objects.',
     'external_uri': 'store-accessions/', 'service_route': 'accessions/',
     'plugin': 0, 'method': 'POST', 'callback_service': 'Discover Bags', 'post_service': None},
    {'name': 'Discover Bags', 'application': 'Ursa Major',
     'description': 'Checks for transfer files and, if found, moves them to storage.',
     'external_uri': 'discover-bags/', 'service_route': 'bagdiscovery/',
     'plugin': 0, 'method': 'POST', 'callback_service': None, 'post_service': 'Store SIPs'},
    {'name': 'Store SIPs', 'application': 'Fornax',
     'description': 'Stores incoming SIP objects.',
     'external_uri': 'store-sips/', 'service_route': 'sips/',
     'plugin': 0, 'method': 'POST', 'callback_service': 'Assemble SIP', 'post_service': None},
    {'name': 'Assemble SIP', 'application': 'Fornax',
     'description': 'Creates Archivematica-compliant SIPs',
     'external_uri': 'assemble-sips', 'service_route': 'sipassembly/',
     'plugin': 0, 'method': 'POST', 'callback_service': None, 'post_service': 'Start Transfer'},
    {'name': 'Start Transfer', 'application': 'Fornax',
     'description': 'Starts transfer in Archivematica',
     'external_uri': 'start-transfer', 'service_route': 'starttransfer/',
     'plugin': 0, 'method': 'POST', 'callback_service': None, 'post_service': 'Approve Transfer'},
    {'name': 'Approve Transfer', 'application': 'Fornax',
     'description': 'Approves transfer in Archivematica',
     'external_uri': 'approve-transfer/', 'service_route': 'approvetransfer/',
     'plugin': 0, 'method': 'POST', 'callback_service': None, 'post_service': None},
    {'name': 'Store Transfer', 'application': 'Archivematica',
     'description': 'Placeholder to trigger download of stored transfers',
     'external_uri': 'store-transfer/', 'service_route': 'storetransfer/',
     'plugin': 0, 'method': 'POST', 'callback_service': 'Download Packages', 'post_service': None},
    {'name': 'Download Packages', 'application': 'Gemini',
     'description': 'Downloads packages from Archivematica',
     'external_uri': 'download-packages/', 'service_route': 'download/',
     'plugin': 0, 'method': 'POST', 'callback_service': 'Store Package', 'post_service': None},
    {'name': 'Store Package', 'application': 'Gemini',
     'description': 'Stores packages in Fedora',
     'external_uri': 'store-packages', 'service_route': 'store/',
     'plugin': 0, 'method': 'POST', 'callback_service': None, 'post_service': 'Store Data'},
    {'name': 'Store Data', 'application': 'Aquarius',
     'description': 'Stores incoming transfer objects',
     'external_uri': 'store-data/', 'service_route': 'transfers/',
     'plugin': 0, 'method': 'POST', 'callback_service': 'Process Data', 'post_service': None},
    {'name': 'Process Data', 'application': 'Aquarius',
     'description': 'Transforms and delivers accession and transfer data to ArchivesSpace',
     'external_uri': 'process-data/', 'service_route': 'process/',
     'plugin': 0, 'method': 'POST', 'callback_service': None, 'post_service': None},
]

# create superuser?
if len(User.objects.all()) == 0:
    User.objects.create_superuser('admin', 'admin@example.com', 'adminpass')

# Create applications
if len(Application.objects.all()) == 0:
    for application in APPLICATIONS:
        Application.objects.create(
            name=application['name'],
            is_active=True,
            app_host=application['host'],
            app_port=application['port'],
        )
        print("Created application: {}".format(application['name']))

# Create services
if len(ServiceRegistry.objects.all()) == 0:
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

    # Add callbacks
    for service in SERVICES:
        object = ServiceRegistry.objects.get(name=service['name'])
        object.callback_service = ServiceRegistry.objects.get(name=service['callback_service']) if service['callback_service'] else None
        object.post_service = ServiceRegistry.objects.get(name=service['post_service']) if service['post_service'] else None
        object.save()
    print("Callbacks and POST services linked")
