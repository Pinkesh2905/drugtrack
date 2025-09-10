from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import json
from datetime import datetime

from .simulate_temp import temperature_simulator


class TemperatureMonitorView(LoginRequiredMixin, TemplateView):
    """Main temperature monitoring dashboard"""
    template_name = 'iot_mock/temperature.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get selected location or default
        location_id = self.request.GET.get('location', 'main_refrigerator')
        
        # Get current temperature reading
        current_reading = temperature_simulator.get_current_reading(location_id)
        
        # Get historical data for chart
        historical_data = temperature_simulator.get_historical_data(location_id, 24)
        
        # Get all locations for selector
        all_locations = temperature_simulator.get_all_locations_status()
        
        # Get system summary
        system_summary = temperature_simulator.get_system_summary()
        
        # Get alerts
        alerts = temperature_simulator.simulate_alert_conditions()
        
        context.update({
            'current_reading': current_reading,
            'historical_data': historical_data,
            'all_locations': all_locations,
            'system_summary': system_summary,
            'alerts': alerts,
            'selected_location': location_id,
            'available_locations': temperature_simulator.storage_locations,
            'page_title': 'Cold Chain Monitoring',
            'breadcrumb': 'Temperature Monitoring'
        })
        
        return context


@login_required
def temperature_view(request):
    """Function-based temperature monitoring view"""
    # Get selected location or default
    location_id = request.GET.get('location', 'main_refrigerator')
    
    # Get current temperature reading
    current_reading = temperature_simulator.get_current_reading(location_id)
    
    # Get historical data for chart
    historical_data = temperature_simulator.get_historical_data(location_id, 24)
    
    # Get all locations for selector
    all_locations = temperature_simulator.get_all_locations_status()
    
    # Get system summary
    system_summary = temperature_simulator.get_system_summary()
    
    # Get alerts
    alerts = temperature_simulator.simulate_alert_conditions()
    
    context = {
        'current_reading': current_reading,
        'historical_data': historical_data,
        'all_locations': all_locations,
        'system_summary': system_summary,
        'alerts': alerts,
        'selected_location': location_id,
        'available_locations': temperature_simulator.storage_locations,
        'page_title': 'Cold Chain Monitoring',
        'breadcrumb': 'Temperature Monitoring'
    }
    
    return render(request, 'iot_mock/temperature.html', context)


