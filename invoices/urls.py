# invoices/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('create/', views.create_invoice_view, name='create_invoice'),
    path('<int:pk>/', views.invoice_detail_view, name='invoice_detail'),
    path('all-bills/', views.invoice_list, name='invoice_list'),
    path('daily-sales/', views.daily_sales_report, name='daily_sales_report'),
    path('send-owner-report/', views.send_simple_daily_report_email, name='send_owner_email_report_url'),
]
