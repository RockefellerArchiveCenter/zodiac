import json
from dateutil import tz

from django_celery_results.models import TaskResult
from django.contrib.auth.models import User
from django.views.generic import TemplateView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.detail import BaseDetailView, DetailView
from django.views.generic.list import ListView
from django_datatables_view.base_datatable_view import BaseDatatableView
from django.urls import reverse_lazy
from rest_framework import status
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import RetrieveAPIView

from zodiac import settings
from .service_library import send_service_request, check_service_plugin
from .models import Application, ServiceRegistry, RequestLog, Source
from .mixins import JSONResponseMixin
from .serializers import ServiceRegistrySerializer


applications_update_fields = ['name', 'app_host', 'app_port']
services_registry_fields = [
    'name',
    'application',
    'description',
    'external_uri',
    'service_route',
    'plugin',
    'sources',
    'is_private',
    'method',
    'post_service',
    'callback_service',
]


class Gateway(APIView):

    authentication_classes = ()
    renderer_classes = (JSONRenderer,)
    request = {}

    def operation(self, request):
        # Checks to ensure URL is correctly formatted. Expects path api/external uri/service_route
        path = request.path_info.split('/')
        if len(path) < 2:
            return self.bad_request(request=request, msg="No URL path.")

        # Checks that application is in registry, service route is valid, and request method is registered for route
        try:
            registry = ServiceRegistry.objects.get(external_uri=path[2], method=request.method)
        except ServiceRegistry.DoesNotExist:
            return self.bad_request(request=request, msg="No service registry matching path {} and method {}.".format(path[2], request.method))
        except ServiceRegistry.MultipleObjectsReturned:
            return self.bad_request(request=request, msg="More than one service registry matching path {} and method {}.".format(path[2], request.method))

        # Checks authentication
        valid, msg = check_service_plugin(registry, request)
        if not valid:
            return self.bad_request(service=registry, request=request, msg=msg)

        # Checks if both service and system are active
        if not registry.service_active():
            return self.bad_request(registry, request, msg="Service {} cannot be executed.".format(registry))

        res = send_service_request(registry, request)
        data = {'SUCCESS': 0}
        if res:
            data['SUCCESS'] = 1

        return Response(data=data)

    def bad_request(self, service=None, request=request, msg="Bad Request."):
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
        context['applications'] = Application.objects.all().order_by('name')
        context['services'] = ServiceRegistry.objects.exclude(application__name='Pisces')
        context['recent_errors'] = RequestLog.objects.exclude(task_result__status='SUCCESS').order_by('-task_result__date_done')[:5]
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

    def get_context_data(self, **kwargs):
        context = super(ServicesDetailView, self).get_context_data(**kwargs)
        context['service_results'] = RequestLog.objects.filter(service=self.object.pk).order_by('-task_result__date_done')[:5]
        return context


class ServicesJSONView(RetrieveAPIView):
    model = ServiceRegistry
    queryset = ServiceRegistry.objects.all()
    serializer_class = ServiceRegistrySerializer


class ServicesUpdateView(UpdateView):
    template_name = "gateway/services_update.html"
    model = ServiceRegistry
    fields = services_registry_fields + ['is_active']


class ServicesDeleteView(DeleteView):
    template_name = "gateway/services_delete.html"
    model = ServiceRegistry
    success_url = reverse_lazy('services-list')


class ServicesTriggerView(JSONResponseMixin, BaseDetailView):
    model = ServiceRegistry

    def render_to_response(self, context, **response_kwargs):
        result = send_service_request(self.object)
        data = {'SUCCESS': 0}
        if result:
            data['SUCCESS'] = 1

        return self.render_to_json_response(context=data, **response_kwargs)


class ServicesClearErrorsView(JSONResponseMixin, BaseDetailView):
    model = ServiceRegistry

    def render_to_response(self, context, **kwargs):
        try:
            TaskResult.objects.filter(status='FAILURE', request_log__service=self.object).delete()
            data = {'SUCCESS': 1}
        except Exception as e:
            data = {'SUCCESS': 0}
        return self.render_to_json_response(context=data, **kwargs)


