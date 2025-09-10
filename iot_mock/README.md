# IoT Mock App - Cold Chain Monitoring

## Overview
The IoT Mock app simulates real-time temperature monitoring for cold chain storage of vaccines and temperature-sensitive medications. It provides realistic IoT sensor data, alerts, and compliance reporting for pharmaceutical inventory management.

## Features
- **Real-time Temperature Simulation**: Realistic temperature data with multiple scenarios
- **Multiple Storage Locations**: 4 different storage locations with unique characteristics
- **Smart Alert System**: Critical, warning, and info-level alerts with recommendations
- **Visual Thermometer Display**: Beautiful thermometer-style temperature indicators
- **Live Dashboard**: Real-time monitoring with auto-refresh capabilities
- **Compliance Reporting**: Detailed compliance analysis with export functionality
- **Historical Data**: Temperature history charts and trend analysis
- **System Health Monitoring**: Overall system reliability and health scores
- **API Endpoints**: RESTful API for external integrations
- **Scenario Simulation**: Manual scenario triggering for demos

## Storage Locations
1. **Main Vaccine Refrigerator** - Primary storage (500 vials capacity)
2. **Backup Cold Storage** - Emergency backup (200 vials capacity)  
3. **Mobile Transport Unit** - Delivery vehicle (50 vials capacity)
4. **Clinic Refrigerator** - Vaccination center (100 vials capacity)

## Temperature Scenarios
- **Normal Operation** (70% probability) - Stable temperatures within range
- **Minor Fluctuation** (15% probability) - Small temperature variations
- **Door Opening** (10% probability) - Temperature spikes from door access
- **Cooling Failure** (3% probability) - Equipment malfunction
- **Power Outage** (2% probability) - Complete system failure

## Installation

### 1. Add to Django Settings
```python
INSTALLED_APPS = [
    # ... other apps
    'iot_mock',
    'rest_framework',  # if not already included
]
```

### 2. URL Configuration
Include the app URLs in your main `urls.py`:
```python
from django.urls import path, include

urlpatterns = [
    # ... other patterns
    path('iot/', include('iot_mock.urls')),
]
```

### 3. Template Configuration
Ensure your base template (`base.html`) is properly configured.

## Usage

### Main Views
- `/iot/temp/` - Main temperature monitoring dashboard
- `/iot/dashboard/` - System-wide overview dashboard
- `/iot/alerts/` - Alerts and notifications center
- `/iot/compliance/` - Compliance reporting and analysis

### AJAX Endpoints
- `/iot/ajax/temperature/` - Live temperature updates
- `/iot/ajax/historical/` - Historical temperature data
- `/iot/export/` - Export temperature data as JSON

### API Endpoints
- `/iot/api/locations/` - List of all storage locations
- `/iot/api/temperature/<location_id>/` - Current temperature for location
- `/iot/api/historical/<location_id>/` - Historical data for location
- `/iot/api/status/` - Overall system status

### Demo Features
- `/iot/simulate/?scenario=<scenario_name>` - Trigger specific scenarios

## Temperature Simulation
The app generates realistic temperature data including:

### Safe Range
- **Minimum**: 2°C
- **Maximum**: 8°C  
- **Optimal**: 5°C

### Simulation Factors
- **Seasonal Patterns**: Natural temperature cycles
- **Time-based Fluctuations**: Daily temperature variations
- **Weekend Effects**: Lower activity on weekends
- **Equipment Malfunctions**: Random system failures
- **Environmental Factors**: Door openings, power issues

### Data Generation
- Readings generated every 15 minutes
- Realistic noise and variation
- Smoothing to prevent rapid changes
- Multiple scenario-based patterns

## Alert System

### Alert Levels
- **Critical** (Red) - Temperature outside 1-9°C range
- **Warning** (Yellow) - Temperature in 1-2°C or 8-9°C range  
- **Info** (Blue) - System notifications and maintenance

### Alert Types
- Temperature excursions
- System maintenance reminders
- Sensor calibration alerts
- Battery level warnings
- Communication issues

### Recommended Actions
Each alert includes specific recommended actions:
- Equipment checks
- Maintenance procedures
- Emergency protocols
- Escalation procedures

## Compliance Features

### Compliance Metrics
- Overall compliance rate percentage
- Safe vs. unsafe readings ratio
- Temperature excursion count
- Time-in-range statistics

### Reporting
- Detailed compliance reports
- Temperature history charts
- Excursion analysis
- Export capabilities (JSON, CSV, PDF)

### Audit Trail
- Complete temperature history
- Alert acknowledgments
- System status changes
- User actions log

## Customization

### Adding New Locations
Modify the `storage_locations` dictionary in `simulate_temp.py`:
```python
storage_locations = {
    'new_location': {
        'name': 'New Storage Unit',
        'location': 'Building C',
        'capacity': '300 vials',
        'reliability': 0.92,
        'base_temp': 4.0
    }
}
```

### Custom Temperature Ranges
Modify the temperature constants:
```python
self.safe_min = 2.0  # Your minimum safe temperature
self.safe_max = 8.0  # Your maximum safe temperature
```

### Adding New Scenarios
Add scenarios to the `scenarios` dictionary:
```python
scenarios = {
    'your_scenario': {
        'weight': 5, 
        'temp_drift': 3.0, 
        'malfunction_chance': 0.3
    }
}
```

## File Structure
```
iot_mock/
├── __init__.py
├── apps.py
├── admin.py
├── views.py
├── urls.py
├── simulate_temp.py          # Core simulation engine
├── README.md
├── templates/
│   └── iot_mock/
│       ├── temperature.html  # Main monitoring dashboard
│       ├── dashboard.html    # System overview
│       ├── alerts.html       # Alerts management
│       └── compliance.html   # Compliance reporting
```

## API Examples

### Get Current Temperature
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
     http://localhost:8000/iot/api/temperature/main_refrigerator/
```

### Get Historical Data
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
     "http://localhost:8000/iot/api/historical/main_refrigerator/?hours=24"
```

### Export Compliance Data
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
     "http://localhost:8000/iot/export/?location=main_refrigerator&hours=168" \
     -o compliance_data.json
```

### Trigger Demo Scenario
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
     "http://localhost:8000/iot/simulate/?scenario=cooling_failure&location=main_refrigerator"
```

## Security Features
- All views require authentication
- CSRF protection enabled
- Input validation and sanitization
- Rate limiting on API endpoints
- Secure session management

## Performance Considerations
- Efficient in-memory simulation
- Optimized chart rendering
- Minimal database queries (model-less design)
- Cached temperature calculations
- Lazy loading of historical data

## Browser Compatibility
- Modern browsers (Chrome, Firefox, Safari, Edge)
- Responsive design for mobile devices
- Progressive Web App features
- Offline capability for cached data

## Demo Scenarios
Perfect for hackathon demonstrations:

1. **Normal Operation**: Show stable monitoring
2. **Door Opening**: Demonstrate temperature spike alerts
3. **Cooling Failure**: Critical alert with recommendations
4. **System Recovery**: Show alert resolution
5. **Compliance Report**: Generate professional reports

## Future Enhancements
- Real IoT sensor integration
- Machine learning for predictive alerts
- Mobile app companion
- SMS/Email alert notifications
- Integration with inventory management
- Blockchain for audit trails
- Multi-tenant support
- Advanced analytics dashboard

## Support
For issues and feature requests, please contact the DrugTrack development team.

## License
Part of the DrugTrack project. See main project license for details.