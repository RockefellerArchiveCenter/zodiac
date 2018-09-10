from django.urls import path

from . import views

urlpatterns = [
    path('', views.SplashView.as_view(), name='dashboard'),
    path('services/add/', views.ServicesAddView.as_view(), name='services-add'),
    path('systems/', views.SystemsListView.as_view(), name='systems-list'),
    path('systems/add/', views.SystemsAddView.as_view(), name='systems-add'),
]
