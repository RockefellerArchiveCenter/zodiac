from django.contrib.auth.models import User
from django_celery_beat.models import CrontabSchedule, PeriodicTask
from gateway.models import Application, ServiceRegistry, Source

APPLICATIONS = [
    {'name': 'Ursa Major', 'host': 'ursa-major-web', 'port': 8005},
    {'name': 'Fornax', 'host': 'fornax-web', 'port': 8003},
    {'name': 'Gemini', 'host': 'gemini-web', 'port': 8006},
    {'name': 'Aquarius', 'host': 'aquarius-web', 'port': 8002},
    {'name': 'Aurora', 'host': 'localhost', 'port': 8000},
    {'name': 'Pisces', 'host': 'pisces-web', 'port': 8007},
]

SERVICES = [
    {'name': 'Update Transfers', 'application': 'Aurora',
     'description': 'Updates transfers and removes files from destination directory.',
     'external_uri': 'api/transfers/', 'service_route': 'api/transfers/',
     'plugin': 0, 'method': 'POST', 'callback_service': None, 'post_service': None,
     'sources': None,},
    {'name': 'Store Accessions', 'application': 'Ursa Major',
     'description': 'Stores incoming accession data and creates associated transfer objects.',
     'external_uri': 'store-accessions', 'service_route': 'accessions',
     'plugin': 2, 'method': 'POST', 'callback_service': 'Ursa Major.Discover Bags',
     'post_service': None, 'sources': ['aurora'],},
    {'name': 'Discover Bags', 'application': 'Ursa Major',
     'description': 'Checks for transfer files and, if found, moves them to storage.',
     'external_uri': 'discover-bags/', 'service_route': 'bagdiscovery/',
     'plugin': 0, 'method': 'POST', 'callback_service': None, 'post_service': 'Fornax.Store SIPs',
     'sources': None,},
    {'name': 'Cleanup Bags', 'application': 'Ursa Major',
     'description': 'Removes transfers from destination directory.',
     'external_uri': 'cleanup-bags/', 'service_route': 'cleanup/',
     'plugin': 0, 'method': 'POST', 'callback_service': None, 'post_service': None,
     'sources': None,},
    {'name': 'Store SIPs', 'application': 'Fornax',
     'description': 'Stores incoming SIP objects.',
     'external_uri': 'store-sips/', 'service_route': 'sips/',
     'plugin': 0, 'method': 'POST', 'callback_service': 'Fornax.Assemble SIP',
     'post_service': None, 'sources': None,},
    {'name': 'Assemble SIP', 'application': 'Fornax',
     'description': 'Creates Archivematica-compliant SIPs',
     'external_uri': 'assemble-sips', 'service_route': 'assemble/',
     'plugin': 0, 'method': 'POST', 'callback_service': 'Fornax.Start Transfer',
     'post_service': None, 'sources': None,},
    {'name': 'Start Transfer', 'application': 'Fornax',
     'description': 'Starts transfer in Archivematica',
     'external_uri': 'start-transfer', 'service_route': 'start/',
     'plugin': 0, 'method': 'POST', 'callback_service': 'Fornax.Approve Transfer',
     'post_service': None, 'sources': None,},
    {'name': 'Approve Transfer', 'application': 'Fornax',
     'description': 'Approves transfer in Archivematica',
     'external_uri': 'approve-transfer/', 'service_route': 'approve/',
     'plugin': 0, 'method': 'POST', 'callback_service': 'Fornax.Request Bag Cleanup',
     'post_service': None, 'sources': None,},
    {'name': 'Request Bag Cleanup', 'application': 'Fornax',
     'description': 'Requests deletion of processed bags from source directory.',
     'external_uri': 'request-bag-cleanup/', 'service_route': 'request-cleanup/',
     'plugin': 0, 'method': 'POST', 'callback_service': 'Fornax.Remove Completed Ingests',
     'post_service': 'Ursa Major.Cleanup Bags', 'sources': None,},
    {'name': 'Remove Completed Ingests', 'application': 'Fornax',
     'description': 'Removes completed ingests from Archivematica dashboard.',
     'external_uri': 'remove-completed-ingests/', 'service_route': 'remove-ingests/',
     'plugin': 0, 'method': 'POST', 'callback_service': 'Fornax.Remove Completed Transfers',
     'post_service': None, 'sources': None,},
    {'name': 'Remove Completed Transfers', 'application': 'Fornax',
     'description': 'Removes completed transfers from Archivematica dashboard.',
     'external_uri': 'remove-completed-transfers/', 'service_route': 'remove-transfers/',
     'plugin': 0, 'method': 'POST', 'callback_service': 'Gemini.Download Packages',
     'post_service': None, 'sources': None,},
    {'name': 'Cleanup SIPs', 'application': 'Fornax',
     'description': 'Removes SIPs from destination directory.',
     'external_uri': 'cleanup-sips/', 'service_route': 'cleanup/',
     'plugin': 0, 'method': 'POST', 'callback_service': None, 'post_service': None,
     'sources': None,},
    {'name': 'Download Packages', 'application': 'Gemini',
     'description': 'Downloads packages from Archivematica',
     'external_uri': 'download-packages/', 'service_route': 'download/',
     'plugin': 0, 'method': 'POST', 'callback_service': 'Gemini.Store Package',
     'post_service': None, 'sources': None,},
    {'name': 'Store Package', 'application': 'Gemini',
     'description': 'Stores packages in Fedora',
     'external_uri': 'store-packages', 'service_route': 'store/',
     'plugin': 0, 'method': 'POST', 'callback_service': 'Gemini.Request SIP Cleanup',
     'post_service': 'Aquarius.Store Package Data', 'sources': None,},
    {'name': 'Request SIP Cleanup', 'application': 'Gemini',
     'description': 'Requests deletion of processed SIPs from source directory.',
     'external_uri': 'request-sip-cleanup/', 'service_route': 'request-cleanup/',
     'plugin': 0, 'method': 'POST', 'callback_service': None, 'post_service': 'Fornax.Cleanup SIPs',
     'sources': None,},
    {'name': 'Store Package Data', 'application': 'Aquarius',
     'description': 'Stores incoming transfer objects',
     'external_uri': 'store-data/', 'service_route': 'packages/',
     'plugin': 0, 'method': 'POST', 'callback_service': 'Aquarius.Process Accessions',
     'post_service': None, 'sources': None,},
    {'name': 'Process Accessions', 'application': 'Aquarius',
     'description': 'Transforms and delivers accession data to ArchivesSpace',
     'external_uri': 'process-accessions/', 'service_route': 'accessions/',
     'plugin': 0, 'method': 'POST', 'callback_service': 'Aquarius.Process Grouping Components',
     'post_service': None, 'sources': None,},
    {'name': 'Process Grouping Components', 'application': 'Aquarius',
     'description': 'Transforms and delivers grouping component data to ArchivesSpace',
     'external_uri': 'process-grouping-components/', 'service_route': 'grouping-components/',
     'plugin': 0, 'method': 'POST', 'callback_service': 'Aquarius.Process Transfer Components',
     'post_service': None, 'sources': None,},
    {'name': 'Process Transfer Components', 'application': 'Aquarius',
     'description': 'Transforms and delivers transfer data to ArchivesSpace',
     'external_uri': 'process-transfer-components/', 'service_route': 'transfer-components/',
     'plugin': 0, 'method': 'POST', 'callback_service': 'Aquarius.Process Digital Objects',
     'post_service': None, 'sources': None,},
    {'name': 'Process Digital Objects', 'application': 'Aquarius',
     'description': 'Transforms and delivers digital object data to ArchivesSpace',
     'external_uri': 'process-digital-objects/', 'service_route': 'digital-objects/',
     'plugin': 0, 'method': 'POST', 'callback_service': 'Aquarius.Update Transfer Status',
     'post_service': None, 'sources': None,},
    {'name': 'Update Transfer Status', 'application': 'Aquarius',
     'description': 'Sends information about updated transfers.',
     'external_uri': 'update-transfers/', 'service_route': 'send-update/',
     'plugin': 0, 'method': 'POST', 'callback_service': None, 'post_service':
     'Aurora.Update Transfers', 'sources': None,},
    {'name': 'Fetch ArchivesSpace Changes', 'application': 'Pisces',
     'description': 'Fetches updated and deleted data from ArchivesSpace.',
     'external_uri': 'fetch-archivesspace-changes/', 'service_route': 'fetch/archivesspace/changes',
     'plugin': 0, 'method': 'POST', 'callback_service': None, 'post_service':
     None, 'sources': None,},
    {'name': 'Fetch ArchivesSpace URI', 'application': 'Pisces',
     'description': 'Fetches data from an ArchivesSpace URI.',
     'external_uri': 'fetch-archivesspace-uri/', 'service_route': 'fetch/archivesspace/uri',
     'plugin': 0, 'method': 'POST', 'callback_service': None, 'post_service':
     None, 'sources': None,},
    {'name': 'Transform ArchivesSpace Data', 'application': 'Pisces',
     'description': 'Transforms a single ArchivesSpace data object.',
     'external_uri': 'transform-archivesspace/', 'service_route': 'transform/archivesspace/',
     'plugin': 0, 'method': 'POST', 'callback_service': None, 'post_service':
     None, 'sources': None,},
    {'name': 'Add to Index', 'application': 'Pisces',
     'description': 'Adds data to index.',
     'external_uri': 'index-add/', 'service_route': 'index/add/',
     'plugin': 0, 'method': 'POST', 'callback_service': None, 'post_service':
     None, 'sources': None,},
    {'name': 'Delete from Index', 'application': 'Pisces',
     'description': 'Deletes data from index.',
     'external_uri': 'index-delete/', 'service_route': 'index/delete/',
     'plugin': 0, 'method': 'POST', 'callback_service': None, 'post_service':
     None, 'sources': None,},
]

