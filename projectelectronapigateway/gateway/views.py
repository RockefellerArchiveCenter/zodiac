import requests
from django.shortcuts import render
from django.http import HttpResponse
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from .models import ServiceRegistry

class Gateway(APIView):

    authentication_classes = ()

    def operation(self, request):

        # CHECKs
        # Expects path api/external uri/service_route
        path = request.path_info.split('/')
        if len(path) < 2:
            return Response('bad request', status=status.HTTP_400_BAD_REQUEST)

        print(path)
        # Application in registry; service route is valid; and request method is registered for route
        registry = ServiceRegistry.objects.filter(external_uri=path[2], method=request.method)
        if registry.count() != 1:
            return Response('bad request', status=status.HTTP_400_BAD_REQUEST)

        valid, msg = registry[0].check_plugin(request)
        if not valid:
            return Response(msg, status=status.HTTP_400_BAD_REQUEST)

        res = registry[0].send_request(request)

        # SHOULD FORCE JSON
        # if res.headers.get('Content-Type', '').lower() == 'application/json':
        #     data = res.json()
        # else:
        #     data = res.content
        return Response(data=data, status=res.status_code)
    
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