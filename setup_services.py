from django_celery_beat.models import CrontabSchedule, PeriodicTask
from gateway.models import Application, ServiceRegistry, Source, User

SUPERUSERS = [
    {"username": "admin", "email": "admin@example.com", "password": "adminpass"}
]

USERS = [
    {"username": "aurora", "email": "aurora@example.com", "password": "aurorapass"}
]

SOURCES = [
    {"username": "aurora", "apikey": "demo"},
]

APPLICATIONS = [
    # {'name': 'Ursa Major', 'host': 'ursa-major-web',
    #     'port': 8005, 'health_check_path': '/status'},
    # {'name': 'Fornax', 'host': 'fornax-web',
    #     'port': 8003, 'health_check_path': '/status'},
    # {'name': 'Gemini', 'host': 'gemini-web',
    #     'port': 8006, 'health_check_path': '/status'},
    # {'name': 'Aquarius', 'host': 'aquarius-web',
    #     'port': 8002, 'health_check_path': '/status'},
    # {'name': 'Aurora', 'host': 'localhost',
    #     'port': 8000, 'health_check_path': None},
    {'name': 'Pisces', 'host': 'pisces-web',
        'port': 8007, 'health_check_path': '/status'},
    {'name': 'Scorpio', 'host': 'scorpio-web',
        'port': 8008, 'health_check_path': '/status'}
]

