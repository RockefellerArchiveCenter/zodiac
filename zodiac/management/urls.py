from django.urls import path

from . import views

urlpatterns = [
    path('', views.SplashView.as_view(), name='dashboard'),

    # SERVICES URLS
    path('services/', views.ServicesListView.as_view(), name='services-list'),
    path('services/<int:pk>/', views.ServicesDetailView.as_view(), name='services-detail'),
    path('services/edit/<int:pk>/', views.ServicesUpdateView.as_view(), name='services-update'),
    path('services/add/', views.ServicesAddView.as_view(), name='services-add'),
    path('services/edit/<int:pk>/delete/', views.ServicesDeleteView.as_view(), name='services-delete'),
    path('services/trigger/<int:pk>/', views.ServicesTriggerView.as_view(), name='services-trigger'),
    path('services/async_results/<int:pk>/', views.ServicesASyncResultsView.as_view(), name='services-async-results'),

    # SYSTEMS URLS
    path('systems/', views.SystemsListView.as_view(), name='systems-list'),
    path('systems/<int:pk>/', views.SystemsDetailView.as_view(), name='systems-detail'),
    path('systems/edit/<int:pk>/', views.SystemsUpdateView.as_view(), name='systems-update'),
    path('systems/add/', views.SystemsAddView.as_view(), name='systems-add'),
    path('systems/edit/<int:pk>/delete/', views.SystemsDeleteView.as_view(), name='systems-delete'),

    # RESULTS URLS
    path('results/', views.ResultsListView.as_view(), name='results-list'),
    path('results/<int:pk>/', views.ResultsDetailView.as_view(), name='results-detail'),
]
