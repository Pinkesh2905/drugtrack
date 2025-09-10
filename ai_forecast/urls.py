from django.urls import path
from . import views

app_name = 'ai_forecast'

urlpatterns = [
    # Main forecast dashboard
    path('', views.forecast_view, name='forecast'),
    path('dashboard/', views.ForecastDashboardView.as_view(), name='dashboard'),
    
    # Analytics and detailed views
    path('analytics/', views.forecast_analytics, name='analytics'),
    path('comparison/', views.forecast_comparison, name='comparison'),
    
    # AJAX endpoints
    path('ajax/chart/', views.ajax_forecast_chart, name='ajax_chart'),
    path('export/', views.export_forecast_data, name='export'),
    
    # API endpoints
    path('api/drugs/', views.api_drug_list, name='api_drugs'),
    path('api/forecast/<str:drug_name>/', views.api_forecast_data, name='api_forecast'),
    path('api/summary/', views.api_summary_stats, name='api_summary'),
]