class ApplicationsAddView(CreateView):
    template_name = "gateway/applications_add.html"
    model = Application
    fields = applications_update_fields


class ApplicationsDetailView(DetailView):
    template_name = "gateway/applications_detail.html"
    model = Application


class ApplicationsListView(ListView):
    template_name = "gateway/applications_list.html"
    model = Application


class ApplicationsUpdateView(UpdateView):
    template_name = "gateway/applications_update.html"
    model = Application
    fields = applications_update_fields + ['is_active']


class ApplicationsDeleteView(DeleteView):
    template_name = "gateway/applications_delete.html"
    model = Application
    success_url = reverse_lazy('applications-list')


class ResultsListView(TemplateView):
    template_name = "gateway/results_list.html"


class ResultsDatatableView(BaseDatatableView):
    model = RequestLog
    columns = ['async_result_id', 'service__name', 'task_result_status', 'task_result__result', 'task_result__date_done']
    order_columns = ['async_result_id', 'service__name', 'task_result_status', 'task_result__result', 'task_result__date_done']
    max_display_length = 500

    def get_filter_method(self): return self.FILTER_ICONTAINS

    def get_task_result(self, result):
        task_result = ''
        if result.task_result:
            task_result = result.task_result.result
            if 'exc_message' in result.task_result.result:
                task_result = str(json.loads(result.task_result.result).get('exc_message')[0])
        return task_result

    def get_status_display(self, status):
        statuses = {
            "Error": ['danger', 'times-circle'],
            "Idle": ['default', 'circle'],
            "Success": ['success', 'check-circle']
        }
        return '<span class="text-{}">{} <i class="fa fa-{}"></i></span>'.format(statuses[status][0], status, statuses[status][1])

    def prepare_results(self, qs):
        json_data = []
        for result in qs:
            result.refresh_from_db()
            json_data.append([
                '<a href="'+str(reverse_lazy('results-detail', kwargs={"pk": result.id}))+'">'+result.async_result_id+'</a>',
                '<a href="'+str(reverse_lazy('services-detail', kwargs={"pk": result.service.id}))+'">'+result.service.name+'</a>' if result.service else '',
                self.get_status_display(result.task_result_status),
                '<pre>'+self.get_task_result(result)+'</pre>',
                result.task_result.date_done.astimezone(tz.tzlocal()).strftime('%b %e, %Y %I:%M:%S %p') if result.task_result else '',
            ])
        return json_data


class ResultsDetailView(DetailView):
    template_name = "gateway/results_detail.html"
    model = RequestLog


class SourcesAddView(CreateView):
    template_name = "gateway/sources_add.html"
    model = Source
    fields = ('user', 'apikey')


class SourcesDetailView(DetailView):
    template_name = "gateway/sources_detail.html"
    model = Source


class SourcesListView(ListView):
    template_name = "gateway/sources_list.html"
    model = Source


class SourcesUpdateView(UpdateView):
    template_name = "gateway/sources_update.html"
    model = Source
    fields = ('user', 'apikey')


class SourcesDeleteView(DeleteView):
    template_name = "gateway/sources_delete.html"
    model = Source
    success_url = reverse_lazy('sources-list')


class UsersAddView(CreateView):
    template_name = "gateway/users_add.html"
    model = User
    fields = ('username',)


class UsersDetailView(DetailView):
    template_name = "gateway/users_detail.html"
    model = User


class UsersListView(ListView):
    template_name = "gateway/users_list.html"
    model = User


class UsersUpdateView(UpdateView):
    template_name = "gateway/users_update.html"
    model = User
    fields = ('username',)
    success_url = reverse_lazy('users-list')


class UsersDeleteView(DeleteView):
    template_name = "gateway/users_delete.html"
    model = User
    success_url = reverse_lazy('users-list')