SERVICES = [
    # {'name': 'Update Transfers', 'application': 'Aurora',
    #  'description': 'Updates transfers and removes files from destination directory.',
    #  'external_uri': 'api/transfers/', 'service_route': 'api/transfers/',
    #  'plugin': 0, 'method': 'POST', 'callback_service': None, 'post_service': None,
    #  'sources': None},
    # {'name': 'Update Accessions', 'application': 'Aurora',
    #  'description': 'Updates accession data.',
    #  'external_uri': 'api/accessions/', 'service_route': 'api/acccessions/',
    #  'plugin': 0, 'method': 'POST', 'callback_service': None, 'post_service': None,
    #  'sources': None},
    # {'name': 'Store Accessions', 'application': 'Ursa Major',
    #  'description': 'Stores incoming accession data and creates associated transfer objects.',
    #  'external_uri': 'store-accessions', 'service_route': 'accessions',
    #  'plugin': 2, 'method': 'POST', 'callback_service': 'Ursa Major.Discover Bags',
    #  'post_service': None, 'sources': ['aurora']},
    # {'name': 'Store Bags', 'application': 'Ursa Major',
    #  'description': 'Stores incoming bag data.',
    #  'external_uri': 'store-bags', 'service_route': 'bags',
    #  'plugin': 2, 'method': 'POST', 'callback_service': 'Ursa Major.Discover Bags',
    #  'post_service': None, 'sources': ['aurora']},
    # {'name': 'Discover Bags', 'application': 'Ursa Major',
    #  'description': 'Checks for transfer files and, if found, moves them to storage.',
    #  'external_uri': 'discover-bags/', 'service_route': 'bagdiscovery/',
    #  'plugin': 0, 'method': 'POST', 'callback_service': None, 'post_service': 'Fornax.Store SIPs',
    #  'sources': None},
    # {'name': 'Cleanup Bags', 'application': 'Ursa Major',
    #  'description': 'Removes transfers from destination directory.',
    #  'external_uri': 'cleanup-bags/', 'service_route': 'cleanup/',
    #  'plugin': 0, 'method': 'POST', 'callback_service': None, 'post_service': None,
    #  'sources': None},
    # {'name': 'Store SIPs', 'application': 'Fornax',
    #  'description': 'Stores incoming SIP objects.',
    #  'external_uri': 'store-sips/', 'service_route': 'sips/',
    #  'plugin': 0, 'method': 'POST', 'callback_service': 'Fornax.Assemble SIP',
    #  'post_service': None, 'sources': None},
    # {'name': 'Assemble SIP', 'application': 'Fornax',
    #  'description': 'Creates Archivematica-compliant SIPs',
    #  'external_uri': 'assemble-sips', 'service_route': 'assemble/',
    #  'plugin': 0, 'method': 'POST', 'callback_service': 'Fornax.Create Transfer',
    #  'post_service': None, 'sources': None},
    # {'name': 'Create Transfer', 'application': 'Fornax',
    #  'description': 'Starts and approves a transfer in Archivematica',
    #  'external_uri': 'create-transfer', 'service_route': 'start/',
    #  'plugin': 0, 'method': 'POST', 'callback_service': 'Fornax.Request Bag Cleanup',
    #  'post_service': None, 'sources': None},
    # {'name': 'Request Bag Cleanup', 'application': 'Fornax',
    #  'description': 'Requests deletion of processed bags from source directory.',
    #  'external_uri': 'request-bag-cleanup/', 'service_route': 'request-cleanup/',
    #  'plugin': 0, 'method': 'POST', 'callback_service': 'Fornax.Remove Completed Ingests',
    #  'post_service': 'Ursa Major.Cleanup Bags', 'sources': None},
    # {'name': 'Remove Completed Ingests', 'application': 'Fornax',
    #  'description': 'Removes completed ingests from Archivematica dashboard.',
    #  'external_uri': 'remove-completed-ingests/', 'service_route': 'remove-ingests/',
    #  'plugin': 0, 'method': 'POST', 'callback_service': 'Fornax.Remove Completed Transfers',
    #  'post_service': None, 'sources': None},
    # {'name': 'Remove Completed Transfers', 'application': 'Fornax',
    #  'description': 'Removes completed transfers from Archivematica dashboard.',
    #  'external_uri': 'remove-completed-transfers/', 'service_route': 'remove-transfers/',
    #  'plugin': 0, 'method': 'POST', 'callback_service': 'Gemini.Download Packages',
    #  'post_service': None, 'sources': None},
    # {'name': 'Cleanup SIPs', 'application': 'Fornax',
    #  'description': 'Removes SIPs from destination directory.',
    #  'external_uri': 'cleanup-sips/', 'service_route': 'cleanup/',
    #  'plugin': 0, 'method': 'POST', 'callback_service': None, 'post_service': None,
    #  'sources': None},
    # {'name': 'Download Packages', 'application': 'Gemini',
    #  'description': 'Downloads packages from Archivematica',
    #  'external_uri': 'download-packages/', 'service_route': 'download/',
    #  'plugin': 0, 'method': 'POST', 'callback_service': 'Gemini.Store Package',
    #  'post_service': None, 'sources': None},
    # {'name': 'Store Package', 'application': 'Gemini',
    #  'description': 'Stores packages in Fedora',
    #  'external_uri': 'store-packages', 'service_route': 'store/',
    #  'plugin': 0, 'method': 'POST', 'callback_service': 'Gemini.Request SIP Cleanup',
    #  'post_service': 'Aquarius.Store Package Data', 'sources': None, },
    # {'name': 'Request SIP Cleanup', 'application': 'Gemini',
    #  'description': 'Requests deletion of processed SIPs from source directory.',
    #  'external_uri': 'request-sip-cleanup/', 'service_route': 'request-cleanup/',
    #  'plugin': 0, 'method': 'POST', 'callback_service': None, 'post_service': 'Fornax.Cleanup SIPs',
    #  'sources': None},
    # {'name': 'Store Package Data', 'application': 'Aquarius',
    #  'description': 'Stores incoming transfer objects',
    #  'external_uri': 'store-data/', 'service_route': 'packages/',
    #  'plugin': 0, 'method': 'POST', 'callback_service': 'Aquarius.Process Accessions',
    #  'post_service': None, 'sources': None},
    # {'name': 'Process Accessions', 'application': 'Aquarius',
    #  'description': 'Transforms and delivers accession data to ArchivesSpace',
    #  'external_uri': 'process-accessions/', 'service_route': 'accessions/',
    #  'plugin': 0, 'method': 'POST', 'callback_service': 'Aquarius.Update Accession Status',
    #  'post_service': None, 'sources': None},
    # {'name': 'Update Accession Status', 'application': 'Aquarius',
    #  'description': 'Sends information about updated accessions',
    #  'external_uri': 'update-accessions/', 'service_route': 'send-accession-update/',
    #  'plugin': 0, 'method': 'POST', 'callback_service': 'Aquarius.Process Grouping Components',
    #  'post_service': 'Aurora.Update Accessions', 'sources': None},
    # {'name': 'Process Grouping Components', 'application': 'Aquarius',
    #  'description': 'Transforms and delivers grouping component data to ArchivesSpace',
    #  'external_uri': 'process-grouping-components/', 'service_route': 'grouping-components/',
    #  'plugin': 0, 'method': 'POST', 'callback_service': 'Aquarius.Process Transfer Components',
    #  'post_service': None, 'sources': None},
    # {'name': 'Process Transfer Components', 'application': 'Aquarius',
    #  'description': 'Transforms and delivers transfer data to ArchivesSpace',
    #  'external_uri': 'process-transfer-components/', 'service_route': 'transfer-components/',
    #  'plugin': 0, 'method': 'POST', 'callback_service': 'Aquarius.Process Digital Objects',
    #  'post_service': None, 'sources': None},
    # {'name': 'Process Digital Objects', 'application': 'Aquarius',
    #  'description': 'Transforms and delivers digital object data to ArchivesSpace',
    #  'external_uri': 'process-digital-objects/', 'service_route': 'digital-objects/',
    #  'plugin': 0, 'method': 'POST', 'callback_service': 'Aquarius.Update Transfer Status',
    #  'post_service': None, 'sources': None},
    # {'name': 'Update Transfer Status', 'application': 'Aquarius',
    #  'description': 'Sends information about updated transfers.',
    #  'external_uri': 'update-transfers/', 'service_route': 'send-update/',
    #  'plugin': 0, 'method': 'POST', 'callback_service': None, 'post_service':
    #  'Aurora.Update Transfers', 'sources': None},
    {'name': 'Fetch ArchivesSpace Resource Updates', 'application': 'Pisces',
     'description': 'Fetches updated resource data from ArchivesSpace.',
     'external_uri': 'fetch-archivesspace-resource-updates/',
     'service_route': 'fetch/archivesspace/updates/?object_type=resource', 'plugin': 0,
     'method': 'POST', 'callback_service': None, 'post_service': None,
     'sources': None},
    {'name': 'Fetch ArchivesSpace Archival Object Updates', 'application': 'Pisces',
     'description': 'Fetches updated archival object data from ArchivesSpace.',
     'external_uri': 'fetch-archivesspace-archival-object-updates/',
     'service_route': 'fetch/archivesspace/updates/?object_type=archival_object', 'plugin': 0,
     'method': 'POST', 'callback_service': None, 'post_service': None,
     'sources': None},
    {'name': 'Fetch ArchivesSpace Subject Updates', 'application': 'Pisces',
     'description': 'Fetches updated subject data from ArchivesSpace.',
     'external_uri': 'fetch-archivesspace-subject-updates/',
     'service_route': 'fetch/archivesspace/updates/?object_type=subject', 'plugin': 0,
     'method': 'POST', 'callback_service': None, 'post_service': None,
     'sources': None},
    {'name': 'Fetch ArchivesSpace Person Updates', 'application': 'Pisces',
     'description': 'Fetches updated person data from ArchivesSpace.',
     'external_uri': 'fetch-archivesspace-person-updates/',
     'service_route': 'fetch/archivesspace/updates/?object_type=person', 'plugin': 0,
     'method': 'POST', 'callback_service': None, 'post_service': None,
     'sources': None},
    {'name': 'Fetch ArchivesSpace Organization Updates', 'application': 'Pisces',
     'description': 'Fetches updated organization data from ArchivesSpace.',
     'external_uri': 'fetch-archivesspace-organization-updates/',
     'service_route': 'fetch/archivesspace/updates/?object_type=organization', 'plugin': 0,
     'method': 'POST', 'callback_service': None, 'post_service': None,
     'sources': None},
    {'name': 'Fetch ArchivesSpace Family Updates', 'application': 'Pisces',
     'description': 'Fetches updated family data from ArchivesSpace.',
     'external_uri': 'fetch-archivesspace-family-updates/',
     'service_route': 'fetch/archivesspace/updates/?object_type=family', 'plugin': 0,
     'method': 'POST', 'callback_service': None, 'post_service': None,
     'sources': None},
    {'name': 'Fetch ArchivesSpace Resource Deletes', 'application': 'Pisces',
     'description': 'Fetches deleted resource data from ArchivesSpace.',
     'external_uri': 'fetch-archivesspace-resource-deletes/',
     'service_route': 'fetch/archivesspace/deletes/?object_type=resource', 'plugin': 0,
     'method': 'POST', 'callback_service': None, 'post_service': None,
     'sources': None},
    {'name': 'Fetch ArchivesSpace Archival Object Deletes', 'application': 'Pisces',
     'description': 'Fetches deleted archival object data from ArchivesSpace.',
     'external_uri': 'fetch-archivesspace-archival-object-deletes/',
     'service_route': 'fetch/archivesspace/deletes/?object_type=archival_object', 'plugin': 0,
     'method': 'POST', 'callback_service': None, 'post_service': None,
     'sources': None},
    {'name': 'Fetch ArchivesSpace Subject Deletes', 'application': 'Pisces',
     'description': 'Fetches deleted subject data from ArchivesSpace.',
     'external_uri': 'fetch-archivesspace-subject-deletes/',
     'service_route': 'fetch/archivesspace/deletes/?object_type=subject', 'plugin': 0,
     'method': 'POST', 'callback_service': None, 'post_service': None,
     'sources': None},
    {'name': 'Fetch ArchivesSpace Person Deletes', 'application': 'Pisces',
     'description': 'Fetches deleted person data from ArchivesSpace.',
     'external_uri': 'fetch-archivesspace-person-deletes/',
     'service_route': 'fetch/archivesspace/deletes/?object_type=person', 'plugin': 0,
     'method': 'POST', 'callback_service': None, 'post_service': None,
     'sources': None},
    {'name': 'Fetch ArchivesSpace Organization Deletes', 'application': 'Pisces',
     'description': 'Fetches deleted organization data from ArchivesSpace.',
     'external_uri': 'fetch-archivesspace-organization-deletes/',
     'service_route': 'fetch/archivesspace/deletes/?object_type=organization', 'plugin': 0,
     'method': 'POST', 'callback_service': None, 'post_service': None,
     'sources': None},
    {'name': 'Fetch ArchivesSpace Family Deletes', 'application': 'Pisces',
     'description': 'Fetches deleted family data from ArchivesSpace.',
     'external_uri': 'fetch-archivesspace-family-deletes/',
     'service_route': 'fetch/archivesspace/deletes/?object_type=family', 'plugin': 0,
     'method': 'POST', 'callback_service': None, 'post_service': None,
     'sources': None},
]

