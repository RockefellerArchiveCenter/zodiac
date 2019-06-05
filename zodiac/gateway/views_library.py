# Create your tasks here
from __future__ import absolute_import, unicode_literals
import urllib.parse as urlparse


def render_service_path(service, uri=''):
    if not service:
        return ''

    app_port = (':{}'.format(service.application.app_port) if service.application.app_port > 0 else '')
    url = 'http://{}{}/{}{}'.format(
        service.application.app_host, app_port, service.service_route, uri)

    # add slash to URL end
    if url[-1] != '/':
        url = '{}/'.format(url) 

    parsed_url = urlparse.urlparse(url)
    parsed_url_parts = list(parsed_url)

    query = dict(urlparse.parse_qsl(parsed_url_parts[4]))
    query['format'] = 'json'

    parsed_url_parts[4] = urlparse.urlencode(query)

    return urlparse.urlunparse(parsed_url_parts)
