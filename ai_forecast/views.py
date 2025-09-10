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

from .forecast_utils import DemandForecaster


class ForecastDashboardView(LoginRequiredMixin, TemplateView):
    """Main forecast dashboard view"""
    template_name = 'ai_forecast/forecast.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        forecaster = DemandForecaster()
        
        # Get available drugs
        available_drugs = sorted(forecaster.drugs_data['drug_name'].unique().tolist())
        
        # Get summary statistics
        summary_stats = forecaster.get_summary_statistics()
        
        # Get top drugs by demand
        top_drugs = forecaster.get_top_drugs_by_demand(5)
        
        # Default drug for initial chart
        default_drug = available_drugs[0] if available_drugs else None
        chart_data = None
        forecast_data = None
        
        if default_drug:
            chart_data = forecaster.create_forecast_chart(default_drug)
            forecast_data = forecaster.forecast_demand(default_drug, 90)
        
        context.update({
            'available_drugs': available_drugs,
            'summary_stats': summary_stats,
            'top_drugs': top_drugs,
            'default_drug': default_drug,
            'chart_data': chart_data,
            'forecast_data': forecast_data,
            'page_title': 'AI Demand Forecasting',
            'breadcrumb': 'Forecasting'
        })
        
        return context


@login_required
def forecast_view(request):
    """Function-based view for forecast dashboard"""
    forecaster = DemandForecaster()
    
    # Get available drugs
    available_drugs = sorted(forecaster.drugs_data['drug_name'].unique().tolist())
    
    # Get summary statistics
    summary_stats = forecaster.get_summary_statistics()
    
    # Get top drugs by demand
    top_drugs = forecaster.get_top_drugs_by_demand(5)
    
    # Default drug for initial display
    selected_drug = request.GET.get('drug', available_drugs[0] if available_drugs else None)
    
    chart_data = None
    forecast_data = None
    
    if selected_drug:
        chart_data = forecaster.create_forecast_chart(selected_drug)
        forecast_data = forecaster.forecast_demand(selected_drug, 90)
    
    context = {
        'available_drugs': available_drugs,
        'selected_drug': selected_drug,
        'summary_stats': summary_stats,
        'top_drugs': top_drugs,
        'chart_data': chart_data,
        'forecast_data': forecast_data,
        'page_title': 'AI Demand Forecasting',
        'breadcrumb': 'Forecasting'
    }
    
    return render(request, 'ai_forecast/forecast.html', context)


@login_required
def ajax_forecast_chart(request):
    """AJAX endpoint to get forecast chart for a specific drug"""
    drug_name = request.GET.get('drug')
    
    if not drug_name:
        return JsonResponse({'error': 'Drug name is required'}, status=400)
    
    forecaster = DemandForecaster()
    
    # Check if drug exists
    available_drugs = forecaster.drugs_data['drug_name'].unique().tolist()
    if drug_name not in available_drugs:
        return JsonResponse({'error': 'Drug not found'}, status=404)
    
    # Generate forecast and chart
    forecast_data = forecaster.forecast_demand(drug_name, 90)
    chart_data = forecaster.create_forecast_chart(drug_name)
    
    return JsonResponse({
        'chart_data': chart_data,
        'forecast_data': forecast_data,
        'drug_name': drug_name
    })


@login_required
def forecast_analytics(request):
    """View for detailed analytics"""
    forecaster = DemandForecaster()
    
    # Get comprehensive analytics
    summary_stats = forecaster.get_summary_statistics()
    top_drugs = forecaster.get_top_drugs_by_demand(10)
    
    # Calculate overall trends
    total_demand = sum(stats['total_demand_last_year'] for stats in summary_stats.values())
    avg_volatility = sum(stats['demand_volatility'] for stats in summary_stats.values()) / len(summary_stats)
    
    # Identify high-growth drugs
    high_growth_drugs = [
        drug for drug, stats in summary_stats.items() 
        if stats['monthly_growth_rate'] > 5
    ]
    
    # Identify high-volatility drugs (potential stockout risk)
    high_risk_drugs = [
        drug for drug, stats in summary_stats.items() 
        if stats['demand_volatility'] > avg_volatility * 1.5
    ]
    
    context = {
        'summary_stats': summary_stats,
        'top_drugs': top_drugs,
        'total_demand': total_demand,
        'avg_volatility': round(avg_volatility, 2),
        'high_growth_drugs': high_growth_drugs,
        'high_risk_drugs': high_risk_drugs,
        'total_drugs': len(summary_stats),
        'page_title': 'Forecast Analytics',
        'breadcrumb': 'Analytics'
    }
    
    return render(request, 'ai_forecast/analytics.html', context)


