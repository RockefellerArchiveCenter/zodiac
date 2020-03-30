from django.core.management.base import BaseCommand
from django_celery_beat.models import CrontabSchedule, PeriodicTask
from gateway.models import Application, ServiceRegistry, Source, User

SUPERUSERS = [
    {"username": "admin", "email": "admin@example.com", "password": "adminpass"}
]

USERS = [
    {"username": "aurora", "email": "aurora@example.com", "password": "aurorapass"},
    {"username": "zorya", "email": "zorya@example.com", "password": "zoryapass"}
]

SOURCES = [
    {"username": "aurora", "apikey": "aurorakey"},
    {"username": "zorya", "apikey": "zoryakey"},
]

APPLICATIONS = [
    {
        "name": "Ursa Major", "host": "ursa-major-web",
        "port": 8005, "health_check_path": "/status"
    },
    {
        "name": "Fornax", "host": "fornax-web",
        "port": 8003, "health_check_path": "/status"
    },
    {
        "name": "Gemini", "host": "gemini-web",
        "port": 8006, "health_check_path": "/status"
    },
    {
        "name": "Aquarius", "host": "aquarius-web",
        "port": 8002, "health_check_path": "/status"
    },
    {
        "name": "Aurora", "host": "localhost",
        "port": 8000, "health_check_path": "/status"
    },
]

SERVICES = [
    {
        "name": "Update Transfers",
        "application": "Aurora",
        "description": "Updates transfers and removes files from destination directory.",
        "external_uri": "api/transfers",
        "service_route": "api/transfers",
    },
    {
        "name": "Update Accessions",
        "application": "Aurora",
        "description": "Updates accession data.",
        "external_uri": "api/accessions",
        "service_route": "api/acccessions",
    },
    {
        "name": "Store Accessions",
        "application": "Ursa Major",
        "description": "Stores incoming accession data and creates associated transfer objects.",
        "external_uri": "store-accessions",
        "service_route": "accessions",
        "plugin": 2,
        "callback_service": "Ursa Major.Discover Bags",
        "sources": ["aurora"]
    },
    {
        "name": "Store Bags",
        "application": "Ursa Major",
        "description": "Stores incoming bag data.",
        "external_uri": "store-bags",
        "service_route": "bags",
        "plugin": 2,
        "callback_service": "Ursa Major.Discover Bags",
        "sources": ["zorya"]
    },
    {
        "name": "Discover Bags",
        "application": "Ursa Major",
        "description": "Checks for transfer files and, if found, moves them to storage.",
        "external_uri": "discover-bags",
        "service_route": "bagdiscovery",
        "callback_service": "Ursa Major.Deliver Bags"
    },
    {
        "name": "Deliver Bags",
        "application": "Ursa Major",
        "description": "Delivers discovered transfers to configured service.",
        "external_uri": "discover-bags",
        "service_route": "bagdiscovery",
    },
    {
        "name": "Cleanup Bags",
        "application": "Ursa Major",
        "description": "Removes transfers from destination directory.",
        "external_uri": "cleanup-bags",
        "service_route": "cleanup",
    },
    {
        "name": "Store SIPs",
        "application": "Fornax",
        "description": "Stores incoming SIP objects.",
        "external_uri": "store-sips",
        "service_route": "sips",
        "callback_service": "Fornax.Assemble SIP",
    },
    {
        "name": "Assemble SIP",
        "application": "Fornax",
        "description": "Creates Archivematica-compliant SIPs",
        "external_uri": "assemble-sips",
        "service_route": "assemble",
        "callback_service": "Fornax.Create Transfer",
    },
    {
        "name": "Create Transfer",
        "application": "Fornax",
        "description": "Starts and approves a transfer in Archivematica",
        "external_uri": "create-transfer",
        "service_route": "start",
        "callback_service": "Fornax.Request Bag Cleanup",
    },
    {
        "name": "Request Bag Cleanup",
        "application": "Fornax",
        "description": "Requests deletion of processed bags from source directory.",
        "external_uri": "request-bag-cleanup",
        "service_route": "request-cleanup",
        "callback_service": "Fornax.Remove Completed Ingests",
    },
    {
        "name": "Remove Completed Ingests",
        "application": "Fornax",
        "description": "Removes completed ingests from Archivematica dashboard.",
        "external_uri": "remove-completed-ingests",
        "service_route": "remove-ingests",
        "callback_service": "Fornax.Remove Completed Transfers",
    },
    {
        "name": "Remove Completed Transfers",
        "application": "Fornax",
        "description": "Removes completed transfers from Archivematica dashboard.",
        "external_uri": "remove-completed-transfers",
        "service_route": "remove-transfers",
        "callback_service": "Gemini.Download Packages",
    },
    {
        "name": "Cleanup SIPs",
        "application": "Fornax",
        "description": "Removes SIPs from destination directory.",
        "external_uri": "cleanup-sips",
        "service_route": "cleanup",
    },
    {
        "name": "Download Packages",
        "application": "Gemini",
        "description": "Downloads packages from Archivematica",
        "external_uri": "download-packages",
        "service_route": "download",
        "callback_service": "Gemini.Store Package",
    },
    {
        "name": "Store Package",
        "application": "Gemini",
        "description": "Stores packages in Fedora",
        "external_uri": "store-packages",
        "service_route": "store",
        "callback_service": "Gemini.Deliver Package",
    },
    {
        "name": "Deliver Package",
        "application": "Gemini",
        "description": "Delivers data about stored packages to configured service",
        "external_uri": "deliver-packages",
        "service_route": "deliver",
        "callback_service": "Gemini.Request SIP Cleanup",
    },
    {
        "name": "Request SIP Cleanup",
        "application": "Gemini",
        "description": "Requests deletion of processed SIPs from source directory.",
        "external_uri": "request-sip-cleanup",
        "service_route": "request-cleanup",
    },
    {
        "name": "Store Package Data",
        "application": "Aquarius",
        "description": "Stores incoming transfer objects",
        "external_uri": "store-data",
        "service_route": "packages",
        "callback_service": "Aquarius.Process Accessions",
    },
    {
        "name": "Process Accessions",
        "application": "Aquarius",
        "description": "Transforms and delivers accession data to ArchivesSpace",
        "external_uri": "process-accessions",
        "service_route": "accessions",
        "callback_service": "Aquarius.Update Accession Status",
    },
    {
        "name": "Update Accession Status",
        "application": "Aquarius",
        "description": "Sends information about updated accessions",
        "external_uri": "update-accessions",
        "service_route": "send-accession-update",
        "callback_service": "Aquarius.Process Grouping Components",
    },
    {
        "name": "Process Grouping Components",
        "application": "Aquarius",
        "description": "Transforms and delivers grouping component data to ArchivesSpace",
        "external_uri": "process-grouping-components",
        "service_route": "grouping-components",
        "callback_service": "Aquarius.Process Transfer Components",
    },
    {
        "name": "Process Transfer Components",
        "application": "Aquarius",
        "description": "Transforms and delivers transfer data to ArchivesSpace",
        "external_uri": "process-transfer-components",
        "service_route": "transfer-components",
        "callback_service": "Aquarius.Process Digital Objects",
    },
    {
        "name": "Process Digital Objects",
        "application": "Aquarius",
        "description": "Transforms and delivers digital object data to ArchivesSpace",
        "external_uri": "process-digital-objects",
        "service_route": "digital-objects",
        "callback_service": "Aquarius.Update Transfer Status",
    },
    {
        "name": "Update Transfer Status",
        "application": "Aquarius",
        "description": "Sends information about updated transfers.",
        "external_uri": "update-transfers",
        "service_route": "send-update",
    }
]

