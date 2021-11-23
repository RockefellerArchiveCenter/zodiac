from django.apps import AppConfig


class GatewayConfig(AppConfig):
    name = 'gateway'

    def ready(self):
        import gateway.signals
