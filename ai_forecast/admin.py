from django.contrib import admin
from django.contrib.admin import AdminSite


# Since this app doesn't have models (demo purpose), 
# we'll register the admin interface for managing forecasting settings
# if needed in the future.

# Example of how you might add admin functionality for forecast settings:

# from django.contrib.admin import AdminSite
# from django.urls import path
# from django.shortcuts import render
# from django.http import HttpResponseRedirect
# from django.contrib import messages
# from .forecast_utils import DemandForecaster

class ForecastAdminSite(AdminSite):
    """Custom admin site for forecast management"""
    site_header = 'AI Forecast Administration'
    site_title = 'Forecast Admin'
    index_title = 'Manage Forecasting System'
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('forecast-status/', self.admin_view(self.forecast_status_view), 
                 name='forecast_status'),
            path('regenerate-data/', self.admin_view(self.regenerate_data_view), 
                 name='regenerate_data'),
        ]
        return custom_urls + urls
    
    def forecast_status_view(self, request):
        """View to show forecasting system status"""
        from .forecast_utils import DemandForecaster
        
        forecaster = DemandForecaster()
        context = {
            'title': 'Forecast System Status',
            'available_drugs': len(forecaster.drugs_data['drug_name'].unique()),
            'total_data_points': len(forecaster.drugs_data),
            'date_range': {
                'start': forecaster.drugs_data['date'].min(),
                'end': forecaster.drugs_data['date'].max()
            },
            'system_health': 'Healthy' if len(forecaster.drugs_data) > 1000 else 'Warning',
        }
        
        return render(request, 'admin/ai_forecast/forecast_status.html', context)
    
    def regenerate_data_view(self, request):
        """View to regenerate dummy data"""
        if request.method == 'POST':
            try:
                from .forecast_utils import DemandForecaster
                # This would regenerate the data in a real implementation
                messages.success(request, 'Forecast data regenerated successfully.')
            except Exception as e:
                messages.error(request, f'Error regenerating data: {str(e)}')
        
        return HttpResponseRedirect('../forecast-status/')

# Create custom admin site instance
forecast_admin_site = ForecastAdminSite(name='forecast_admin')

# Register any future models here
# Example:
# @admin.register(ForecastModel, site=forecast_admin_site)
# class ForecastModelAdmin(admin.ModelAdmin):
#     list_display = ['field1', 'field2']
#     search_fields = ['field1']

# Note: Since this app is model-less for demo purposes, 
# we don't have any models to register in the regular admin.
# The custom admin site above can be used for system management.