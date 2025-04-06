import logging
from datetime import datetime
import json

logger = logging.getLogger(__name__)

class MedicalEmergencyAgent:
    def __init__(self):
        self.status = "Monitoring"
        self.last_emergency = None
        self.active_emergencies = {}
        self.hospitals = {
            "hospital1": {
                "name": "City General Hospital",
                "location": {"lat": 51.5074, "lon": -0.1278},
                "capacity": {
                    "emergency_beds": 10,
                    "icu_beds": 5,
                    "operating_rooms": 3
                },
                "specialties": ["trauma", "cardiac", "stroke"]
            },
            "hospital2": {
                "name": "St. Mary's Hospital",
                "location": {"lat": 51.5200, "lon": -0.1300},
                "capacity": {
                    "emergency_beds": 8,
                    "icu_beds": 4,
                    "operating_rooms": 2
                },
                "specialties": ["pediatric", "cardiac", "orthopedic"]
            }
        }
    
    def process(self):
        """Process current medical emergencies"""
        try:
            self._update_hospital_status()
            self._process_active_emergencies()
            return True
        except Exception as e:
            logger.error(f"Error processing medical emergencies: {str(e)}")
            return False
    
    def _update_hospital_status(self):
        """Update real-time hospital capacity and status"""
        # In a real system, this would query hospital APIs
        for hospital_id, hospital in self.hospitals.items():
            # Simulate dynamic capacity changes
            hospital["status"] = self._calculate_hospital_status(hospital["capacity"])
    
    def _calculate_hospital_status(self, capacity):
        """Calculate hospital status based on capacity"""
        total_occupancy = sum(capacity.values()) / (len(capacity) * 10)  # Simulate occupancy
        if total_occupancy < 0.5:
            return "Normal"
        elif total_occupancy < 0.8:
            return "Busy"
        else:
            return "Critical"
    
    def _process_active_emergencies(self):
        """Process and update status of active medical emergencies"""
        current_time = datetime.now()
        completed_emergencies = []
        
        for emergency_id, emergency in self.active_emergencies.items():
            # Update emergency status based on time elapsed
            time_elapsed = (current_time - emergency["start_time"]).total_seconds() / 60
            
            if time_elapsed > emergency["estimated_duration"]:
                emergency["status"] = "completed"
                completed_emergencies.append(emergency_id)
            elif time_elapsed > emergency["estimated_duration"] * 0.5:
                emergency["status"] = "in_progress"
            
            # Log status updates
            logger.info(f"Medical Emergency {emergency_id}: {emergency['status']}")
        
        # Remove completed emergencies
        for emergency_id in completed_emergencies:
            del self.active_emergencies[emergency_id]
    
    def add_emergency(self, emergency_data):
        """Add a new medical emergency to be processed"""
        emergency_id = f"medical_{int(datetime.now().timestamp())}"
        emergency_data.update({
            "id": emergency_id,
            "start_time": datetime.now(),
            "status": "new",
            "estimated_duration": 30  # minutes
        })
        
        # Assign nearest suitable hospital
        nearest_hospital = self._find_nearest_suitable_hospital(
            emergency_data["location"],
            emergency_data.get("required_specialties", [])
        )
        
        if nearest_hospital:
            emergency_data["assigned_hospital"] = nearest_hospital
            self.active_emergencies[emergency_id] = emergency_data
            logger.info(f"New medical emergency {emergency_id} assigned to {nearest_hospital['name']}")
            return emergency_data
        else:
            logger.error("No suitable hospital found for medical emergency")
            return None
    
    def _find_nearest_suitable_hospital(self, location, required_specialties):
        """Find the nearest hospital that can handle the emergency"""
        suitable_hospitals = []
        
        for hospital in self.hospitals.values():
            if hospital["status"] != "Critical" and \
               all(specialty in hospital["specialties"] for specialty in required_specialties):
                # Calculate distance (in a real system, use actual distance calculation)
                distance = abs(location["lat"] - hospital["location"]["lat"]) + \
                          abs(location["lon"] - hospital["location"]["lon"])
                suitable_hospitals.append((distance, hospital))
        
        if suitable_hospitals:
            # Return the nearest suitable hospital
            return min(suitable_hospitals, key=lambda x: x[0])[1]
        return None
    
    def get_state(self):
        """Get current state of the medical emergency agent"""
        return {
            "status": self.status,
            "active_emergencies": len(self.active_emergencies),
            "last_emergency": self.last_emergency,
            "hospitals": {
                hospital_id: {
                    "name": hospital["name"],
                    "status": self._calculate_hospital_status(hospital["capacity"]),
                    "capacity": hospital["capacity"]
                }
                for hospital_id, hospital in self.hospitals.items()
            }
        } 