import requests
import urllib.parse as urlparse


def render_service_path(service, uri='', external=False):
    if not service:
        return ''

    app_port = (':{}'.format(service.application.app_port)
                if service.application.app_port > 0 else '')
    service_uri = service.external_uri if external else service.service_route
    url = 'http://{}{}/{}{}'.format(service.application.app_host,
                                    app_port, service_uri, uri)

    url = "{}/".format(url.rstrip("/"))
    parsed_url = list(urlparse.urlparse(url))
    query = dict(urlparse.parse_qsl(parsed_url[4]))
    query['format'] = 'json'
    parsed_url[4] = urlparse.urlencode(query)

    return urlparse.urlunparse(parsed_url)


def get_health_check_status(application):
    status = None
    if application.health_check_path:
        try:
            resp = requests.get(
                "http://{}:{}/{}/".format(
                    application.app_host,
                    application.app_port,
                    application.health_check_path.lstrip("/").rstrip("/"))).json()
            status = True if resp['health']['ping']['pong'] else False
        except Exception:
            status = None
    return status
