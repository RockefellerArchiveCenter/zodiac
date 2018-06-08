from django.conf.urls import include, url
from django.contrib import admin

urlpatterns = [
    url(r'^bagIngester/', include('bagIngester.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^bagit/', include('gateway.urls', namespace='bagit')),
    url(r'^aurora/', include('gateway.urls', namespace='aurora')),
]
