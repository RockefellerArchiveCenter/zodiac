from django.contrib import admin

from .models import Application, RequestLog, ServiceRegistry, Source

admin.site.register(Application)
admin.site.register(ServiceRegistry)
admin.site.register(Source)
admin.site.register(RequestLog)
