from django.contrib.auth.models import User;
from gateway.models import Application, ServiceRegistry

APPLICATIONS = [
    {'name': 'Ursa Major', 'host': 'ursa-major-web', 'port': 8005},
    {'name': 'Fornax', 'host': 'fornax-web', 'port': 8003},
    {'name': 'Gemini', 'host': 'gemini-web', 'port': 8006},
    {'name': 'Aquarius', 'host': 'aquarius-web', 'port': 8002},
    {'name': 'Aurora', 'host': 'localhost', 'port': 8000},
]

SERVICES = [
    {'name': 'Update Transfers', 'application': 'Aurora',
     'description': 'Updates transfers and removes files from destination directory.',
     'external_uri': 'api/transfers/', 'service_route': 'api/transfers/',
     'plugin': 0, 'method': 'POST', 'callback_service': None, 'post_service': None,},
    {'name': 'Store Accessions', 'application': 'Ursa Major',
     'description': 'Stores incoming accession data and creates associated transfer objects.',
     'external_uri': 'store-accessions', 'service_route': 'accessions',
     'plugin': 0, 'method': 'POST', 'callback_service': 'Ursa Major.Discover Bags', 'post_service': None,},
    {'name': 'Discover Bags', 'application': 'Ursa Major',
     'description': 'Checks for transfer files and, if found, moves them to storage.',
     'external_uri': 'discover-bags/', 'service_route': 'bagdiscovery/',
     'plugin': 0, 'method': 'POST', 'callback_service': None, 'post_service': 'Fornax.Store SIPs',},
    {'name': 'Cleanup Bags', 'application': 'Ursa Major',
     'description': 'Removes transfers from destination directory.',
     'external_uri': 'cleanup-bags/', 'service_route': 'cleanup/',
     'plugin': 0, 'method': 'POST', 'callback_service': None, 'post_service': None,},
    {'name': 'Store SIPs', 'application': 'Fornax',
     'description': 'Stores incoming SIP objects.',
     'external_uri': 'store-sips/', 'service_route': 'sips/',
     'plugin': 0, 'method': 'POST', 'callback_service': 'Fornax.Assemble SIP', 'post_service': None,},
    {'name': 'Assemble SIP', 'application': 'Fornax',
     'description': 'Creates Archivematica-compliant SIPs',
     'external_uri': 'assemble-sips', 'service_route': 'assemble/',
     'plugin': 0, 'method': 'POST', 'callback_service': 'Fornax.Start Transfer', 'post_service': None,},
    {'name': 'Start Transfer', 'application': 'Fornax',
     'description': 'Starts transfer in Archivematica',
     'external_uri': 'start-transfer', 'service_route': 'start/',
     'plugin': 0, 'method': 'POST', 'callback_service': 'Fornax.Approve Transfer', 'post_service': None,},
    {'name': 'Approve Transfer', 'application': 'Fornax',
     'description': 'Approves transfer in Archivematica',
     'external_uri': 'approve-transfer/', 'service_route': 'approve/',
     'plugin': 0, 'method': 'POST', 'callback_service': 'Fornax.Request Bag Cleanup', 'post_service': None,},
    {'name': 'Request Bag Cleanup', 'application': 'Fornax',
     'description': 'Requests deletion of processed bags from source directory.',
     'external_uri': 'request-bag-cleanup/', 'service_route': 'request-cleanup/',
     'plugin': 0, 'method': 'POST', 'callback_service': 'Gemini.Download Packages', 'post_service': 'Ursa Major.Cleanup Bags',},
    {'name': 'Cleanup SIPs', 'application': 'Fornax',
     'description': 'Removes SIPs from destination directory.',
     'external_uri': 'cleanup-sips/', 'service_route': 'cleanup/',
     'plugin': 0, 'method': 'POST', 'callback_service': None, 'post_service': None,},
    {'name': 'Download Packages', 'application': 'Gemini',
     'description': 'Downloads packages from Archivematica',
     'external_uri': 'download-packages/', 'service_route': 'download/',
     'plugin': 0, 'method': 'POST', 'callback_service': 'Gemini.Store Package', 'post_service': None,},
    {'name': 'Store Package', 'application': 'Gemini',
     'description': 'Stores packages in Fedora',
     'external_uri': 'store-packages', 'service_route': 'store/',
     'plugin': 0, 'method': 'POST', 'callback_service': None, 'post_service': 'Gemini.Request SIP Cleanup',},
    {'name': 'Request SIP Cleanup', 'application': 'Gemini',
     'description': 'Requests deletion of processed SIPs from source directory.',
     'external_uri': 'request-sip-cleanup/', 'service_route': 'request-cleanup/',
     'plugin': 0, 'method': 'POST', 'callback_service': 'Aquarius.Store Package Data', 'post_service': 'Fornax.Cleanup SIPs',},
    {'name': 'Store Package Data', 'application': 'Aquarius',
     'description': 'Stores incoming transfer objects',
     'external_uri': 'store-data/', 'service_route': 'packages/',
     'plugin': 0, 'method': 'POST', 'callback_service': 'Aquarius.Process Accessions', 'post_service': None,},
    {'name': 'Process Accessions', 'application': 'Aquarius',
     'description': 'Transforms and delivers accession data to ArchivesSpace',
     'external_uri': 'process-accessions/', 'service_route': 'accessions/',
     'plugin': 0, 'method': 'POST', 'callback_service': 'Aquarius.Process Grouping Components', 'post_service': None,},
    {'name': 'Process Grouping Components', 'application': 'Aquarius',
     'description': 'Transforms and delivers grouping component data to ArchivesSpace',
     'external_uri': 'process-grouping-components/', 'service_route': 'grouping-components/',
     'plugin': 0, 'method': 'POST', 'callback_service': 'Aquarius.Process Transfer Components', 'post_service': None,},
    {'name': 'Process Transfer Components', 'application': 'Aquarius',
     'description': 'Transforms and delivers transfer data to ArchivesSpace',
     'external_uri': 'process-transfer-components/', 'service_route': 'transfer-components/',
     'plugin': 0, 'method': 'POST', 'callback_service': 'Aquarius.Process Digital Objects', 'post_service': None,},
    {'name': 'Process Digital Objects', 'application': 'Aquarius',
     'description': 'Transforms and delivers digital object data to ArchivesSpace',
     'external_uri': 'process-digital-objects/', 'service_route': 'digital-objects/',
     'plugin': 0, 'method': 'POST', 'callback_service': 'Aquarius.Update Transfer Status', 'post_service': None,},
    {'name': 'Update Transfer Status', 'application': 'Aquarius',
     'description': 'Sends information about updated transfers.',
     'external_uri': 'update-transfers/', 'service_route': 'send-update/',
     'plugin': 0, 'method': 'POST', 'callback_service': None, 'post_service': 'Aurora.Update Transfers',},
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

    # Add callbacks and post services
    for service in SERVICES:
        object = ServiceRegistry.objects.get(name=service['name'])
        object.callback_service = ServiceRegistry.objects.get(application__name=service['callback_service'].split('.')[0], name=service['callback_service'].split('.')[1]) if service['callback_service'] else None
        object.post_service = ServiceRegistry.objects.get(application__name=service['post_service'].split('.')[0], name=service['post_service'].split('.')[1]) if service['post_service'] else None
        object.save()
    print("Callbacks and POST Services linked")
