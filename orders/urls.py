from django.urls import path
from . import views

urlpatterns = [
    path('create/', views.create_order_view, name='create_order'),
    path('receipt/<int:order_id>/', views.order_receipt, name='order_receipt'),
    path('all_order/', views.order_list_view, name='order_list'),
    path('order/success/', views.order_success_view, name='order_success'),
    path('toggle-delivery/<int:order_id>/', views.toggle_delivery_status, name='toggle_delivery'), 
]
