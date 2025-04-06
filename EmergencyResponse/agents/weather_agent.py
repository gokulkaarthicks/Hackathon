import requests
import time
from datetime import datetime
from .base_agent import BaseAgent
import os
from dotenv import load_dotenv
import logging

load_dotenv()

logger = logging.getLogger(__name__)

class WeatherAgent(BaseAgent):
    def __init__(self):
        super().__init__("WeatherAgent")
        self.api_key = os.getenv("OPENWEATHER_API_KEY")
        self.base_url = "http://api.openweathermap.org/data/2.5"
        self.monitoring_interval = 300  # 5 minutes
        self.last_check = None
        self.alert_thresholds = {
            "wind_speed": 50,  # km/h
            "precipitation": 25,  # mm/h
            "temperature": 35  # °C
        }
        self.status = "Idle"
        self.last_update = None
        self.current_conditions = {}
        self.alerts = []
        
    def process(self):
        """Main processing loop for weather monitoring"""
        try:
            self.update_status("Monitoring")
            weather_data = self._fetch_weather_data()
            
            if self._check_severe_conditions(weather_data):
                self._trigger_alert(weather_data)
                
            self.last_check = datetime.now()
            self.log_event("Weather Check", f"Completed weather check at {self.last_check}")
            
        except Exception as e:
            self.handle_error(e)
            
    def _fetch_weather_data(self):
        """Fetch current weather data from OpenWeather API"""
        params = {
            "q": "London,UK",  # Example location, should be configurable
            "appid": self.api_key,
            "units": "metric"
        }
        
        response = requests.get(f"{self.base_url}/weather", params=params)
        response.raise_for_status()
        return response.json()
    
    def _check_severe_conditions(self, weather_data):
        """Check if current weather conditions meet alert thresholds"""
        wind_speed = weather_data.get("wind", {}).get("speed", 0)
        precipitation = weather_data.get("rain", {}).get("1h", 0)
        temperature = weather_data.get("main", {}).get("temp", 0)
        
        return (
            wind_speed > self.alert_thresholds["wind_speed"] or
            precipitation > self.alert_thresholds["precipitation"] or
            temperature > self.alert_thresholds["temperature"]
        )
    
    def _trigger_alert(self, weather_data):
        """Trigger emergency alert for severe weather conditions"""
        alert_data = {
            "type": "weather_alert",
            "timestamp": datetime.now().isoformat(),
            "conditions": {
                "wind_speed": weather_data.get("wind", {}).get("speed"),
                "precipitation": weather_data.get("rain", {}).get("1h"),
                "temperature": weather_data.get("main", {}).get("temp"),
                "description": weather_data.get("weather", [{}])[0].get("description")
            }
        }
        
        self.log_event("Alert", f"Weather alert triggered: {alert_data}")
        # Here we would notify other agents through a message queue or event system
        return alert_data
    
    def get_state(self):
        """Get the current state of the weather agent"""
        return {
            "status": self.status,
            "last_update": self.last_update.isoformat() if self.last_update else datetime.now().isoformat(),
            "current_conditions": self.current_conditions,
            "alerts": self.alerts
        }
        
    def process_alert(self, alert_data):
        """Process a weather alert"""
        try:
            # Update agent status
            self.status = "Processing"
            
            # Add alert to alerts list
            self.alerts.append(alert_data)
            
            # Update current conditions based on alert
            if "storm" in alert_data["description"].lower():
                self.current_conditions["precipitation"] = "heavy"
                self.current_conditions["wind_speed"] = "high"
            elif "tornado" in alert_data["description"].lower():
                self.current_conditions["precipitation"] = "heavy"
                self.current_conditions["wind_speed"] = "extreme"
                self.current_conditions["conditions"] = "tornado"
            
            # Update last update time
            self.last_update = datetime.now()
            
            # Log the alert
            logger.info(f"Weather alert processed: {alert_data['description']}")
            
            # Return success
            return True
        except Exception as e:
            logger.error(f"Error processing weather alert: {str(e)}")
            self.status = "Error"
            return False 