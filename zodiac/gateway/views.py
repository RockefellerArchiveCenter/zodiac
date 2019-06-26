from dateutil import tz
from django.views.generic import TemplateView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.detail import BaseDetailView, DetailView
from django.views.generic.list import ListView
from django_datatables_view.base_datatable_view import BaseDatatableView
from django.urls import reverse_lazy
from rest_framework import status
from rest_framework.decorators import detail_route
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import RetrieveAPIView
from .service_library import send_service_request, check_service_plugin
from .models import Application, ServiceRegistry, RequestLog
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
        context['recent_services'] = ServiceRegistry.objects.all().order_by('-modified_time')[:5]
        context['recent_applications'] = Application.objects.all().order_by('-modified_time')[:5]
        context['recent_results'] = RequestLog.objects.all().order_by('-task_result__date_done')[:10]
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
    model = RequestLog
    columns = ['async_result_id', 'service__name', 'task_result__result', 'task_result__date_done']
    order_columns = ['async_result_id', 'service__name', 'task_result__result', 'task_result__date_done']
    max_display_length = 500

    def get_filter_method(self): return self.FILTER_ICONTAINS

    def prepare_results(self, qs):
        json_data = []
        for result in qs:
            result.refresh_from_db()
            json_data.append([
                '<a href="'+str(reverse_lazy('results-detail', kwargs={"pk": result.id}))+'">'+result.async_result_id+'</a>',
                '<a href="'+str(reverse_lazy('services-detail', kwargs={"pk": result.service.id}))+'">'+result.service.name+'</a>' if result.service else '',
                '<pre>'+result.task_result.result+'</pre>' if result.task_result else '',
                result.task_result.date_done.astimezone(tz.tzlocal()).strftime('%b %e, %Y %I:%M:%S %p') if result.task_result else '',
            ])
        return json_data


class ResultsDetailView(DetailView):
    template_name = "gateway/results_detail.html"
    model = RequestLog
