import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
import io
import base64
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Tuple
import json

# Set style for better looking charts
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

class DemandForecaster:
    def __init__(self):
        self.model = LinearRegression()
        self.scaler = StandardScaler()
        self.drugs_data = self._generate_dummy_data()
    
    def _generate_dummy_data(self) -> pd.DataFrame:
        """Generate realistic dummy drug demand data for the past 12 months"""
        
        # Define common drugs with different demand patterns
        drugs = {
            'Paracetamol': {'base_demand': 1000, 'seasonality': 0.3, 'trend': 0.02},
            'Insulin': {'base_demand': 500, 'seasonality': 0.1, 'trend': 0.01},
            'Amoxicillin': {'base_demand': 800, 'seasonality': 0.4, 'trend': -0.01},
            'Aspirin': {'base_demand': 600, 'seasonality': 0.2, 'trend': 0.005},
            'Omeprazole': {'base_demand': 400, 'seasonality': 0.15, 'trend': 0.03},
            'Metformin': {'base_demand': 700, 'seasonality': 0.1, 'trend': 0.02},
            'Atorvastatin': {'base_demand': 350, 'seasonality': 0.12, 'trend': 0.015},
            'Cough Syrup': {'base_demand': 300, 'seasonality': 0.6, 'trend': 0.01},
        }
        
        # Generate dates for past 12 months
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365)
        date_range = pd.date_range(start=start_date, end=end_date, freq='D')
        
        all_data = []
        
        for drug_name, params in drugs.items():
            for date in date_range:
                # Create realistic demand with seasonality and trend
                day_of_year = date.timetuple().tm_yday
                seasonal_factor = 1 + params['seasonality'] * np.sin(2 * np.pi * day_of_year / 365)
                
                # Add trend
                days_since_start = (date - start_date).days
                trend_factor = 1 + params['trend'] * (days_since_start / 365)
                
                # Add some random noise
                noise_factor = np.random.normal(1, 0.1)
                
                # Weekend effect (lower demand on weekends)
                weekend_factor = 0.7 if date.weekday() >= 5 else 1.0
                
                demand = int(params['base_demand'] * seasonal_factor * trend_factor * noise_factor * weekend_factor)
                demand = max(0, demand)  # Ensure non-negative
                
                all_data.append({
                    'date': date,
                    'drug_name': drug_name,
                    'demand': demand,
                    'month': date.strftime('%Y-%m'),
                    'week_day': date.strftime('%A')
                })
        
        return pd.DataFrame(all_data)
    
    def get_historical_data(self, drug_name: str = None) -> pd.DataFrame:
        """Get historical demand data for a specific drug or all drugs"""
        if drug_name:
            return self.drugs_data[self.drugs_data['drug_name'] == drug_name].copy()
        return self.drugs_data.copy()
    
    def forecast_demand(self, drug_name: str, forecast_days: int = 90) -> Dict:
        """Forecast demand for a specific drug for the next N days"""
        
        # Get historical data for the drug
        drug_data = self.get_historical_data(drug_name)
        if drug_data.empty:
            return {"error": f"No data found for drug: {drug_name}"}
        
        # Prepare data for training
        drug_data = drug_data.sort_values('date')
        drug_data['days_since_start'] = (drug_data['date'] - drug_data['date'].min()).dt.days
        drug_data['day_of_year'] = drug_data['date'].dt.dayofyear
        drug_data['is_weekend'] = drug_data['date'].dt.weekday >= 5
        
        # Features for the model
        features = ['days_since_start', 'day_of_year', 'is_weekend']
        X = drug_data[features]
        y = drug_data['demand']
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        # Train the model
        self.model.fit(X_scaled, y)
        
        # Generate future dates
        last_date = drug_data['date'].max()
        future_dates = pd.date_range(start=last_date + timedelta(days=1), periods=forecast_days, freq='D')
        
        # Prepare future features
        future_data = []
        start_date = drug_data['date'].min()
        
        for date in future_dates:
            future_data.append({
                'date': date,
                'days_since_start': (date - start_date).days,
                'day_of_year': date.timetuple().tm_yday,
                'is_weekend': date.weekday() >= 5
            })
        
        future_df = pd.DataFrame(future_data)
        X_future = future_df[features]
        X_future_scaled = self.scaler.transform(X_future)
        
        # Make predictions
        predictions = self.model.predict(X_future_scaled)
        predictions = np.maximum(predictions, 0)  # Ensure non-negative
        
        # Calculate confidence intervals (simple approach)
        residuals = y - self.model.predict(X_scaled)
        std_residuals = np.std(residuals)
        confidence_upper = predictions + 1.96 * std_residuals
        confidence_lower = np.maximum(predictions - 1.96 * std_residuals, 0)
        
        return {
            'drug_name': drug_name,
            'forecast_dates': future_dates.tolist(),
            'forecast_values': predictions.tolist(),
            'confidence_upper': confidence_upper.tolist(),
            'confidence_lower': confidence_lower.tolist(),
            'historical_dates': drug_data['date'].tolist(),
            'historical_values': drug_data['demand'].tolist(),
            'model_score': self.model.score(X_scaled, y)
        }
    
    def get_summary_statistics(self) -> Dict:
        """Get summary statistics for all drugs"""
        summary = {}
        
        for drug in self.drugs_data['drug_name'].unique():
            drug_data = self.get_historical_data(drug)
            
            # Calculate monthly averages for trend analysis
            monthly_avg = drug_data.groupby('month')['demand'].mean()
            
            summary[drug] = {
                'total_demand_last_year': int(drug_data['demand'].sum()),
                'average_daily_demand': round(drug_data['demand'].mean(), 2),
                'max_demand': int(drug_data['demand'].max()),
                'min_demand': int(drug_data['demand'].min()),
                'demand_volatility': round(drug_data['demand'].std(), 2),
                'recent_month_avg': round(monthly_avg.iloc[-1], 2) if not monthly_avg.empty else 0,
                'previous_month_avg': round(monthly_avg.iloc[-2], 2) if len(monthly_avg) > 1 else 0,
            }
            
            # Calculate growth rate
            if summary[drug]['previous_month_avg'] > 0:
                growth_rate = ((summary[drug]['recent_month_avg'] - summary[drug]['previous_month_avg']) / 
                              summary[drug]['previous_month_avg']) * 100
                summary[drug]['monthly_growth_rate'] = round(growth_rate, 2)
            else:
                summary[drug]['monthly_growth_rate'] = 0
        
        return summary
    
    def create_forecast_chart(self, drug_name: str) -> str:
        """Create a forecast chart and return as base64 string"""
        forecast_data = self.forecast_demand(drug_name, 90)
        
        if 'error' in forecast_data:
            return None
        
        plt.figure(figsize=(14, 8))
        
        # Plot historical data
        historical_dates = pd.to_datetime(forecast_data['historical_dates'])
        plt.plot(historical_dates[-90:], forecast_data['historical_values'][-90:], 
                'o-', label='Historical Demand', linewidth=2, markersize=4)
        
        # Plot forecast
        forecast_dates = pd.to_datetime(forecast_data['forecast_dates'])
        plt.plot(forecast_dates, forecast_data['forecast_values'], 
                'r--', label='Forecasted Demand', linewidth=2)
        
        # Plot confidence intervals
        plt.fill_between(forecast_dates, 
                        forecast_data['confidence_lower'], 
                        forecast_data['confidence_upper'], 
                        alpha=0.3, color='red', label='Confidence Interval')
        
        plt.title(f'Demand Forecast for {drug_name}', fontsize=16, fontweight='bold')
        plt.xlabel('Date', fontsize=12)
        plt.ylabel('Daily Demand (Units)', fontsize=12)
        plt.legend(fontsize=10)
        plt.grid(True, alpha=0.3)
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        # Add model accuracy text
        plt.text(0.02, 0.98, f"Model Accuracy: {forecast_data['model_score']:.3f}", 
                transform=plt.gca().transAxes, fontsize=10, 
                bbox=dict(boxstyle="round", facecolor='wheat', alpha=0.8),
                verticalalignment='top')
        
        # Convert to base64
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
        buffer.seek(0)
        chart_data = base64.b64encode(buffer.getvalue()).decode()
        plt.close()
        
        return chart_data
    
    def get_top_drugs_by_demand(self, top_n: int = 5) -> List[Dict]:
        """Get top N drugs by total demand"""
        drug_totals = self.drugs_data.groupby('drug_name')['demand'].sum().sort_values(ascending=False)
        
        top_drugs = []
        for i, (drug, total_demand) in enumerate(drug_totals.head(top_n).items()):
            recent_data = self.get_historical_data(drug).tail(30)
            avg_recent = recent_data['demand'].mean()
            
            top_drugs.append({
                'rank': i + 1,
                'drug_name': drug,
                'total_annual_demand': int(total_demand),
                'average_daily_demand': round(avg_recent, 2),
                'percentage_of_total': round((total_demand / drug_totals.sum()) * 100, 2)
            })
        
        return top_drugs