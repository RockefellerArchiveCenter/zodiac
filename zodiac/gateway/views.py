import json

from dateutil import tz
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView
from django.views.generic.detail import BaseDetailView, DetailView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.views.generic.list import ListView
from django_celery_results.models import TaskResult
from django_datatables_view.base_datatable_view import BaseDatatableView
from rest_framework import status
from rest_framework.generics import RetrieveAPIView
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView

from .mixins import JSONResponseMixin
from .models import Application, RequestLog, ServiceRegistry, Source, User
from .serializers import ServiceRegistrySerializer
from .service_library import check_service_auth, send_service_request
from .views_library import get_health_check_status

applications_update_fields = ['name', 'app_host', 'app_port', 'health_check_path']
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
]


class Gateway(APIView):

    authentication_classes = ()
    renderer_classes = (JSONRenderer,)
    request = {}

    def bad_url(self, request):
        """
        Checks to ensure URL is correctly formatted.
        Expects path_info variable to be `api/{external uri}/{service_route}`
        """
        path = request.path_info.split('/')
        if len(path) < 2:
            return True
        return False

    def operation(self, request):
        # Check URL format
        if self.bad_url(request):
            return self.bad_request(request=request, msg="No URL path.")

        external_uri = request.path_info.split('/')[2]

        # Ensures that exactly one ServiceRegistry object matches the URI path and method.
        try:
            registry = ServiceRegistry.objects.get(external_uri=external_uri, method=request.method)
        except ServiceRegistry.DoesNotExist:
            return self.bad_request(request=request,
                                    msg="No service registry matching path {} and method {}."
                                        .format(external_uri, request.method))
        except ServiceRegistry.MultipleObjectsReturned:
            return self.bad_request(request=request,
                                    msg="More than one service registry matching path {} and method {}."
                                    .format(external_uri, request.method))

        # Checks authentication
        valid, msg = check_service_auth(registry, request)
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
        RequestLog.objects.create(service=service, status_code=status.HTTP_400_BAD_REQUEST, request_url=request.META['REMOTE_ADDR'])
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
        for app in context['applications']:
            app.health_check_status = get_health_check_status(app)
        return context


@method_decorator(login_required, name='dispatch')
class ServicesAddView(CreateView):
    template_name = "gateway/add.html"
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


@method_decorator(login_required, name='dispatch')
class ServicesUpdateView(UpdateView):
    template_name = "gateway/update.html"
    model = ServiceRegistry
    fields = services_registry_fields + ['is_active']


@method_decorator(login_required, name='dispatch')
class ServicesDeleteView(DeleteView):
    template_name = "gateway/delete.html"
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
        except Exception:
            data = {'SUCCESS': 0}
        return self.render_to_json_response(context=data, **kwargs)


@method_decorator(login_required, name='dispatch')
class ApplicationsAddView(CreateView):
    template_name = "gateway/add.html"
    model = Application
    fields = applications_update_fields


class ApplicationsDetailView(DetailView):
    template_name = "gateway/applications_detail.html"
    model = Application

    def get_context_data(self, *args, **kwargs):
        context = super(DetailView, self).get_context_data(*args, **kwargs)
        context['health_check_status'] = get_health_check_status(self.object)
        return context


class ApplicationsListView(ListView):
    template_name = "gateway/applications_list.html"
    model = Application

    def get_context_data(self, *args, **kwargs):
        context = super(ListView, self).get_context_data(*args, **kwargs)
        for obj in context['object_list']:
            obj.health_check_status = get_health_check_status(obj)
        return context


@method_decorator(login_required, name='dispatch')
class ApplicationsUpdateView(UpdateView):
    template_name = "gateway/update.html"
    model = Application
    fields = applications_update_fields + ['is_active']


@method_decorator(login_required, name='dispatch')
class ApplicationsDeleteView(DeleteView):
    template_name = "gateway/delete.html"
    model = Application
    success_url = reverse_lazy('applications-list')


class ResultsListView(TemplateView):
    template_name = "gateway/results_list.html"


class ResultsDatatableView(BaseDatatableView):
    model = RequestLog
    columns = ['async_result_id', 'service__name', 'task_result_status', 'task_result__result', 'task_result__date_done']
    order_columns = ['async_result_id', 'service__name', 'task_result_status', 'task_result__result', 'task_result__date_done']
    max_display_length = 500

    def get_filter_method(self):
        return self.FILTER_ICONTAINS

    def get_task_result(self, result):
        task_result = ''
        if result.task_result:
            task_result = result.task_result.result
            if 'exc_message' in result.task_result.result:
                task_result = str(json.loads(result.task_result.result).get('exc_message')[0])
        return task_result

    def get_status_display(self, status):
        status = status if status else "Idle"
        statuses = {
            "Error": ['danger', 'times-circle'],
            "Idle": ['warning', 'circle'],
            "Success": ['success', 'check-circle'],
        }
        return '<span class="text-{}">{} <i class="fa fa-{}"></i></span>'.format(statuses[status][0], status, statuses[status][1])

    def prepare_results(self, qs):
        json_data = []
        for result in qs:
            result.refresh_from_db()
            async_result_id = result.async_result_id if result.async_result_id else ""
            json_data.append([
                '<a href="' + str(reverse_lazy('results-detail', kwargs={"pk": result.id})) + '">' + async_result_id + '</a>',
                '<a href="' + str(reverse_lazy('services-detail', kwargs={"pk": result.service.id})) + '">' + result.service.full_name + '</a>' if result.service else '',
                self.get_status_display(result.task_result_status),
                '<pre>' + self.get_task_result(result) + '</pre>',
                result.task_result.date_done.astimezone(tz.tzlocal()).strftime('%b %e, %Y %I:%M:%S %p') if result.task_result else '',
            ])
        return json_data


class ResultsDetailView(DetailView):
    template_name = "gateway/results_detail.html"
    model = RequestLog


@method_decorator(login_required, name='dispatch')
class SourcesAddView(CreateView):
    template_name = "gateway/add.html"
    model = Source
    fields = ('user', 'apikey')


class SourcesDetailView(DetailView):
    template_name = "gateway/sources_detail.html"
    model = Source


class SourcesListView(ListView):
    template_name = "gateway/sources_list.html"
    model = Source


@method_decorator(login_required, name='dispatch')
class SourcesUpdateView(UpdateView):
    template_name = "gateway/update.html"
    model = Source
    fields = ('user', 'apikey')


@method_decorator(login_required, name='dispatch')
class SourcesDeleteView(DeleteView):
    template_name = "gateway/delete.html"
    model = Source
    success_url = reverse_lazy('sources-list')


@method_decorator(login_required, name='dispatch')
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


@method_decorator(login_required, name='dispatch')
class UsersUpdateView(UpdateView):
    template_name = "gateway/users_update.html"
    model = User
    fields = ('username',)
    success_url = reverse_lazy('users-list')


@method_decorator(login_required, name='dispatch')
class UsersDeleteView(DeleteView):
    template_name = "gateway/users_delete.html"
    model = User
    success_url = reverse_lazy('users-list')


class UsersLoginView(LoginView):
    template_name = "gateway/users_login.html"


class UsersLogoutView(LogoutView):
    next_page = reverse_lazy("dashboard")
