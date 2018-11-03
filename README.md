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

To process the tasks in the queue, first log into the gateway-web container:

```
docker-compose exec gateway-web bash
```

and then run:

```
celery -A zodiac worker -l info
```


## License

This code is released under an [MIT License](LICENSE).