# TASKS = [
#     {"name": "Process queued callbacks", "task": "gateway.tasks.queue_callbacks"},
#     {"name": "Delete successful results", "task": "gateway.tasks.delete_successful"}
# ]

# Create users
for superuser in SUPERUSERS:
    if not User.objects.filter(username=superuser["username"]).exists():
        User.objects.create_superuser(
            superuser["username"],
            superuser["email"],
            superuser["password"]
        )

for user in USERS:
    if not User.objects.filter(username=user["username"]).exists():
        User.objects.create_user(
            user["username"],
            user["email"],
            user["password"]
        )

print("Created users")

# Create sources
for source in SOURCES:
    if not Source.objects.filter(apikey=source['apikey']).exists():
        Source.objects.create(
            user=User.objects.get(username=source['username']),
            apikey=source['apikey']
        )
print("Created sources")

# Create applications
for application in APPLICATIONS:
    if not Application.objects.filter(name=application["name"],
                                      app_host=application['host'],
                                      app_port=application['port']).exists():
        Application.objects.create(
            name=application['name'],
            is_active=True,
            app_host=application['host'],
            app_port=application['port'],
            health_check_path=application['health_check_path'],
        )
        print("Created application: {}".format(application['name']))

# Create services
for service in SERVICES:
    if not ServiceRegistry.objects.filter(
            name=service['name'], external_uri=service['external_uri'],
            service_route=service['service_route']).exists():
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
                new_service.sources.add(
                    Source.objects.get(
                        user__username=source))
        print("Created service: {}".format(service['name']))

# Add callbacks and post services
for service in SERVICES:
    object = ServiceRegistry.objects.get(name=service['name'])
    object.callback_service = ServiceRegistry.objects.get(
        application__name=service['callback_service'].split('.')[0],
        name=service['callback_service'].split('.')[1]) if service['callback_service'] else None
    object.post_service = ServiceRegistry.objects.get(
        application__name=service['post_service'].split('.')[0],
        name=service['post_service'].split('.')[1]) if service['post_service'] else None
    object.save()
print("Callbacks and POST Services linked")

# every_minute, _ = CrontabSchedule.objects.get_or_create(minute='*', hour='*',
#                                                         day_of_week='*', day_of_month='*',
#                                                         month_of_year='*')
# daily, _ = CrontabSchedule.objects.get_or_create(minute='0', hour='4',
#                                                  day_of_week='*', day_of_month='*',
#                                                  month_of_year='*')
# for task in TASKS:
#     if not PeriodicTask.objects.filter(
#             name=task["name"], task=task["task"]).exists():
#         PeriodicTask.objects.create(crontab=every_minute, name=task["name"],
#                                     task=task["task"])
#
# print("Tasks scheduled")
