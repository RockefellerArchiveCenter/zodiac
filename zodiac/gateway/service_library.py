import requests
import json
from rest_framework.authentication import BasicAuthentication

from .tasks import queue_request
from .views_library import render_service_path, render_post_service_url
from .models import ServiceRegistryTask


def send_service_request(service, request={}):
    headers = {}
    files = {}

    if request:
        files = request.FILES

        if service.plugin != 1 and request.META.get('HTTP_AUTHORIZATION'):
            headers['authorization'] = request.META.get('HTTP_AUTHORIZATION')
        # headers['content-type'] = request.content_type

        strip = '/api/' + service.external_uri
        full_path = request.get_full_path()[len(strip):]

        url = render_service_path(service, full_path)

        method = request.method.lower()

        for k, v in request.FILES.items():
            request.data.pop(k)

        #force json

        if request.content_type and request.content_type.lower() == 'application/json':
            data = json.dumps(request.data)
            headers['content-type'] = request.content_type
        else:
            data = request.data

    else:
        headers['content-type'] = 'application/json'
        method = service.method.lower()
        data = {}
        url = render_service_path(service, '')

    # chain exceptions
    async_result = queue_request.delay(
        method,
        url,
        headers=headers,
        data=data,
        files=files,
        params={'post_service_url': render_post_service_url(service)}
    )
    print(async_result, 'this is async')

    return async_result.id


def check_service_plugin(service, request):
    if service.plugin == 0:
        return True, ''

    elif service.plugin == 1:
        auth = BasicAuthentication()
        try:
            user, password = auth.authenticate(request)
        except:
            return False, 'Authentication credentials were not provided'

        if service.consumers.filter(user=user):
            return True, ''
        else:
            return False, 'permission not allowed'
    elif service.plugin == 2:
        apikey = request.META.get('HTTP_APIKEY')
        consumers = service.consumers.all()
        for consumer in consumers:
            if apikey == consumer.apikey:
                return True, ''
        return False, 'apikey need'
    elif service.plugin == 3:
        consumer = service.consumers.all()
        if not consumer:
            return False, 'consumer need'
        request.META['HTTP_AUTHORIZATION'] = requests.auth._basic_auth_str(consumer[0].user.username, consumer[0].apikey)
        return True, ''
    else:
        raise NotImplementedError("plugin %d not implemented" % service.plugin)


def retrieve_async_result_logs(service):
    return list(ServiceRegistryTask.objects.filter(service=service).values_list('async_result_id', flat=True))


def store_async_result(service, async_result_id):
    ServiceRegistryTask.objects.create(
        service=service,
        async_result_id=async_result_id
    )