# API Views for external access
@api_view(['GET'])
def api_forecast_data(request, drug_name):
    """API endpoint to get forecast data for a specific drug"""
    forecaster = DemandForecaster()
    
    # Validate drug exists
    available_drugs = forecaster.drugs_data['drug_name'].unique().tolist()
    if drug_name not in available_drugs:
        return Response({'error': 'Drug not found'}, status=status.HTTP_404_NOT_FOUND)
    
    # Get forecast parameters
    days = int(request.GET.get('days', 90))
    days = min(max(days, 7), 365)  # Limit between 7 and 365 days
    
    forecast_data = forecaster.forecast_demand(drug_name, days)
    
    return Response({
        'status': 'success',
        'data': forecast_data
    })


@api_view(['GET'])
def api_drug_list(request):
    """API endpoint to get list of available drugs"""
    forecaster = DemandForecaster()
    available_drugs = sorted(forecaster.drugs_data['drug_name'].unique().tolist())
    
    return Response({
        'status': 'success',
        'drugs': available_drugs,
        'count': len(available_drugs)
    })


@api_view(['GET'])
def api_summary_stats(request):
    """API endpoint to get summary statistics for all drugs"""
    forecaster = DemandForecaster()
    summary_stats = forecaster.get_summary_statistics()
    top_drugs = forecaster.get_top_drugs_by_demand(5)
    
    return Response({
        'status': 'success',
        'summary_statistics': summary_stats,
        'top_drugs': top_drugs
    })


@login_required
def export_forecast_data(request):
    """Export forecast data as JSON"""
    drug_name = request.GET.get('drug')
    
    if not drug_name:
        return JsonResponse({'error': 'Drug name is required'}, status=400)
    
    forecaster = DemandForecaster()
    
    # Get comprehensive data
    forecast_data = forecaster.forecast_demand(drug_name, 90)
    historical_data = forecaster.get_historical_data(drug_name)
    
    # Prepare export data
    export_data = {
        'drug_name': drug_name,
        'export_timestamp': forecaster.drugs_data['date'].max().isoformat(),
        'forecast': forecast_data,
        'historical_summary': {
            'total_records': len(historical_data),
            'date_range': {
                'start': historical_data['date'].min().isoformat(),
                'end': historical_data['date'].max().isoformat()
            },
            'demand_stats': {
                'mean': float(historical_data['demand'].mean()),
                'std': float(historical_data['demand'].std()),
                'min': int(historical_data['demand'].min()),
                'max': int(historical_data['demand'].max())
            }
        }
    }
    
    return JsonResponse(export_data, json_dumps_params={'indent': 2})


@login_required
def forecast_comparison(request):
    """Compare forecasts for multiple drugs"""
    selected_drugs = request.GET.getlist('drugs')
    
    if not selected_drugs:
        # Default to top 3 drugs
        forecaster = DemandForecaster()
        top_drugs = forecaster.get_top_drugs_by_demand(3)
        selected_drugs = [drug['drug_name'] for drug in top_drugs]
    
    # Limit to max 5 drugs for comparison
    selected_drugs = selected_drugs[:5]
    
    forecaster = DemandForecaster()
    comparison_data = {}
    
    for drug in selected_drugs:
        forecast_data = forecaster.forecast_demand(drug, 30)  # 30 days for comparison
        comparison_data[drug] = {
            'forecast_avg': sum(forecast_data['forecast_values']) / len(forecast_data['forecast_values']),
            'historical_avg': sum(forecast_data['historical_values'][-30:]) / len(forecast_data['historical_values'][-30:]),
            'trend': 'increasing' if forecast_data['forecast_values'][-1] > forecast_data['forecast_values'][0] else 'decreasing'
        }
    
    context = {
        'selected_drugs': selected_drugs,
        'comparison_data': comparison_data,
        'available_drugs': sorted(forecaster.drugs_data['drug_name'].unique().tolist()),
        'page_title': 'Forecast Comparison',
        'breadcrumb': 'Comparison'
    }
    
    return render(request, 'ai_forecast/comparison.html', context)