from django.urls import path, re_path

from . import views

urlpatterns = [
    re_path('api/.+', views.Gateway.as_view(), name='gateway'),

    path('', views.SplashView.as_view(), name='dashboard'),

    # SERVICES URLS
    path('services/', views.ServicesListView.as_view(), name='services-list'),
    path('services/<int:pk>/', views.ServicesDetailView.as_view(), name='services-detail'),
    path('services/<int:pk>.json', views.ServicesJSONView.as_view(), name='services-json'),
    path('services/edit/<int:pk>/', views.ServicesUpdateView.as_view(), name='services-update'),
    path('services/add/', views.ServicesAddView.as_view(), name='services-add'),
    path('services/delete/<int:pk>/', views.ServicesDeleteView.as_view(), name='services-delete'),
    path('services/trigger/<int:pk>/', views.ServicesTriggerView.as_view(), name='services-trigger'),
    path('services/clear-errors/<int:pk>/', views.ServicesClearErrorsView.as_view(), name='services-clear-errors'),

    # APPLICATIONS URLS
    path('applications/', views.ApplicationsListView.as_view(), name='applications-list'),
    path('applications/<int:pk>/', views.ApplicationsDetailView.as_view(), name='applications-detail'),
    path('applications/edit/<int:pk>/', views.ApplicationsUpdateView.as_view(), name='applications-update'),
    path('applications/add/', views.ApplicationsAddView.as_view(), name='applications-add'),
    path('applications/delete/<int:pk>/', views.ApplicationsDeleteView.as_view(), name='applications-delete'),

    # SOURCES URLS
    path('sources/', views.SourcesListView.as_view(), name='sources-list'),
    path('sources/<int:pk>/', views.SourcesDetailView.as_view(), name='sources-detail'),
    path('sources/edit/<int:pk>/', views.SourcesUpdateView.as_view(), name='sources-update'),
    path('sources/add/', views.SourcesAddView.as_view(), name='sources-add'),
    path('sources/delete/<int:pk>/', views.SourcesDeleteView.as_view(), name='sources-delete'),

    # USERS URLS
    path('users/', views.UsersListView.as_view(), name='users-list'),
    path('users/<int:pk>/', views.UsersDetailView.as_view(), name='users-detail'),
    path('users/edit/<int:pk>/', views.UsersUpdateView.as_view(), name='users-update'),
    path('users/add/', views.UsersAddView.as_view(), name='users-add'),
    path('users/delete/<int:pk>/', views.UsersDeleteView.as_view(), name='users-delete'),

    # RESULTS URLS
    path('results/', views.ResultsListView.as_view(), name='results-list'),
    path('results-data/', views.ResultsDatatableView.as_view(), name='results-data'),
    path('results/<int:pk>/', views.ResultsDetailView.as_view(), name='results-detail'),
]