TASKS = [
    {"name": "Process queued callbacks", "task": "gateway.tasks.queue_callbacks"},
    {"name": "Delete successful results", "task": "gateway.tasks.delete_successful"}
]


class Command(BaseCommand):
    help = "Set up services based on defaults."

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Deletes existing users, applications, services, and tasks.',
        )

    def handle(self, *args, **options):
        if options["reset"]:
            User.objects.all().delete()
            Source.objects.all().delete()
            Application.objects.all().delete()
            ServiceRegistry.objects.all().delete()
            CrontabSchedule.objects.all().delete()
            PeriodicTask.objects.all().delete()
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

        for source in SOURCES:
            if not Source.objects.filter(apikey=source['apikey']).exists():
                Source.objects.create(
                    user=User.objects.get(username=source['username']),
                    apikey=source['apikey']
                )
        print("Created sources")

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

        for service in SERVICES:
            if not ServiceRegistry.objects.filter(
                    name=service['name'],
                    external_uri=service['external_uri'],
                    service_route=service['service_route']).exists():
                new_service = ServiceRegistry.objects.create(
                    name=service['name'],
                    application=Application.objects.get(name=service['application']),
                    description=service['description'],
                    external_uri=service['external_uri'],
                    service_route=service['service_route'],
                    plugin=service.get('plugin', 0),
                    is_active=True,
                    is_private=False,
                    method=service.get("method", "POST"),
                )
                if service.get('sources'):
                    for source in service['sources']:
                        new_service.sources.add(
                            Source.objects.get(
                                user__username=source))
                print("Created service: {}".format(service['name']))

        for service in SERVICES:
            object = ServiceRegistry.objects.get(name=service['name'])
            object.callback_service = ServiceRegistry.objects.get(
                application__name=service['callback_service'].split('.')[0],
                name=service['callback_service'].split('.')[1]) if service.get('callback_service') else None
            object.save()
        print("Callbacks and POST Services linked")

        every_minute, _ = CrontabSchedule.objects.get_or_create(minute='*', hour='*',
                                                                day_of_week='*', day_of_month='*',
                                                                month_of_year='*')
        daily, _ = CrontabSchedule.objects.get_or_create(minute='0', hour='4',
                                                         day_of_week='*', day_of_month='*',
                                                         month_of_year='*')
        for task in TASKS:
            if not PeriodicTask.objects.filter(
                    name=task["name"], task=task["task"]).exists():
                PeriodicTask.objects.create(crontab=every_minute, name=task["name"],
                                            task=task["task"])

        print("Tasks scheduled")
