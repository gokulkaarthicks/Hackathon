import logging
from datetime import datetime
import json
import random  # For simulation purposes

logger = logging.getLogger(__name__)

class TrafficMonitoringAgent:
    def __init__(self):
        self.status = "Monitoring"
        self.traffic_cameras = []
        self.traffic_conditions = {}
        self.road_network = {
            "main_st": {
                "name": "Main Street",
                "type": "major",
                "connections": ["oak_ave", "park_rd"],
                "traffic_lights": ["light1", "light2"]
            },
            "oak_ave": {
                "name": "Oak Avenue",
                "type": "secondary",
                "connections": ["main_st", "elm_st"],
                "traffic_lights": ["light3"]
            },
            "park_rd": {
                "name": "Park Road",
                "type": "secondary",
                "connections": ["main_st", "elm_st"],
                "traffic_lights": ["light4"]
            },
            "elm_st": {
                "name": "Elm Street",
                "type": "residential",
                "connections": ["oak_ave", "park_rd"],
                "traffic_lights": ["light5"]
            }
        }
        self.traffic_lights = {
            "light1": {"status": "green", "location": {"lat": 51.5074, "lon": -0.1278}},
            "light2": {"status": "red", "location": {"lat": 51.5080, "lon": -0.1280}},
            "light3": {"status": "green", "location": {"lat": 51.5085, "lon": -0.1285}},
            "light4": {"status": "red", "location": {"lat": 51.5090, "lon": -0.1290}},
            "light5": {"status": "green", "location": {"lat": 51.5095, "lon": -0.1295}}
        }
    
    def process(self):
        """Process traffic monitoring data"""
        try:
            self._update_traffic_conditions()
            self._optimize_traffic_flow()
            return True
        except Exception as e:
            logger.error(f"Error processing traffic monitoring: {str(e)}")
            return False
    
    def _update_traffic_conditions(self):
        """Update traffic conditions for all monitored roads"""
        current_time = datetime.now()
        
        for road_id, road in self.road_network.items():
            # Simulate traffic condition updates
            conditions = self._simulate_traffic_conditions(road)
            self.traffic_conditions[road_id] = {
                "road_name": road["name"],
                "conditions": conditions,
                "last_update": current_time,
                "incidents": self._check_for_incidents(road_id)
            }
    
    def _simulate_traffic_conditions(self, road):
        """Simulate traffic conditions for a road"""
        # In a real system, this would use actual traffic sensor data
        base_congestion = {
            "major": 0.7,
            "secondary": 0.5,
            "residential": 0.3
        }.get(road["type"], 0.4)
        
        # Add some randomness
        congestion = base_congestion + random.uniform(-0.2, 0.2)
        congestion = max(0, min(1, congestion))
        
        if congestion < 0.3:
            return "clear"
        elif congestion < 0.6:
            return "moderate"
        elif congestion < 0.8:
            return "heavy"
        else:
            return "severe"
    
    def _check_for_incidents(self, road_id):
        """Check for traffic incidents on a road"""
        # In a real system, this would check actual incident reports
        if random.random() < 0.05:  # 5% chance of an incident
            incident_types = ["accident", "construction", "debris", "disabled_vehicle"]
            return {
                "type": random.choice(incident_types),
                "severity": random.choice(["minor", "moderate", "major"]),
                "reported_time": datetime.now().isoformat()
            }
        return None
    
    def _optimize_traffic_flow(self):
        """Optimize traffic flow by adjusting traffic lights"""
        for road_id, conditions in self.traffic_conditions.items():
            if conditions["conditions"] in ["heavy", "severe"]:
                self._adjust_traffic_lights(road_id)
    
    def _adjust_traffic_lights(self, congested_road_id):
        """Adjust traffic lights to alleviate congestion"""
        road = self.road_network[congested_road_id]
        for light_id in road["traffic_lights"]:
            # Simulate traffic light adjustment
            current_status = self.traffic_lights[light_id]["status"]
            if current_status == "red":
                self.traffic_lights[light_id]["status"] = "green"
                logger.info(f"Adjusted traffic light {light_id} to green to alleviate congestion")
    
    def get_traffic_conditions(self, location):
        """Get traffic conditions near a location"""
        nearby_conditions = []
        
        for road_id, conditions in self.traffic_conditions.items():
            # In a real system, calculate actual distance to road
            # For simulation, just return all conditions
            nearby_conditions.append({
                "road_name": conditions["road_name"],
                "conditions": conditions["conditions"],
                "incidents": conditions["incidents"]
            })
        
        return nearby_conditions
    
    def get_state(self):
        """Get current state of the traffic monitoring agent"""
        return {
            "status": self.status,
            "monitored_roads": len(self.road_network),
            "traffic_conditions": {
                road_id: {
                    "name": conditions["road_name"],
                    "conditions": conditions["conditions"],
                    "has_incident": conditions["incidents"] is not None
                }
                for road_id, conditions in self.traffic_conditions.items()
            },
            "traffic_lights": {
                light_id: light["status"]
                for light_id, light in self.traffic_lights.items()
            }
        } 