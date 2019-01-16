from django.contrib import admin
from .models import ServiceRegistry, Source, Application, RequestLog

admin.site.register(Application)
admin.site.register(ServiceRegistry)
admin.site.register(Source)
admin.site.register(RequestLog)
