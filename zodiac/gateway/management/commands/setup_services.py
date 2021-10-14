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
        "name": "Aquarius",
        "host": "aquarius-web",
        "port": 8002,
        "health_check_path": "/status",
        "services": [
            {
                "name": "Store Package Data",
                "description": "Stores incoming transfer objects.",
                "external_uri": "store-data",
                "service_route": "packages",
                "has_external_trigger": True,
            },
            {
                "name": "Process Accessions",
                "description": "Transforms and delivers accession data to ArchivesSpace.",
                "service_route": "accessions",
            },
            {
                "name": "Update Accession Status",
                "description": "Sends information about updated accessions in Aurora.",
                "service_route": "send-accession-update",
            },
            {
                "name": "Process Grouping Components",
                "description": "Transforms and delivers grouping component data to ArchivesSpace.",
                "service_route": "grouping-components",
            },
            {
                "name": "Process Transfer Components",
                "description": "Transforms and delivers transfer data to ArchivesSpace.",
                "service_route": "transfer-components",
            },
            {
                "name": "Process Digital Objects",
                "description": "Transforms and delivers digital object data to ArchivesSpace.",
                "service_route": "digital-objects",
            },
            {
                "name": "Update Transfer Status",
                "description": "Sends information about updated transfers.",
                "service_route": "send-update",
            }
        ]
    },
    {
        "name": "Fornax",
        "host": "fornax-web",
        "port": 8003,
        "health_check_path": "/status",
        "services": [
            {
                "name": "Store SIPs",
                "description": "Stores incoming SIP objects.",
                "external_uri": "store-sips",
                "service_route": "sips",
                "has_external_trigger": True,
            },
            {
                "name": "Assemble SIP",
                "description": "Creates Archivematica-compliant SIPs.",
                "service_route": "assemble",
            },
            {
                "name": "Create Transfer",
                "description": "Starts and approves a transfer in Archivematica.",
                "service_route": "start",
            },
            {
                "name": "Request Bag Cleanup",
                "description": "Requests deletion of processed bags from source directory.",
                "service_route": "request-cleanup",
            },
            {
                "name": "Remove Completed Ingests",
                "description": "Removes completed ingests from Archivematica dashboard.",
                "service_route": "remove-ingests",
            },
            {
                "name": "Remove Completed Transfers",
                "description": "Removes completed transfers from Archivematica dashboard.",
                "service_route": "remove-transfers",
            },
            {
                "name": "Cleanup Transfers",
                "description": "Removes a transfer from the destination directory",
                "external_uri": "cleanup-transfers",
                "service_route": "cleanup",
                "has_external_trigger": True,
            }
        ]
    },
    {
        "name": "Gemini",
        "host": "gemini-web",
        "port": 8006,
        "health_check_path": "/status",
        "services": [
            {
                "name": "Create Package",
                "description": "Creates a package to be downloaded from Archivematica.",
                "external_uri": "create-package",
                "service_route": "packages",
                "has_external_trigger": True,
            },
            {
                "name": "Download Package",
                "description": "Downloads packages from Archivematica.",
                "service_route": "download",
            },
            {
                "name": "Store Package",
                "description": "Stores packages in Fedora",
                "service_route": "store",
            },
            {
                "name": "Deliver Package",
                "description": "Delivers data about stored packages to configured service.",
                "service_route": "deliver",
            },
            {
                "name": "Request SIP Cleanup",
                "description": "Requests deletion of processed SIPs from source directory.",
                "service_route": "request-cleanup",
            }
        ]
    },
    {
        "name": "Pictor",
        "host": "pictor-web",
        "port": 8012,
        "health_check_path": "/status",
        "services": [
            {
                "name": "Prepare Bags",
                "description": "Prepares bags for derivative creation",
                "service_route": "prepare",
            },
            {
                "name": "Make JPEG200s",
                "description": "Creates JP2000 derivatives from TIFFs",
                "service_route": "make-jp2",
            },
            {
                "name": "Make PDFs",
                "description": "Creates concatenated PDF file from JP2 derivatives",
                "service_route": "make-pdf",
            },
            {
                "name": "Make IIIF manifest",
                "description": "Creates a IIIF presentation manifest from JP2 files.",
                "service_route": "make-manifest",
            },
            {
                "name": "Upload",
                "description": "Uploads files to AWS.",
                "service_route": "upload",
            },
            {
                "name": "Cleanup",
                "description": "Removes bag files that have been processed.",
                "service_route": "cleanup",
            }
        ]
    },
    {
        "name": "Ursa Major",
        "host": "ursa-major-web",
        "port": 8005,
        "health_check_path": "/status",
        "services": [
            {
                "name": "Store Accessions",
                "description": "Stores incoming accession data and creates associated transfer objects.",
                "external_uri": "store-accessions",
                "service_route": "accessions",
                "plugin": 2,
                "has_external_trigger": True,
                "sources": ["aurora"],
            },
            {
                "name": "Store Bags",
                "description": "Stores incoming bag data.",
                "external_uri": "store-bags",
                "service_route": "bags",
                "plugin": 2,
                "has_external_trigger": True,
                "sources": ["zorya"]
            },
            {
                "name": "Discover Bags",
                "description": "Checks for transfer files and, if found, moves them to storage.",
                "service_route": "bagdiscovery",
            },
            {
                "name": "Deliver Bags",
                "description": "Delivers discovered transfers to configured service.",
                "service_route": "bagdelivery",
            },
            {
                "name": "Cleanup Bags",
                "description": "Delivers discovered transfers to configured service.",
                "external_uri": "cleanup-bags",
                "service_route": "cleanup",
                "has_external_trigger": True,
            }
        ]
    },
    {
        "name": "Zorya",
        "host": "zorya-web",
        "port": 8011,
        "health_check_path": "/status",
        "services": [
            {
                "name": "Download Objects",
                "description": "Downloads an object from an S3 buckent and then deletes it.",
                "service_route": "download-objects",
            },
            {
                "name": "Discover Bags",
                "description": "Validates bag structure and bag info file, renames bag with unique ID.",
                "service_route": "discover-bags",
            },
            {
                "name": "Assign Rights",
                "description": "Send rights IDs to external service and receive JSON in return.",
                "service_route": "assign-rights",
            },
            {
                "name": "Make Package",
                "description": "Create JSON according to Ursa Major schema and package with bag.",
                "service_route": "make-package",
            },
            {
                "name": "Deliver Package",
                "description": "Deliver package to Ursa Major",
                "service_route": "deliver-package",
            },
        ]
    }
]

TASKS = [
    {"name": "Process queued callbacks", "task": "gateway.tasks.queue_services"},
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
            if not Source.objects.filter(apikey=source['apikey'], user__username=source['username']).exists():
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

            for service in application["services"]:
                if not ServiceRegistry.objects.filter(
                        name=service['name'],
                        application=Application.objects.get(name=application["name"]),
                        service_route=service['service_route']).exists():
                    new_service = ServiceRegistry.objects.create(
                        name=service['name'],
                        application=Application.objects.get(name=application["name"]),
                        description=service['description'],
                        external_uri=service.get('external_uri'),
                        service_route=service['service_route'],
                        plugin=service.get('plugin', 0),
                        has_external_trigger=service.get('has_external_trigger', False),
                        is_active=True,
                        is_private=False,
                        method=service.get("method", "POST"),
                    )
                    if service.get('sources'):
                        for source in service['sources']:
                            new_service.sources.add(
                                Source.objects.get(
                                    user__username=source))
                    print(f"Created service: {service['name']}")

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
