from django.urls import path
from . import views

app_name = 'iot_mock'

urlpatterns = [
    # Main temperature monitoring
    path('temp/', views.temperature_view, name='temperature'),
    path('', views.TemperatureMonitorView.as_view(), name='dashboard'),
    
    # System monitoring views
    path('dashboard/', views.system_dashboard, name='system_dashboard'),
    path('alerts/', views.alerts_view, name='alerts'),
    path('compliance/', views.compliance_report, name='compliance'),
    
    # AJAX endpoints for live updates
    path('ajax/temperature/', views.ajax_temperature_update, name='ajax_temperature'),
    path('ajax/historical/', views.ajax_historical_data, name='ajax_historical'),
    path('export/', views.export_data, name='export_data'),
    
    # Demo and testing
    path('simulate/', views.simulate_scenario, name='simulate_scenario'),
    
    # API endpoints
    path('api/locations/', views.api_location_list, name='api_locations'),
    path('api/temperature/<str:location_id>/', views.api_current_temperature, name='api_temperature'),
    path('api/historical/<str:location_id>/', views.api_historical_data, name='api_historical'),
    path('api/status/', views.api_system_status, name='api_status'),
]