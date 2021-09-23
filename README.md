# zodiac

API gateway and administration interface for [Project Electron](https://github.com/RockefellerArchiveCenter/project_electron) microservices, managed via a message queue.

[![Build Status](https://travis-ci.org/RockefellerArchiveCenter/zodiac.svg?branch=base)](https://travis-ci.org/RockefellerArchiveCenter/zodiac)

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

The first time you start zodiac, a set of Applications, Services, Users and Tasks will be created. You can recreate this default application state at any time by running a custom Django management command and passing the `--reset` flag:

    $ python manage.py setup_services --reset

## Usage

zodiac provides a unified interface for microservices, allowing users to both administer these services and the applications to which they belong as well as track activity within the microservice layer. It also includes a message queue which improves service scalability and activity monitoring.

### Applications
Applications are clusters of services which share some common code. In the context of Project Electron, these are a series of Django projects. However, zodiac doesn't care how these applications are implemented as long as the services they provide are available via REST endpoints.

### Services
Services provide small and clearly-defined functionality, which are called via REST endpoints. If the service requires it, zodiac can pass an additional URL to a service (via a `post_service_url` parameter) so it can trigger another service via a POST request. This is especially useful if a service needs to deliver a payload to another service.

### Message Queue
zodiac includes a messaging layer to queue and process tasks. It does this via [Celery](https://github.com/celery/celery/) and [Celery Beat](https://github.com/celery/django-celery-beat), which are installed as daemons in the Docker container and run on startup. To process queued callbacks, you will need to add a periodic task using the Django Admin interface. Task results are available in the user interface.

### Default Users
When you first spin Zodiac up, a number of users will be created as follows:
- A system administrator (in Django terms, a superuser), identified by the username `admin` and password `adminpass`
- Two system users, for applications which authorized to deliver data to specific services. These are:
  - Zorya, a system which creates packages from digitized and legacy born-digital content, identified by the username `zorya` and API key `zoryakey`.
  - Aurora, a system which creates packages from born-digital content, identified by the username `aurora` and the API key `aurorakey`.

## Development
This repository contains a configuration file for git [pre-commit](https://pre-commit.com/) hooks which help ensure that code is linted before it is checked into version control. It is strongly recommended that you install these hooks locally by installing pre-commit and running `pre-commit install`.

## License
This code is released under an [MIT License](LICENSE).
