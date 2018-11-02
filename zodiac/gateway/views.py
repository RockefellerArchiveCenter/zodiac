from rest_framework import status
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import ServiceRegistry, RequestLog


class Gateway(APIView):

    authentication_classes = ()
    renderer_classes = (JSONRenderer,)
    request = {}

    def operation(self, request):
        self.request = request

        # CHECKs
        # Expects path api/external uri/service_route
        path = request.path_info.split('/')
        if len(path) < 2:
            return self.bad_request(request=request)

        # Application in registry; service route is valid; and request method is registered for route
        registry = ServiceRegistry.objects.filter(external_uri=path[2], method=request.method)
        if registry.count() != 1:
            return self.bad_request(request=request)

        valid, msg = registry[0].check_plugin(request)
        if not valid:
            return self.bad_request(registry[0],msg=msg)

        # Check if service and is_active and system is active
        if not registry[0].can_safely_execute():
            # Internally can log why this is the case
            return self.bad_request(registry[0],request)

        res = registry[0].send_request(request)
        data = {'SUCCESS': 0}
        if res:
            data['SUCCESS'] = 1

        # try:
        #     data = res.json()
        # except ValueError:
        #     print('Decoding JSON failed')
        #     return self.bad_request(registry[0],request)

        return Response(data=data)

    def bad_request(self, service=None, request=request, msg='bad request'):
        RequestLog.create(service, status.HTTP_400_BAD_REQUEST, request.META['REMOTE_ADDR'])
        return Response(msg, status=status.HTTP_400_BAD_REQUEST)

    
    def get(self, request):
        return self.operation(request)

    def post(self, request):
        return self.operation(request)

    def put(self, request):
        return self.operation(request)
    
    def patch(self, request):
        return self.operation(request)
    
    def delete(self, request):
        return self.operation(request)