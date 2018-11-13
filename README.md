# Zodiac

API Gateway for Project Electron microservices.

## Installation

### Quick Start
If you have [git](https://git-scm.com/) and [Docker](https://www.docker.com/community-edition) installed:

      git clone https://github.com/RockefellerArchiveCenter/zodiac.git
      cd zodiac
      git submodule init
      git submodule update
      docker-compose up

To shut down Zodiac, run:

      `docker-compose down`

or, if you wish to remove all local data:

      `docker-compose down -v`

## Usage (under active development)

Celery and Celery Beat are installed and will be running on startup. To process queued callbacks, you will need to add a periodic task using Django Admin.


## License

This code is released under an [MIT License](LICENSE).
