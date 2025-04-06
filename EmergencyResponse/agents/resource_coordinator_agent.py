import logging
from datetime import datetime
import json
import random  # For simulation purposes

logger = logging.getLogger(__name__)

class ResourceCoordinatorAgent:
    def __init__(self):
        self.status = "Active"
        self.dispatched_resources = {}
        self.available_resources = {
            "police_units": [
                {"id": "p1", "type": "patrol", "status": "available", "location": {"lat": 51.5074, "lon": -0.1278}},
                {"id": "p2", "type": "patrol", "status": "available", "location": {"lat": 51.5080, "lon": -0.1280}},
                {"id": "p3", "type": "swat", "status": "available", "location": {"lat": 51.5085, "lon": -0.1285}}
            ],
            "ambulances": [
                {"id": "a1", "type": "basic", "status": "available", "location": {"lat": 51.5074, "lon": -0.1278}},
                {"id": "a2", "type": "advanced", "status": "available", "location": {"lat": 51.5080, "lon": -0.1280}},
                {"id": "a3", "type": "basic", "status": "available", "location": {"lat": 51.5085, "lon": -0.1285}}
            ],
            "fire_trucks": [
                {"id": "f1", "type": "engine", "status": "available", "location": {"lat": 51.5074, "lon": -0.1278}},
                {"id": "f2", "type": "ladder", "status": "available", "location": {"lat": 51.5080, "lon": -0.1280}},
                {"id": "f3", "type": "rescue", "status": "available", "location": {"lat": 51.5085, "lon": -0.1285}}
            ],
            "hospitals": [
                {
                    "id": "h1",
                    "name": "City General Hospital",
                    "location": {"lat": 51.5074, "lon": -0.1278},
                    "capacity": {"emergency": 10, "icu": 5},
                    "specialties": ["trauma", "cardiac"]
                },
                {
                    "id": "h2",
                    "name": "St. Mary's Hospital",
                    "location": {"lat": 51.5090, "lon": -0.1290},
                    "capacity": {"emergency": 8, "icu": 4},
                    "specialties": ["pediatric", "burns"]
                }
            ],
            "fire_hydrants": [
                {"id": "h1", "status": "operational", "location": {"lat": 51.5074, "lon": -0.1278}},
                {"id": "h2", "status": "operational", "location": {"lat": 51.5080, "lon": -0.1280}},
                {"id": "h3", "status": "maintenance", "location": {"lat": 51.5085, "lon": -0.1285}}
            ]
        }
    
    def process(self):
        """Process resource coordination tasks"""
        try:
            self._update_resource_status()
            self._optimize_resource_distribution()
            return True
        except Exception as e:
            logger.error(f"Error processing resource coordination: {str(e)}")
            return False
    
    def coordinate_emergency_response(self, emergency_data):
        """Coordinate resources for an emergency response"""
        emergency_id = emergency_data["id"]
        emergency_type = emergency_data["type"]
        location = emergency_data["location"]
        severity = emergency_data.get("severity", "medium")
        
        # Determine required resources based on emergency type and severity
        required_resources = self._determine_required_resources(emergency_type, severity)
        
        # Find and dispatch nearest available resources
        dispatched = {}
        for resource_type, count in required_resources.items():
            resources = self.get_nearest_resources(resource_type, location, count)
            if resources:
                dispatched[resource_type] = resources
                # Update resource status
                for resource in resources:
                    self._update_resource_status_to_dispatched(resource_type, resource["id"], emergency_id)
        
        # Store dispatch information
        self.dispatched_resources[emergency_id] = {
            "emergency_data": emergency_data,
            "resources": dispatched,
            "dispatch_time": datetime.now(),
            "status": "active"
        }
        
        logger.info(f"Resources dispatched for emergency {emergency_id}: {json.dumps(dispatched, indent=2)}")
        return dispatched
    
    def _determine_required_resources(self, emergency_type, severity):
        """Determine required resources based on emergency type and severity"""
        base_requirements = {
            "weather_alert": {
                "police_units": 1,
                "ambulances": 1
            },
            "crime_alert": {
                "police_units": 2
            },
            "fire_alert": {
                "fire_trucks": 2,
                "ambulances": 1
            },
            "medical_alert": {
                "ambulances": 1
            }
        }
        
        # Get base requirements for the emergency type
        requirements = base_requirements.get(emergency_type, {}).copy()
        
        # Adjust based on severity
        if severity == "high":
            for resource_type in requirements:
                requirements[resource_type] = requirements[resource_type] * 2
        elif severity == "critical":
            for resource_type in requirements:
                requirements[resource_type] = requirements[resource_type] * 3
        
        return requirements
    
    def get_nearest_resources(self, resource_type, location, count=1):
        """Find nearest available resources of a specific type"""
        if resource_type not in self.available_resources:
            return []
        
        # Filter available resources
        available = [
            r for r in self.available_resources[resource_type]
            if isinstance(r, dict) and r.get("status") == "available"
        ]
        
        # Calculate distances and sort
        resources_with_distance = []
        for resource in available:
            distance = self._calculate_distance(location, resource["location"])
            resources_with_distance.append((distance, resource))
        
        # Sort by distance and return the nearest ones
        resources_with_distance.sort(key=lambda x: x[0])
        return [r[1] for r in resources_with_distance[:count]]
    
    def _calculate_distance(self, location1, location2):
        """Calculate distance between two locations"""
        # In a real system, use proper distance calculation
        return abs(location1["lat"] - location2["lat"]) + \
               abs(location1["lon"] - location2["lon"])
    
    def _update_resource_status_to_dispatched(self, resource_type, resource_id, emergency_id):
        """Update resource status to dispatched"""
        for resource in self.available_resources[resource_type]:
            if isinstance(resource, dict) and resource.get("id") == resource_id:
                resource["status"] = "dispatched"
                resource["emergency_id"] = emergency_id
                break
    
    def _update_resource_status(self):
        """Update status of all resources"""
        current_time = datetime.now()
        completed_emergencies = []
        
        for emergency_id, dispatch_data in self.dispatched_resources.items():
            # Check if emergency response is complete
            time_elapsed = (current_time - dispatch_data["dispatch_time"]).total_seconds() / 60
            
            if time_elapsed > 60:  # Simulate 1-hour response time
                # Mark emergency as complete
                dispatch_data["status"] = "completed"
                completed_emergencies.append(emergency_id)
                
                # Free up resources
                for resource_type, resources in dispatch_data["resources"].items():
                    for resource in resources:
                        if isinstance(resource, dict) and "id" in resource:
                            self._free_resource(resource_type, resource["id"])
        
        # Remove completed emergencies
        for emergency_id in completed_emergencies:
            del self.dispatched_resources[emergency_id]
    
    def _free_resource(self, resource_type, resource_id):
        """Mark a resource as available"""
        for resource in self.available_resources[resource_type]:
            if isinstance(resource, dict) and resource.get("id") == resource_id:
                resource["status"] = "available"
                resource.pop("emergency_id", None)
                break
    
    def _optimize_resource_distribution(self):
        """Optimize distribution of available resources"""
        # In a real system, implement complex resource distribution algorithms
        # For simulation, just log current distribution
        for resource_type, resources in self.available_resources.items():
            available_count = sum(1 for r in resources if isinstance(r, dict) and r.get("status") == "available")
            logger.info(f"Available {resource_type}: {available_count}")
    
    def get_dispatched_resources(self, emergency_id):
        """Get resources dispatched to a specific emergency"""
        if emergency_id in self.dispatched_resources:
            return self.dispatched_resources[emergency_id]["resources"]
        return {}
    
    def get_state(self):
        """Get current state of the resource coordinator"""
        return {
            "status": self.status,
            "active_emergencies": len(self.dispatched_resources),
            "available_resources": {
                resource_type: sum(1 for r in resources if isinstance(r, dict) and r.get("status") == "available")
                for resource_type, resources in self.available_resources.items()
            },
            "dispatched_resources": {
                resource_type: sum(1 for r in resources if isinstance(r, dict) and r.get("status") == "dispatched")
                for resource_type, resources in self.available_resources.items()
                if isinstance(resources, list)
            }
        } 