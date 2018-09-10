from django.urls import path, re_path

from . import views

urlpatterns = [
	re_path('.+', views.Gateway.as_view(), name='gateway'),
]