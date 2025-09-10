from django.contrib import admin
from django.urls import path
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.contrib import messages

# Since this app doesn't have models (simulation purpose), 
# we'll register the admin interface for managing IoT settings
# and simulation parameters if needed in the future.

class IoTAdminSite(admin.AdminSite):
    """Custom admin site for IoT monitoring management"""
    site_header = 'IoT Cold Chain Administration'
    site_title = 'IoT Admin'
    index_title = 'Manage IoT Monitoring System'
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('iot-status/', self.admin_view(self.iot_status_view), 
                 name='iot_status'),
            path('simulation-settings/', self.admin_view(self.simulation_settings_view), 
                 name='simulation_settings'),
            path('reset-simulation/', self.admin_view(self.reset_simulation_view), 
                 name='reset_simulation'),
        ]
        return custom_urls + urls
    
    def iot_status_view(self, request):
        """View to show IoT system status"""
        from .simulate_temp import temperature_simulator
        
        # Get system overview
        system_summary = temperature_simulator.get_system_summary()
        all_locations = temperature_simulator.get_all_locations_status()
        alerts = temperature_simulator.simulate_alert_conditions()
        
        context = {
            'title': 'IoT System Status',
            'system_summary': system_summary,
            'all_locations': all_locations,
            'alerts': alerts,
            'total_locations': len(temperature_simulator.storage_locations),
            'simulation_scenarios': list(temperature_simulator.scenarios.keys()),
            'current_scenario': temperature_simulator.current_scenario,
        }
        
        return render(request, 'admin/iot_mock/iot_status.html', context)
    
    def simulation_settings_view(self, request):
        """View to manage simulation settings"""
        from .simulate_temp import temperature_simulator
        
        if request.method == 'POST':
            try:
                scenario = request.POST.get('scenario')
                if scenario in temperature_simulator.scenarios:
                    temperature_simulator.current_scenario = scenario
                    temperature_simulator.scenario_start_time = __import__('time').time()
                    messages.success(request, f'Simulation scenario changed to "{scenario}"')
                else:
                    messages.error(request, 'Invalid scenario selected')
            except Exception as e:
                messages.error(request, f'Error updating simulation: {str(e)}')
        
        context = {
            'title': 'Simulation Settings',
            'scenarios': temperature_simulator.scenarios,
            'current_scenario': temperature_simulator.current_scenario,
            'storage_locations': temperature_simulator.storage_locations,
        }
        
        return render(request, 'admin/iot_mock/simulation_settings.html', context)
    
    def reset_simulation_view(self, request):
        """View to reset simulation to default state"""
        if request.method == 'POST':
            try:
                from .simulate_temp import temperature_simulator
                
                # Reset to normal scenario
                temperature_simulator.current_scenario = 'normal'
                temperature_simulator.last_temp = temperature_simulator.optimal_temp
                temperature_simulator.scenario_start_time = __import__('time').time()
                
                messages.success(request, 'Simulation reset to normal operating conditions')
            except Exception as e:
                messages.error(request, f'Error resetting simulation: {str(e)}')
        
        return HttpResponseRedirect('../iot-status/')

# Create custom admin site instance
iot_admin_site = IoTAdminSite(name='iot_admin')

# Note: Since this app is model-less for simulation purposes, 
# we don't have any models to register in the regular admin.
# The custom admin site above can be used for system management.

# If you want to add this to the main admin, you could create
# a simple admin configuration:

class IoTSystemConfig(admin.ModelAdmin):
    """
    Placeholder admin configuration for IoT system management.
    This would be used if we had actual models to manage.
    """
    pass

# Example of how you might register future models:
# @admin.register(TemperatureSensor, site=iot_admin_site)
# class TemperatureSensorAdmin(admin.ModelAdmin):
#     list_display = ['location', 'current_temperature', 'status', 'last_updated']
#     list_filter = ['status', 'location']
#     search_fields = ['location']
#     readonly_fields = ['last_updated']

# Add custom admin views to main Django admin if needed
from django.contrib.admin import site as admin_site

def iot_dashboard_view(request):
    """Simple IoT dashboard for main admin"""
    from .simulate_temp import temperature_simulator
    
    context = {
        'title': 'IoT Monitoring Dashboard',
        'system_summary': temperature_simulator.get_system_summary(),
        'locations_count': len(temperature_simulator.storage_locations),
        'app_label': 'iot_mock',
    }
    
    return render(request, 'admin/iot_mock/dashboard_simple.html', context)

# You can add this view to main admin by registering a custom admin view
# This is optional and would require additional URL configuration