@login_required
def ajax_temperature_update(request):
    """AJAX endpoint for live temperature updates"""
    location_id = request.GET.get('location', 'main_refrigerator')
    
    try:
        # Get fresh reading
        current_reading = temperature_simulator.get_current_reading(location_id)
        
        return JsonResponse({
            'status': 'success',
            'data': current_reading
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)


@login_required
def ajax_historical_data(request):
    """AJAX endpoint for historical temperature data"""
    location_id = request.GET.get('location', 'main_refrigerator')
    hours = int(request.GET.get('hours', 24))
    
    try:
        historical_data = temperature_simulator.get_historical_data(location_id, hours)
        
        return JsonResponse({
            'status': 'success',
            'data': historical_data,
            'location': location_id,
            'hours': hours
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)


@login_required
def system_dashboard(request):
    """System-wide monitoring dashboard"""
    system_summary = temperature_simulator.get_system_summary()
    all_locations = temperature_simulator.get_all_locations_status()
    alerts = temperature_simulator.simulate_alert_conditions()
    
    # Calculate additional statistics
    total_capacity = sum(
        int(loc['capacity'].split()[0]) for loc in all_locations 
        if loc['capacity'].split()[0].isdigit()
    )
    
    # Get historical data for all locations (last 6 hours for overview)
    location_trends = {}
    for location_id in temperature_simulator.storage_locations.keys():
        recent_data = temperature_simulator.get_historical_data(location_id, 6)
        if recent_data:
            latest_temps = [data['temperature'] for data in recent_data[-4:]]  # Last hour
            avg_temp = sum(latest_temps) / len(latest_temps)
            trend = 'stable'
            if len(latest_temps) >= 2:
                if latest_temps[-1] > latest_temps[-2] + 0.5:
                    trend = 'rising'
                elif latest_temps[-1] < latest_temps[-2] - 0.5:
                    trend = 'falling'
            
            location_trends[location_id] = {
                'avg_temp': round(avg_temp, 1),
                'trend': trend
            }
    
    context = {
        'system_summary': system_summary,
        'all_locations': all_locations,
        'alerts': alerts,
        'location_trends': location_trends,
        'total_capacity': total_capacity,
        'page_title': 'System Dashboard',
        'breadcrumb': 'System Overview'
    }
    
    return render(request, 'iot_mock/dashboard.html', context)


@login_required
def alerts_view(request):
    """Alerts and notifications view"""
    alerts = temperature_simulator.simulate_alert_conditions()
    system_summary = temperature_simulator.get_system_summary()
    
    # Group alerts by severity
    critical_alerts = [alert for alert in alerts if alert['severity'] == 'danger']
    warning_alerts = [alert for alert in alerts if alert['severity'] == 'warning']
    info_alerts = [alert for alert in alerts if alert['severity'] == 'info']
    
    context = {
        'all_alerts': alerts,
        'critical_alerts': critical_alerts,
        'warning_alerts': warning_alerts,
        'info_alerts': info_alerts,
        'system_summary': system_summary,
        'page_title': 'Alerts & Notifications',
        'breadcrumb': 'Alerts'
    }
    
    return render(request, 'iot_mock/alerts.html', context)


@login_required
def compliance_report(request):
    """Compliance and reporting view"""
    location_id = request.GET.get('location', 'main_refrigerator')
    hours = int(request.GET.get('hours', 24))
    
    # Export compliance data
    compliance_data = temperature_simulator.export_temperature_log(location_id, hours)
    
    context = {
        'compliance_data': compliance_data,
        'selected_location': location_id,
        'selected_hours': hours,
        'available_locations': temperature_simulator.storage_locations,
        'page_title': 'Compliance Report',
        'breadcrumb': 'Compliance'
    }
    
    return render(request, 'iot_mock/compliance.html', context)


@login_required
def export_data(request):
    """Export temperature data as JSON"""
    location_id = request.GET.get('location', 'main_refrigerator')
    hours = int(request.GET.get('hours', 24))
    
    try:
        export_data = temperature_simulator.export_temperature_log(location_id, hours)
        
        return JsonResponse(export_data, json_dumps_params={'indent': 2})
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)


# API Views for external access
@api_view(['GET'])
def api_current_temperature(request, location_id):
    """API endpoint for current temperature"""
    try:
        if location_id not in temperature_simulator.storage_locations:
            return Response({
                'error': 'Location not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        reading = temperature_simulator.get_current_reading(location_id)
        
        return Response({
            'status': 'success',
            'data': reading
        })
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def api_location_list(request):
    """API endpoint for available locations"""
    try:
        locations = []
        for location_id, location_data in temperature_simulator.storage_locations.items():
            current_reading = temperature_simulator.get_current_reading(location_id)
            locations.append({
                'id': location_id,
                'name': location_data['name'],
                'location': location_data['location'],
                'capacity': location_data['capacity'],
                'current_temperature': current_reading['temperature'],
                'status': current_reading['status']
            })
        
        return Response({
            'status': 'success',
            'locations': locations,
            'count': len(locations)
        })
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def api_historical_data(request, location_id):
    """API endpoint for historical temperature data"""
    try:
        if location_id not in temperature_simulator.storage_locations:
            return Response({
                'error': 'Location not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        hours = int(request.GET.get('hours', 24))
        hours = min(max(hours, 1), 168)  # Limit between 1 hour and 1 week
        
        historical_data = temperature_simulator.get_historical_data(location_id, hours)
        
        return Response({
            'status': 'success',
            'location_id': location_id,
            'hours': hours,
            'data': historical_data
        })
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def api_system_status(request):
    """API endpoint for system status"""
    try:
        system_summary = temperature_simulator.get_system_summary()
        alerts = temperature_simulator.simulate_alert_conditions()
        
        return Response({
            'status': 'success',
            'system_summary': system_summary,
            'active_alerts': len(alerts),
            'alerts': alerts
        })
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@login_required
def simulate_scenario(request):
    """Manually trigger specific scenarios for demo"""
    scenario = request.GET.get('scenario', 'normal')
    
    # Valid scenarios
    valid_scenarios = list(temperature_simulator.scenarios.keys())
    
    if scenario not in valid_scenarios:
        return JsonResponse({
            'status': 'error',
            'message': f'Invalid scenario. Valid options: {valid_scenarios}'
        }, status=400)
    
    # Force the scenario
    temperature_simulator.current_scenario = scenario
    temperature_simulator.scenario_start_time = __import__('time').time()
    
    # Get updated reading
    location_id = request.GET.get('location', 'main_refrigerator')
    current_reading = temperature_simulator.get_current_reading(location_id)
    
    return JsonResponse({
        'status': 'success',
        'message': f'Scenario "{scenario}" activated',
        'current_reading': current_reading
    })