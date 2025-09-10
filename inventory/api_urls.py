from django.urls import path
from . import api_views

app_name = 'inventory_api'

urlpatterns = [
    # Drug batch CRUD operations
    path('batches/', api_views.DrugBatchListCreateAPIView.as_view(), name='batch_list_create'),
    path('batches/<uuid:id>/', api_views.DrugBatchDetailAPIView.as_view(), name='batch_detail'),
    
    # Verification endpoints
    path('verify/', api_views.verify_drug_api, name='verify_drug'),
    path('verify-qr/', api_views.verify_qr_api, name='verify_qr'),
    
    # Statistics and alerts
    path('stats/', api_views.inventory_stats_api, name='inventory_stats'),
    path('low-stock/', api_views.low_stock_alerts_api, name='low_stock_alerts'),
    path('expiry-alerts/', api_views.expiry_alerts_api, name='expiry_alerts'),
]