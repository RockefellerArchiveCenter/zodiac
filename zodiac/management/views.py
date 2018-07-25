from django.views.generic import TemplateView


class SplashView(TemplateView):
    template_name = "management/splash.html"
