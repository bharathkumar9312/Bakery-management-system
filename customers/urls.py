from django.urls import path
from . import views

urlpatterns = [
    path('', views.customers_list, name='customers_list'),
    path('add/', views.customers_create, name='customers_create'), 
    path('delete/<int:pk>/', views.customers_delete, name='customers_delete'),
    path('api/search/', views.customer_search_api, name='customer-search-api'),
]