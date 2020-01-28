import requests
import json
from rest_framework.authentication import BasicAuthentication

from .models import ServiceRegistry
from .tasks import queue_request
from .views_library import render_service_path


def send_service_request(service, request={}):
    headers = {}
    files = {}

    if service.has_active_task:
        return False

    if request:
        files = request.FILES

        if service.plugin != ServiceRegistry.BASIC_AUTH and request.META.get(
                "HTTP_AUTHORIZATION"):
            headers["authorization"] = request.META.get("HTTP_AUTHORIZATION")

        strip = "/api/" + service.external_uri
        full_path = request.get_full_path()[len(strip):]

        url = render_service_path(service, full_path)

        method = request.method.lower()

        for k, v in request.FILES.items():
            request.data.pop(k)

        if request.content_type and request.content_type.lower() == "application/json":
            data = json.dumps(request.data)
            headers["content-type"] = request.content_type
        else:
            data = request.data

    else:
        headers["content-type"] = "application/json"
        method = service.method.lower()
        data = {}
        url = render_service_path(service, "")

    async_result = queue_request.delay(
        method,
        url,
        headers=headers,
        data=data,
        files=files,
        params={
            "post_service_url": render_service_path(
                service.post_service,
                external=True)},
        service_id=service.pk,
    )

    return async_result.id


def check_service_auth(service, request):
    if service.plugin == ServiceRegistry.REMOTE_AUTH:
        return True, ""

    elif service.plugin == ServiceRegistry.BASIC_AUTH:
        auth = BasicAuthentication()
        try:
            user, password = auth.authenticate(request)
        except Exception:
            return False, "Authentication credentials were not provided."
        if service.source.filter(user=user):
            return True, ""
        else:
            return False, "Permission not allowed"
    elif service.plugin == ServiceRegistry.KEY_AUTH:
        apikey = request.META.get("HTTP_APIKEY")
        sources = service.sources.all()
        for source in sources:
            if apikey == source.apikey:
                return True, ""
        return False, "API Key needed."
    elif service.plugin == ServiceRegistry.SERVER_AUTH:
        source = service.sources.all()
        if not source:
            return False, "Source needed."
        request.META["HTTP_AUTHORIZATION"] = requests.auth._basic_auth_str(
            source[0].user.username, source[0].apikey)
        return True, ""
    else:
        raise NotImplementedError("Plugin %d not implemented" % service.plugin)
