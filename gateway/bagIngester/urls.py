from django.conf.urls import url
from . import tests
from . import views
from . import ingester

urlpatterns = [
    url(r'^$', views.handler, name='handler'),
    url(r'^tests', tests.test, name='tests'),
    url(r'^ingester', ingester.sendBag, name='transform'),
]
