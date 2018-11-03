import requests
from django.views.generic import TemplateView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.detail import DetailView
from django.views.generic.detail import BaseDetailView
from django.views.generic.list import ListView
from django.shortcuts import render
from django.http import HttpResponse
from django.urls import reverse_lazy
from django_celery_results.models import TaskResult
from rest_framework.response import Response
from rest_framework import status
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.renderers import JSONRenderer
from .models import Application, ServiceRegistry, RequestLog
from .mixins import JSONResponseMixin


systems_update_fields = ['name', 'app_host', 'app_port']
services_registry_fields = [
    'name',
    'application',
    'description',
    'external_uri',
    'service_route',
    'plugin',
    'consumers',
    'is_private',
    'method'
]


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
            return self.bad_request(request=request, msg="No URL path.")

        # Application in registry; service route is valid; and request method is registered for route
        registry = ServiceRegistry.objects.filter(external_uri=path[2], method=request.method)
        print(path[2])
        if registry.count() != 1:
            return self.bad_request(request=request, msg="No service registry matching path and method.")

        valid, msg = registry[0].check_plugin(request)
        if not valid:
            return self.bad_request(registry[0], msg=msg)

        # Check if service and is_active and system is active
        if not registry[0].can_safely_execute():
            # Internally can log why this is the case
            return self.bad_request(registry[0], request, msg="Service cannot be executed.")

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

    def bad_request(self, service=None, request=request, msg=None):
        RequestLog.create(service, status.HTTP_400_BAD_REQUEST, request.META['REMOTE_ADDR'])
        return Response({"detail": msg}, status=status.HTTP_400_BAD_REQUEST)

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


class SplashView(TemplateView):
    template_name = "gateway/splash.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['recent_services'] = ServiceRegistry.objects.all().order_by('-modified_time')
        context['recent_systems'] = Application.objects.all().order_by('-modified_time')
        context['recent_results'] = TaskResult.objects.all().order_by('-date_done')
        return context


class ServicesAddView(CreateView):
    template_name = "gateway/services_add.html"
    model = ServiceRegistry
    fields = services_registry_fields


class ServicesListView(ListView):
    template_name = "gateway/services_list.html"
    model = ServiceRegistry


class ServicesDetailView(DetailView):
    template_name = "gateway/services_detail.html"
    model = ServiceRegistry


class ServicesUpdateView(UpdateView):
    template_name = "gateway/services_update.html"
    model = ServiceRegistry
    fields = services_registry_fields + ['is_active']


class ServicesDeleteView(DeleteView):
    template_name = "gateway/services_delete.html"
    model = Application
    success_url = reverse_lazy('services-list')


class ServicesTriggerView(JSONResponseMixin, BaseDetailView):
    model = ServiceRegistry

    def render_to_response(self, context, **response_kwargs):
        result = self.object.send_request()
        data = {'SUCCESS': 0}
        # CAN WE CHECK IF IT WAS QUED?
        if result:
            data['SUCCESS'] = 1
            # Store async ID FOR TEMP STorage until it's gone
            self.object.store_async_result(result)

        return self.render_to_json_response(context=data, **response_kwargs)


class ServicesASyncResultsView(JSONResponseMixin, BaseDetailView):
    model = ServiceRegistry

    def render_to_response(self, context, **response_kwargs):
        logs = self.object.retrieve_async_result_logs()
        data = {'SUCCESS':0}
        if logs:
            data['SUCCESS'] = 1
            data['logs'] = logs
        return self.render_to_json_response(context=data, **response_kwargs)


class SystemsAddView(CreateView):
    template_name = "gateway/systems_add.html"
    model = Application
    fields = systems_update_fields


class SystemsDetailView(DetailView):
    template_name = "gateway/systems_detail.html"
    model = Application


class SystemsListView(ListView):
    template_name = "gateway/systems_list.html"
    model = Application


class SystemsUpdateView(UpdateView):
    template_name = "gateway/systems_update.html"
    model = Application
    fields = systems_update_fields + ['is_active']


class SystemsDeleteView(DeleteView):
    template_name = "gateway/systems_delete.html"
    model = Application
    success_url = reverse_lazy('systems-list')


class ResultsListView(ListView):
    template_name = "gateway/results_list.html"
    model = TaskResult


class ResultsDetailView(DetailView):
    template_name = "gateway/results_detail.html"
    model = TaskResult
