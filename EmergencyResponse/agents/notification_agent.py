from twilio.rest import Client
from datetime import datetime
from .base_agent import BaseAgent
import os
from dotenv import load_dotenv
from geopy.distance import geodesic

load_dotenv()

class NotificationAgent(BaseAgent):
    def __init__(self):
        super().__init__("NotificationAgent")
        self.twilio_client = Client(
            os.getenv("TWILIO_ACCOUNT_SID"),
            os.getenv("TWILIO_AUTH_TOKEN")
        )
        self.twilio_number = os.getenv("TWILIO_PHONE_NUMBER")
        self.sms_radius = 25  # km
        self.call_radius = 10  # km
        self.notification_queue = []
        
        # Test users (in a real system, this would be in a database)
        self.test_users = [
            {
                "phone": "+18128227804",  # Test number for simulation
                "location": {"lat": 51.5074, "lon": -0.1278},
                "name": "Test User 1"
            }
        ]
        
    def process(self):
        """Process pending notifications"""
        try:
            self.update_status("Processing")
            while self.notification_queue:
                notification = self.notification_queue.pop(0)
                self._handle_notification(notification)
                
        except Exception as e:
            self.handle_error(e)
            
    def add_notification(self, notification_data):
        """Add a new notification to the queue"""
        self.notification_queue.append(notification_data)
        self.log_event("Queue", f"Added notification to queue. Queue size: {len(self.notification_queue)}")
        
    def _handle_notification(self, notification):
        """Process a single notification"""
        try:
            if notification["type"] == "weather_alert":
                self._handle_weather_alert(notification)
            elif notification["type"] == "crime_alert":
                self._handle_crime_alert(notification)
                
        except Exception as e:
            self.log_event("Error", f"Failed to process notification: {str(e)}")
            
    def _handle_weather_alert(self, alert_data):
        """Handle weather-related emergency notifications"""
        location = alert_data.get("location", {})
        affected_users = self._get_affected_users(location)
        
        for user in affected_users:
            distance = self._calculate_distance(location, user["location"])
            
            if distance <= self.call_radius:
                self._make_emergency_call(user)
            elif distance <= self.sms_radius:
                self._send_sms_alert(user, alert_data)
                
    def _handle_crime_alert(self, alert_data):
        """Handle crime-related emergency notifications"""
        location = alert_data.get("location", {})
        affected_users = self._get_affected_users(location)
        
        for user in affected_users:
            distance = self._calculate_distance(location, user["location"])
            
            if distance <= self.call_radius:
                self._make_emergency_call(user)
            elif distance <= self.sms_radius:
                self._send_sms_alert(user, alert_data)
        
    def _get_affected_users(self, location):
        """Get list of users in the affected area"""
        # For testing, return all test users
        return self.test_users
        
    def _calculate_distance(self, point1, point2):
        """Calculate distance between two points in kilometers"""
        return geodesic(
            (point1["lat"], point1["lon"]),
            (point2["lat"], point2["lon"])
        ).kilometers
        
    def _send_sms_alert(self, user, alert_data):
        """Send SMS alert to user"""
        try:
            message = self.twilio_client.messages.create(
                body=f"EMERGENCY ALERT: {alert_data['description']}",
                from_=self.twilio_number,
                to=user["phone"]
            )
            self.log_event("SMS", f"Sent SMS to {user['phone']}: {message.sid}")
        except Exception as e:
            self.log_event("Error", f"Failed to send SMS to {user['phone']}: {str(e)}")
            
    def _make_emergency_call(self, user):
        """Make emergency call to user"""
        try:
            call = self.twilio_client.calls.create(
                twiml='<Response><Say>Emergency alert. Please check your phone for details.</Say></Response>',
                from_=self.twilio_number,
                to=user["phone"]
            )
            self.log_event("Call", f"Made emergency call to {user['phone']}: {call.sid}")
        except Exception as e:
            self.log_event("Error", f"Failed to make call to {user['phone']}: {str(e)}")
            
    def get_state(self):
        """Get extended state information including queue size"""
        state = super().get_state()
        state.update({
            "queue_size": len(self.notification_queue),
            "sms_radius": self.sms_radius,
            "call_radius": self.call_radius
        })
        return state 