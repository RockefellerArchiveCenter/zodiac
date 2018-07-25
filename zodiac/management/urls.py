from django.urls import path

from . import views

urlpatterns = [
    path('', views.SplashView.as_view(), name='dashboard'),
]