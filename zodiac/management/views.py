from django.views.generic import TemplateView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.detail import DetailView
from django.views.generic.detail import BaseDetailView
from django.views.generic.list import ListView
from django.urls import reverse_lazy
from django_celery_results.models import TaskResult

from management.mixins import JSONResponseMixin

from gateway.models import Application, ServiceRegistry



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


class SplashView(TemplateView):
    template_name = "management/splash.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['recent_services'] = ServiceRegistry.objects.all().order_by('-modified_time')
        context['recent_systems'] = Application.objects.all().order_by('-modified_time')
        context['recent_results'] = TaskResult.objects.all().order_by('-date_done')
        return context


class ServicesAddView(CreateView):
    template_name = "management/services_add.html"
    model = ServiceRegistry
    fields = services_registry_fields


class ServicesListView(ListView):
    template_name = "management/services_list.html"
    model = ServiceRegistry


class ServicesDetailView(DetailView):
    template_name = "management/services_detail.html"
    model = ServiceRegistry


class ServicesUpdateView(UpdateView):
    template_name = "management/services_update.html"
    model = ServiceRegistry
    fields = services_registry_fields + ['is_active']


class ServicesDeleteView(DeleteView):
    template_name = "management/services_delete.html"
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
    template_name = "management/systems_add.html"
    model = Application
    fields = systems_update_fields


class SystemsDetailView(DetailView):
    template_name = "management/systems_detail.html"
    model = Application


class SystemsListView(ListView):
    template_name = "management/systems_list.html"
    model = Application


class SystemsUpdateView(UpdateView):
    template_name = "management/systems_update.html"
    model = Application
    fields = systems_update_fields + ['is_active']


class SystemsDeleteView(DeleteView):
    template_name = "management/systems_delete.html"
    model = Application
    success_url = reverse_lazy('systems-list')


class ResultsListView(ListView):
    template_name = "management/results_list.html"
    model = TaskResult


class ResultsDetailView(DetailView):
    template_name = "management/results_detail.html"
    model = TaskResult
