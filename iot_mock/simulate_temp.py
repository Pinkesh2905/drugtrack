import random
import time
import math
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import json

class ColdChainSimulator:
    """
    Simulates IoT temperature monitoring for vaccine cold chain
    Generates realistic temperature data with various scenarios
    """
    
    def __init__(self):
        self.safe_min = 2.0  # Minimum safe temperature (°C)
        self.safe_max = 8.0  # Maximum safe temperature (°C)
        self.optimal_temp = 5.0  # Optimal storage temperature (°C)
        
        # Simulation scenarios
        self.scenarios = {
            'normal': {'weight': 70, 'temp_drift': 0.5, 'malfunction_chance': 0},
            'minor_fluctuation': {'weight': 15, 'temp_drift': 1.5, 'malfunction_chance': 0.1},
            'door_opening': {'weight': 10, 'temp_drift': 2.5, 'malfunction_chance': 0.2},
            'cooling_failure': {'weight': 3, 'temp_drift': 4.0, 'malfunction_chance': 0.8},
            'power_outage': {'weight': 2, 'temp_drift': 8.0, 'malfunction_chance': 0.9}
        }
        
        # Storage locations with different characteristics
        self.storage_locations = {
            'main_refrigerator': {
                'name': 'Main Vaccine Refrigerator',
                'location': 'Pharmacy Storage Room A',
                'capacity': '500 vials',
                'reliability': 0.95,
                'base_temp': 4.5
            },
            'backup_fridge': {
                'name': 'Backup Cold Storage',
                'location': 'Emergency Storage Room B',
                'capacity': '200 vials',
                'reliability': 0.90,
                'base_temp': 3.5
            },
            'transport_cooler': {
                'name': 'Mobile Transport Unit',
                'location': 'Delivery Vehicle #3',
                'capacity': '50 vials',
                'reliability': 0.85,
                'base_temp': 6.0
            },
            'clinic_fridge': {
                'name': 'Clinic Refrigerator',
                'location': 'Vaccination Center',
                'capacity': '100 vials',
                'reliability': 0.88,
                'base_temp': 5.5
            }
        }
        
        # Current simulation state
        self.current_scenario = 'normal'
        self.last_temp = self.optimal_temp
        self.scenario_start_time = time.time()
        self.scenario_duration = random.randint(300, 1800)  # 5-30 minutes
    
    def _select_scenario(self) -> str:
        """Select a scenario based on weighted probabilities"""
        total_weight = sum(scenario['weight'] for scenario in self.scenarios.values())
        random_value = random.randint(1, total_weight)
        
        cumulative_weight = 0
        for scenario_name, scenario_data in self.scenarios.items():
            cumulative_weight += scenario_data['weight']
            if random_value <= cumulative_weight:
                return scenario_name
        
        return 'normal'
    
    def _calculate_temperature(self, location_id: str = 'main_refrigerator') -> float:
        """Calculate realistic temperature based on current scenario"""
        current_time = time.time()
        
        # Check if we need to change scenario
        if current_time - self.scenario_start_time > self.scenario_duration:
            self.current_scenario = self._select_scenario()
            self.scenario_start_time = current_time
            self.scenario_duration = random.randint(300, 1800)
        
        # Get location and scenario data
        location = self.storage_locations.get(location_id, self.storage_locations['main_refrigerator'])
        scenario = self.scenarios[self.current_scenario]
        
        # Base temperature for this location
        base_temp = location['base_temp']
        
        # Add time-based fluctuation (simulates natural temperature cycles)
        time_factor = math.sin(current_time / 600) * 0.3  # 10-minute cycle
        
        # Add scenario-specific drift
        temp_drift = random.uniform(-scenario['temp_drift'], scenario['temp_drift'])
        
        # Add small random noise
        noise = random.uniform(-0.2, 0.2)
        
        # Calculate new temperature
        new_temp = base_temp + time_factor + temp_drift + noise
        
        # Apply some smoothing to prevent rapid changes
        smoothing_factor = 0.7
        new_temp = (self.last_temp * smoothing_factor) + (new_temp * (1 - smoothing_factor))
        
        # Check for malfunction
        if random.random() < scenario['malfunction_chance']:
            # Simulate equipment malfunction
            malfunction_temp = random.uniform(-5, 25)  # Extreme temperatures
            new_temp = malfunction_temp
        
        # Update last temperature
        self.last_temp = new_temp
        
        return round(new_temp, 1)
    
    def get_current_reading(self, location_id: str = 'main_refrigerator') -> Dict:
        """Get current temperature reading with full context"""
        temperature = self._calculate_temperature(location_id)
        location = self.storage_locations[location_id]
        
        # Determine status
        if self.safe_min <= temperature <= self.safe_max:
            status = 'safe'
            status_text = 'SAFE'
            alert_level = 'success'
        elif self.safe_min - 1 <= temperature < self.safe_min or self.safe_max < temperature <= self.safe_max + 1:
            status = 'warning'
            status_text = 'WARNING'
            alert_level = 'warning'
        else:
            status = 'unsafe'
            status_text = 'CRITICAL'
            alert_level = 'danger'
        
        # Calculate time in current range
        time_in_range = random.randint(5, 180)  # 5 minutes to 3 hours
        
        return {
            'location_id': location_id,
            'location_name': location['name'],
            'location_details': location['location'],
            'capacity': location['capacity'],
            'temperature': temperature,
            'status': status,
            'status_text': status_text,
            'alert_level': alert_level,
            'safe_min': self.safe_min,
            'safe_max': self.safe_max,
            'optimal_temp': self.optimal_temp,
            'current_scenario': self.current_scenario.replace('_', ' ').title(),
            'timestamp': datetime.now(),
            'time_in_current_range': time_in_range,
            'reliability_score': int(location['reliability'] * 100),
            'humidity': round(random.uniform(45, 75), 1),  # Typical humidity range
            'battery_level': random.randint(75, 100) if status != 'unsafe' else random.randint(10, 50)
        }
    
    def get_historical_data(self, location_id: str = 'main_refrigerator', hours: int = 24) -> List[Dict]:
        """Generate historical temperature data for charts"""
        historical_data = []
        current_time = datetime.now()
        
        # Generate data points every 15 minutes for the specified period
        intervals = hours * 4  # 4 intervals per hour
        
        # Temporarily store current state
        original_temp = self.last_temp
        original_scenario = self.current_scenario
        
        for i in range(intervals, 0, -1):
            # Calculate time for this data point
            point_time = current_time - timedelta(minutes=15 * i)
            
            # Generate temperature for this time point
            temp = self._calculate_temperature(location_id)
            
            # Determine status
            if self.safe_min <= temp <= self.safe_max:
                status = 'safe'
            elif self.safe_min - 1 <= temp < self.safe_min or self.safe_max < temp <= self.safe_max + 1:
                status = 'warning'
            else:
                status = 'unsafe'
            
            historical_data.append({
                'timestamp': point_time.strftime('%Y-%m-%d %H:%M:%S'),
                'temperature': temp,
                'status': status,
                'formatted_time': point_time.strftime('%H:%M')
            })
        
        # Restore original state
        self.last_temp = original_temp
        self.current_scenario = original_scenario
        
        return historical_data
    
    def get_all_locations_status(self) -> List[Dict]:
        """Get current status for all storage locations"""
        all_locations = []
        
        for location_id in self.storage_locations.keys():
            reading = self.get_current_reading(location_id)
            all_locations.append(reading)
        
        return all_locations
    
    def get_system_summary(self) -> Dict:
        """Get overall system health summary"""
        all_readings = self.get_all_locations_status()
        
        total_locations = len(all_readings)
        safe_count = sum(1 for r in all_readings if r['status'] == 'safe')
        warning_count = sum(1 for r in all_readings if r['status'] == 'warning')
        unsafe_count = sum(1 for r in all_readings if r['status'] == 'unsafe')
        
        avg_temp = sum(r['temperature'] for r in all_readings) / total_locations
        avg_reliability = sum(r['reliability_score'] for r in all_readings) / total_locations
        
        # System health score
        health_score = (safe_count * 100 + warning_count * 60 + unsafe_count * 0) / total_locations
        
        if health_score >= 90:
            system_status = 'excellent'
            system_status_text = 'Excellent'
            system_alert_level = 'success'
        elif health_score >= 70:
            system_status = 'good'
            system_status_text = 'Good'
            system_alert_level = 'info'
        elif health_score >= 50:
            system_status = 'warning'
            system_status_text = 'Needs Attention'
            system_alert_level = 'warning'
        else:
            system_status = 'critical'
            system_status_text = 'Critical'
            system_alert_level = 'danger'
        
        return {
            'total_locations': total_locations,
            'safe_count': safe_count,
            'warning_count': warning_count,
            'unsafe_count': unsafe_count,
            'average_temperature': round(avg_temp, 1),
            'average_reliability': round(avg_reliability, 1),
            'health_score': round(health_score, 1),
            'system_status': system_status,
            'system_status_text': system_status_text,
            'system_alert_level': system_alert_level,
            'last_updated': datetime.now(),
            'active_alerts': unsafe_count + warning_count
        }
    
    def simulate_alert_conditions(self) -> List[Dict]:
        """Generate alert conditions for demonstration"""
        alerts = []
        
        # Temperature alerts
        all_readings = self.get_all_locations_status()
        for reading in all_readings:
            if reading['status'] in ['warning', 'unsafe']:
                alert_type = 'Temperature Alert' if reading['status'] == 'warning' else 'Critical Temperature Alert'
                alerts.append({
                    'id': f"temp_{reading['location_id']}_{int(time.time())}",
                    'type': alert_type,
                    'location': reading['location_name'],
                    'message': f"Temperature {reading['temperature']}°C is outside safe range ({self.safe_min}°C - {self.safe_max}°C)",
                    'severity': reading['alert_level'],
                    'timestamp': datetime.now(),
                    'acknowledged': False,
                    'recommended_action': self._get_recommended_action(reading)
                })
        
        # Add some system alerts occasionally
        if random.random() < 0.3:  # 30% chance
            system_alerts = [
                {
                    'id': f"sys_maintenance_{int(time.time())}",
                    'type': 'Maintenance Reminder',
                    'location': 'System Wide',
                    'message': 'Scheduled maintenance check due for temperature sensors',
                    'severity': 'info',
                    'timestamp': datetime.now(),
                    'acknowledged': False,
                    'recommended_action': 'Schedule maintenance check with technician'
                },
                {
                    'id': f"sys_calibration_{int(time.time())}",
                    'type': 'Calibration Check',
                    'location': 'Main Refrigerator',
                    'message': 'Temperature sensor calibration recommended',
                    'severity': 'warning',
                    'timestamp': datetime.now(),
                    'acknowledged': False,
                    'recommended_action': 'Perform sensor calibration check'
                }
            ]
            alerts.extend(random.sample(system_alerts, 1))
        
        return alerts
    
    def _get_recommended_action(self, reading: Dict) -> str:
        """Get recommended action based on reading status"""
        if reading['status'] == 'unsafe':
            if reading['temperature'] > self.safe_max:
                return "IMMEDIATE ACTION: Check cooling system, verify door seal, move vaccines to backup storage if needed"
            else:
                return "IMMEDIATE ACTION: Check for freezing, adjust temperature settings, inspect ventilation"
        elif reading['status'] == 'warning':
            return "Monitor closely, check door seals, verify temperature calibration"
        else:
            return "Continue normal monitoring"
    
    def export_temperature_log(self, location_id: str = 'main_refrigerator', hours: int = 24) -> Dict:
        """Export temperature log data for compliance"""
        historical_data = self.get_historical_data(location_id, hours)
        current_reading = self.get_current_reading(location_id)
        
        # Calculate compliance statistics
        total_readings = len(historical_data)
        safe_readings = sum(1 for data in historical_data if data['status'] == 'safe')
        compliance_rate = (safe_readings / total_readings) * 100 if total_readings > 0 else 0
        
        # Find temperature excursions
        excursions = [data for data in historical_data if data['status'] in ['warning', 'unsafe']]
        
        return {
            'export_info': {
                'location': current_reading['location_name'],
                'location_id': location_id,
                'export_timestamp': datetime.now().isoformat(),
                'period_hours': hours,
                'total_readings': total_readings
            },
            'compliance_summary': {
                'compliance_rate': round(compliance_rate, 2),
                'safe_readings': safe_readings,
                'warning_readings': sum(1 for data in historical_data if data['status'] == 'warning'),
                'unsafe_readings': sum(1 for data in historical_data if data['status'] == 'unsafe'),
                'temperature_excursions': len(excursions)
            },
            'temperature_data': historical_data,
            'excursion_details': excursions,
            'current_status': current_reading
        }

# Global simulator instance
temperature_simulator = ColdChainSimulator()