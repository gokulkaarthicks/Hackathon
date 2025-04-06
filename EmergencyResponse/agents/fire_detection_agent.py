import logging
from datetime import datetime
import json
import random  # For simulation purposes

logger = logging.getLogger(__name__)

class FireDetectionAgent:
    def __init__(self):
        self.status = "Monitoring"
        self.camera_feeds = []
        self.active_fires = {}
        self.fire_stations = {
            "station1": {
                "name": "Central Fire Station",
                "location": {"lat": 51.5074, "lon": -0.1278},
                "resources": {
                    "fire_trucks": 5,
                    "firefighters": 20,
                    "water_tankers": 2
                }
            },
            "station2": {
                "name": "North District Station",
                "location": {"lat": 51.5200, "lon": -0.1300},
                "resources": {
                    "fire_trucks": 3,
                    "firefighters": 12,
                    "water_tankers": 1
                }
            }
        }
        self.fire_hydrants = [
            {"id": "hydrant1", "location": {"lat": 51.5074, "lon": -0.1278}, "status": "operational"},
            {"id": "hydrant2", "location": {"lat": 51.5200, "lon": -0.1300}, "status": "operational"},
            {"id": "hydrant3", "location": {"lat": 51.5100, "lon": -0.1290}, "status": "maintenance"}
        ]
    
    def process(self):
        """Process thermal camera feeds and detect fires"""
        try:
            self._process_camera_feeds()
            self._update_active_fires()
            return True
        except Exception as e:
            logger.error(f"Error processing fire detection: {str(e)}")
            return False
    
    def add_camera_feed(self, feed_url):
        """Add a new thermal camera feed"""
        self.camera_feeds.append({
            "url": feed_url,
            "status": "active",
            "last_check": datetime.now()
        })
        logger.info(f"Added new thermal camera feed: {feed_url}")
    
    def _process_camera_feeds(self):
        """Process all thermal camera feeds for fire detection"""
        for feed in self.camera_feeds:
            try:
                # Simulate thermal camera processing
                self._analyze_thermal_feed(feed)
                feed["last_check"] = datetime.now()
            except Exception as e:
                logger.error(f"Error processing camera feed {feed['url']}: {str(e)}")
                feed["status"] = "error"
    
    def _analyze_thermal_feed(self, feed):
        """Analyze thermal camera feed for fire detection"""
        # In a real system, this would process actual thermal camera data
        # For simulation, randomly detect fires
        if random.random() < 0.01:  # 1% chance of detecting a fire
            fire_location = {
                "lat": self.fire_stations["station1"]["location"]["lat"] + random.uniform(-0.01, 0.01),
                "lon": self.fire_stations["station1"]["location"]["lon"] + random.uniform(-0.01, 0.01)
            }
            self._report_fire(fire_location, feed["url"])
    
    def _report_fire(self, location, source):
        """Report a detected fire"""
        fire_id = f"fire_{int(datetime.now().timestamp())}"
        fire_data = {
            "id": fire_id,
            "location": location,
            "detection_time": datetime.now(),
            "source": source,
            "status": "detected",
            "severity": self._estimate_fire_severity(location),
            "nearest_hydrants": self._find_nearest_hydrants(location),
            "nearest_station": self._find_nearest_fire_station(location)
        }
        self.active_fires[fire_id] = fire_data
        logger.warning(f"Fire detected! ID: {fire_id}, Location: {location}")
        return fire_data
    
    def _estimate_fire_severity(self, location):
        """Estimate fire severity based on location and conditions"""
        # In a real system, this would use thermal imaging data
        return random.choice(["low", "medium", "high", "critical"])
    
    def _find_nearest_hydrants(self, location, max_distance=0.02):
        """Find nearest operational fire hydrants"""
        nearby_hydrants = []
        for hydrant in self.fire_hydrants:
            if hydrant["status"] != "operational":
                continue
            
            # Calculate distance (in a real system, use proper distance calculation)
            distance = abs(location["lat"] - hydrant["location"]["lat"]) + \
                      abs(location["lon"] - hydrant["location"]["lon"])
            
            if distance <= max_distance:
                nearby_hydrants.append({
                    "hydrant_id": hydrant["id"],
                    "distance": distance,
                    "location": hydrant["location"]
                })
        
        return sorted(nearby_hydrants, key=lambda x: x["distance"])
    
    def _find_nearest_fire_station(self, location):
        """Find the nearest fire station"""
        stations_with_distance = []
        for station_id, station in self.fire_stations.items():
            # Calculate distance (in a real system, use proper distance calculation)
            distance = abs(location["lat"] - station["location"]["lat"]) + \
                      abs(location["lon"] - station["location"]["lon"])
            stations_with_distance.append((distance, station_id, station))
        
        if stations_with_distance:
            _, station_id, station = min(stations_with_distance, key=lambda x: x[0])
            return {
                "station_id": station_id,
                "name": station["name"],
                "location": station["location"],
                "available_resources": station["resources"]
            }
        return None
    
    def _update_active_fires(self):
        """Update status of active fires"""
        current_time = datetime.now()
        resolved_fires = []
        
        for fire_id, fire in self.active_fires.items():
            # Update fire status based on time elapsed
            time_elapsed = (current_time - fire["detection_time"]).total_seconds() / 60
            
            if time_elapsed > 60:  # Simulate fire being extinguished after 60 minutes
                fire["status"] = "extinguished"
                resolved_fires.append(fire_id)
            elif time_elapsed > 30:
                fire["status"] = "contained"
            elif time_elapsed > 15:
                fire["status"] = "responding"
            
            logger.info(f"Fire {fire_id} status: {fire['status']}")
        
        # Remove resolved fires
        for fire_id in resolved_fires:
            del self.active_fires[fire_id]
    
    def get_state(self):
        """Get current state of the fire detection agent"""
        return {
            "status": self.status,
            "active_fires": len(self.active_fires),
            "camera_feeds": len(self.camera_feeds),
            "fire_stations": {
                station_id: {
                    "name": station["name"],
                    "available_resources": station["resources"]
                }
                for station_id, station in self.fire_stations.items()
            },
            "operational_hydrants": sum(1 for h in self.fire_hydrants if h["status"] == "operational")
        } 