# Create users
if len(User.objects.all()) == 0:
    User.objects.create_superuser('admin', 'admin@example.com', 'adminpass')
    User.objects.create_user('aurora', 'aurora@example.com', 'aurorapass')
    print("Created users")

# Create sources
if len(Source.objects.all()) == 0:
    Source.objects.create(
        user=User.objects.get(username="aurora"),
        apikey="demo"
    )
    print("Created sources")

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
        new_service = ServiceRegistry.objects.create(
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
        if service['sources']:
            for source in service['sources']:
                new_service.sources.add(Source.objects.get(user__username=source))
        print("Created service: {}".format(service['name']))

    # Add callbacks and post services
    for service in SERVICES:
        object = ServiceRegistry.objects.get(name=service['name'])
        object.callback_service = ServiceRegistry.objects.get(application__name=service['callback_service'].split('.')[0], name=service['callback_service'].split('.')[1]) if service['callback_service'] else None
        object.post_service = ServiceRegistry.objects.get(application__name=service['post_service'].split('.')[0], name=service['post_service'].split('.')[1]) if service['post_service'] else None
        object.save()
    print("Callbacks and POST Services linked")

if len(PeriodicTask.objects.all()) == 0:
    every_minute, _ = CrontabSchedule.objects.get_or_create(minute='*', hour='*',
                                                        day_of_week='*', day_of_month='*',
                                                        month_of_year='*')
    daily, _ = CrontabSchedule.objects.get_or_create(minute='0', hour='4',
                                                      day_of_week='*', day_of_month='*',
                                                      month_of_year='*')
    # PeriodicTask.objects.create(crontab=every_minute, name="Process queued callbacks",
    #                             task="gateway.tasks.queue_callbacks")
    PeriodicTask.objects.create(crontab=every_minute, name="Fetch ArchivesSpace changes",
                                task="gateway.tasks.fetch_archivesspace_changes")
    PeriodicTask.objects.create(crontab=daily, name="Delete successful results",
                                task="gateway.tasks.delete_successful")
    print("Tasks scheduled")
