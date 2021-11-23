import json

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
        params={},
        service_id=service.pk,
    )

    return async_result.id


def check_service_auth(service, request):
    if service.plugin == ServiceRegistry.REMOTE_AUTH:
        return True, ""

    elif service.plugin == ServiceRegistry.KEY_AUTH:
        apikey = request.META.get("HTTP_APIKEY")
        sources = service.sources.all()
        msg = False, "API Key needed."
        for source in sources:
            if apikey == source.apikey:
                msg = True, ""
        return msg
    else:
        raise NotImplementedError("Plugin %d not implemented" % service.plugin)
