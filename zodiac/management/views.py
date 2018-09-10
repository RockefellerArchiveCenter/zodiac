from django.views.generic import TemplateView


class SplashView(TemplateView):
    template_name = "management/splash.html"


class ServicesAddView(TemplateView):
    template_name = "management/services_add.html"


class SystemsListView(TemplateView):
    template_name = "management/systems_list.html"


class SystemsAddView(TemplateView):
    template_name = "management/systems_add.html"
