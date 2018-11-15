# zodiac

API Gateway for [Project Electron](https://github.com/RockefellerArchiveCenter/project_electron) microservices.

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

## Usage (under active development)

Celery and Celery Beat are installed and will be running on startup. To process queued callbacks, you will need to add a periodic task using Django Admin.


## License

This code is released under an [MIT License](LICENSE).
