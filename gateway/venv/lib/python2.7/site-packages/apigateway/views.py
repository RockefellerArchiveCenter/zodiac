# -*- coding: utf-8 -*-
import requests
from django.shortcuts import render
from django.http import HttpResponse
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from models import Api

class gateway(APIView):
    authentication_classes = ()

    def operation(self, request):
        path = request.path_info.split('/')
        if len(path) < 2:
            return Response('bad request', status=status.HTTP_400_BAD_REQUEST)
        
        apimodel = Api.objects.filter(name=path[2])
        if apimodel.count() != 1:
            return Response('bad request', status=status.HTTP_400_BAD_REQUEST)

        valid, msg = apimodel[0].check_plugin(request)
        if not valid:
            return Response(msg, status=status.HTTP_400_BAD_REQUEST)

        res = apimodel[0].send_request(request)
        if res.status_code == 204:
            data = res.content if res.content else None
        else:
            if res.headers.get('Content-Type', '').lower() == 'application/json':
                data = res.json()
            else:
                data = res.content
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
