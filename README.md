# zodiac

API gateway and administration interface for [Project Electron](https://github.com/RockefellerArchiveCenter/project_electron) microservices, managed via a message queue.

[![Build Status](https://travis-ci.org/RockefellerArchiveCenter/zodiac.svg?branch=master)](https://travis-ci.org/RockefellerArchiveCenter/zodiac)

## Setup

Install [git](https://git-scm.com/) and clone the repository

    $ git clone https://github.com/RockefellerArchiveCenter/zodiac.git

Install [Docker](https://store.docker.com/search?type=edition&offering=community) and run docker-compose from the root directory. You can include all associated microservice submodules.

    $ cd zodiac
    $ git submodule init
    $ git submodule update
    $ docker-compose up

Once the applications start successfully, you should be able to access zodiac in your browser at `http://localhost:8001`

When you're done, shut down docker-compose

    $ docker-compose down

Or, if you want to remove all data

    $ docker-compose down -v

The first time you start zodiac, a set of Applications and Services will be created. You can recreate this default set of services and applications at any time by running the `setup_services` Django management command, passing the `--reset` flag.

    $ python manage.py setup_services --reset


## Usage

zodiac provides a unified interface for microservices, allowing users to both administer these services and the applications to which they belong as well as track activity within the microservice layer. It also includes a message queue which improves service scalability and activity monitoring.

### Applications
Applications are clusters of services which share some common code. In the context of Project Electron, these are a series of Django projects. However, zodiac doesn't care how these applications are implemented as long as the services they provide are available via REST endpoints.

### Services
Services provide small and clearly-defined functionality, which are called via REST endpoints.

### Message Queue
zodiac includes a messaging layer to queue and process tasks. It does this via [Celery](https://github.com/celery/celery/) and [Celery Beat](https://github.com/celery/django-celery-beat), which are installed as daemons in the Docker container and run on startup. To process queued callbacks, you will need to add a periodic task using the Django Admin interface. Task results are available in the user interface.


## License

This code is released under an [MIT License](LICENSE).
