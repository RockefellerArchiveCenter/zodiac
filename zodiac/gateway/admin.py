from django.contrib import admin
from .models import ServiceRegistry, Consumer, Application, RequestLog

admin.site.register(Application)
admin.site.register(ServiceRegistry)
admin.site.register(Consumer)
admin.site.register(RequestLog)