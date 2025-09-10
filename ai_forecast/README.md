# AI Forecast App

## Overview
The AI Forecast app is part of the DrugTrack project, providing demand forecasting capabilities for pharmaceutical inventory management. This app uses machine learning to predict drug demand patterns and help optimize inventory levels.

## Features
- **Demand Forecasting**: Uses linear regression to predict future drug demand
- **Interactive Dashboards**: Visual charts showing historical and predicted demand
- **Drug Comparison**: Side-by-side comparison of multiple drugs
- **Analytics Dashboard**: Comprehensive statistics and insights
- **Risk Assessment**: Identifies high-volatility drugs that may cause stockouts
- **Growth Analysis**: Tracks drugs with increasing/decreasing demand trends
- **API Endpoints**: RESTful API for external integrations
- **Export Functionality**: Download forecast data as JSON

## Installation

### 1. Install Dependencies
```bash
pip install pandas numpy scikit-learn matplotlib seaborn djangorestframework
```

### 2. Add to Django Settings
Add the app to your `INSTALLED_APPS`:
```python
INSTALLED_APPS = [
    # ... other apps
    'ai_forecast',
    'rest_framework',  # if not already included
]
```

### 3. URL Configuration
Include the app URLs in your main `urls.py`:
```python
from django.urls import path, include

urlpatterns = [
    # ... other patterns
    path('forecast/', include('ai_forecast.urls')),
]
```

### 4. Template Configuration
Ensure your base template (`base.html`) is properly configured in your main templates directory.

## Usage

### Main Views
- `/forecast/` - Main forecasting dashboard
- `/forecast/analytics/` - Detailed analytics and statistics
- `/forecast/comparison/` - Compare multiple drugs
- `/forecast/ajax/chart/` - AJAX endpoint for chart updates

### API Endpoints
- `/forecast/api/drugs/` - List of available drugs
- `/forecast/api/forecast/<drug_name>/` - Get forecast data for specific drug
- `/forecast/api/summary/` - Summary statistics for all drugs

### Template Tags
The app includes custom template tags for enhanced functionality:
```html
{% load forecast_extras %}

<!-- Dictionary lookup -->
{{ my_dict|lookup:"key_name" }}

<!-- Sum list values -->
{{ my_list|add_values }}

<!-- Generate random number -->
{% random 10 100 %}

<!-- Metric card widget -->
{% metric_card "Total Demand" 1500 "Units" icon="fas fa-pills" color="success" %}
```

## Data Generation
The app generates realistic dummy data including:
- 8 different pharmaceutical drugs
- 12 months of historical daily demand data
- Seasonal patterns (higher demand during winter months)
- Growth trends (some drugs growing, others declining)
- Weekend effects (lower demand on weekends)
- Random noise for realistic variation

## Machine Learning Model
- **Algorithm**: Linear Regression with feature scaling
- **Features**: Days since start, day of year, weekend indicator
- **Training**: Uses 12 months of historical data
- **Prediction**: Forecasts next 90 days with confidence intervals
- **Accuracy**: Model provides R² score for accuracy assessment

## Customization

### Adding New Drugs
Modify the `_generate_dummy_data()` method in `forecast_utils.py`:
```python
drugs = {
    'YourNewDrug': {'base_demand': 500, 'seasonality': 0.2, 'trend': 0.01},
    # ... existing drugs
}
```

### Changing Forecast Period
Modify the default forecast period in views:
```python
forecast_data = forecaster.forecast_demand(drug_name, 30)  # 30 days instead of 90
```

### Custom Styling
Override the CSS classes in your templates:
```css
.forecast-card {
    /* Your custom styles */
}
```

## File Structure
```
ai_forecast/
├── __init__.py
├── apps.py
├── admin.py
├── views.py
├── urls.py
├── forecast_utils.py
├── requirements.txt
├── README.md
├── templates/
│   └── ai_forecast/
│       ├── forecast.html
│       ├── analytics.html
│       ├── comparison.html
│       └── widgets/
│           ├── metric_card.html
│           └── trend_indicator.html
└── templatetags/
    ├── __init__.py
    └── forecast_extras.py
```

## API Examples

### Get Drug List
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
     http://localhost:8000/forecast/api/drugs/
```

### Get Forecast Data
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
     "http://localhost:8000/forecast/api/forecast/Paracetamol/?days=30"
```

### Export Forecast Data
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
     "http://localhost:8000/forecast/export/?drug=Insulin" \
     -o insulin_forecast.json
```

## Security Notes
- All views require authentication (`@login_required`)
- API endpoints should use proper authentication tokens
- CSRF protection is enabled for form submissions
- Input validation prevents SQL injection and XSS

## Performance Considerations
- Data is generated in-memory for demo purposes
- For production, implement database caching
- Consider using Celery for background forecast generation
- Implement pagination for large datasets

## Future Enhancements
- Integration with real pharmaceutical data sources
- More advanced ML models (Prophet, ARIMA, Neural Networks)
- Real-time data updates via WebSockets
- Mobile-responsive progressive web app
- Integration with inventory management systems
- Automated email alerts for stock recommendations

## Support
For issues and feature requests, please contact the DrugTrack development team.