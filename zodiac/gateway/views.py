from django.views.generic import TemplateView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.detail import BaseDetailView, DetailView
from django.views.generic.list import ListView
from django_datatables_view.base_datatable_view import BaseDatatableView
from django.urls import reverse_lazy
from django_celery_results.models import TaskResult
from rest_framework.response import Response
from rest_framework import status
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView
from .service_library import send_service_request, check_service_plugin
from .models import Application, ServiceRegistry, RequestLog
from .mixins import JSONResponseMixin


applications_update_fields = ['name', 'app_host', 'app_port']
services_registry_fields = [
    'name',
    'application',
    'description',
    'external_uri',
    'service_route',
    'plugin',
    'consumers',
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
        self.request = request

        # CHECKs
        # Expects path api/external uri/service_route
        path = request.path_info.split('/')
        if len(path) < 2:
            return self.bad_request(request=request, msg="No URL path.")

        # Application in registry; service route is valid; and request method is registered for route
        registry = ServiceRegistry.objects.filter(external_uri=path[2], method=request.method)
        if registry.count() != 1:
            return self.bad_request(request=request, msg="No service registry matching path {} and method {}.".format(path[2], request.method))

        valid, msg = check_service_plugin(registry[0], request)
        if not valid:
            return self.bad_request(registry[0], msg=msg)

        # Check if service and is_active and system is active
        if not registry[0].can_safely_execute():
            # Internally can log why this is the case
            return self.bad_request(registry[0], request, msg="Service {} cannot be executed.".format(registry[0]))

        res = send_service_request(registry[0], request)
        data = {'SUCCESS': 0}
        if res:
            data['SUCCESS'] = 1

        # try:
        #     data = res.json()
        # except ValueError:
        #     print('Decoding JSON failed')
        #     return self.bad_request(registry[0],request)

        RequestLog.create(registry[0], status.HTTP_200_OK, request.META['REMOTE_ADDR'])
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
        context['recent_services'] = ServiceRegistry.objects.all().order_by('-modified_time')[:5]
        context['recent_applications'] = Application.objects.all().order_by('-modified_time')[:5]
        context['recent_results'] = TaskResult.objects.all().order_by('-date_done')[:10]
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
    model = ServiceRegistry
    success_url = reverse_lazy('services-list')


class ServicesTriggerView(JSONResponseMixin, BaseDetailView):
    model = ServiceRegistry

    def render_to_response(self, context, **response_kwargs):
        result = send_service_request(self.object)
        data = {'SUCCESS': 0}
        # CAN WE CHECK IF IT WAS QUED?
        if result:
            data['SUCCESS'] = 1

        return self.render_to_json_response(context=data, **response_kwargs)


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
    model = TaskResult
    columns = ['task_id', 'date_done', 'status']
    order_columns = ['task_id', 'date_done', 'status']
    max_display_length = 500

    def get_filter_method(self): return self.FILTER_ICONTAINS

    def render_column(self, row, column):
        if column == 'task_id':
            url = str(reverse_lazy('results-detail', kwargs={"pk":row.id}))
            return '<a href="'+url+'">'+row.task_id+'</a>'
        else:
            return super(ResultsDatatableView, self).render_column(row, column)


class ResultsDetailView(DetailView):
    template_name = "gateway/results_detail.html"
    model = TaskResult
