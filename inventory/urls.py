from django.urls import path
from . import views

app_name = 'inventory'

urlpatterns = [
    # Main inventory views
    path('add/', views.add_batch, name='add_batch'),
    path('list/', views.list_batches, name='list_batches'),
    
    # The URL for the verification form (handles POST and initial GET)
    path('verify/', views.verify_drug, name='verify_drug'),
    
    # The URL for showing the verification result for a specific batch
    path('verify/<str:batch_number>/', views.verify_drug, name='verify_drug_detail'),
    
    # Batch detail and management
    path('batch/<uuid:batch_id>/', views.batch_detail, name='batch_detail'),
    path('batch/<uuid:batch_id>/delete/', views.delete_batch, name='delete_batch'),
    path('export/expired-csv/', views.export_expired_csv, name='export_expired_csv'),
    path('alert/all-expired/', views.alert_all_expired, name='alert_all_expired'),
    
    path('analytics/', views.analytics_view, name='analytics'),
    
    # API endpoints
    path('api/verify-qr/', views.api_verify_qr, name='api_verify_qr'),
    path('api/stats/', views.inventory_stats, name='inventory_stats'),
    
    # Default redirect to list view
    path('', views.list_batches, name='index'),
]
