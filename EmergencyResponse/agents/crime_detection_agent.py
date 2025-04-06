import cv2
import numpy as np
from datetime import datetime
from .base_agent import BaseAgent
import os
import json

class CrimeDetectionAgent(BaseAgent):
    def __init__(self):
        super().__init__("CrimeDetectionAgent")
        self.camera_feeds = []
        self.detection_threshold = 0.7
        self.frame_buffer = []
        self.max_buffer_size = 30  # Store 1 second of video at 30fps
        self.suspicious_activities = []
        
    def process(self):
        """Main processing loop for crime detection"""
        try:
            self.update_status("Monitoring")
            for feed in self.camera_feeds:
                frame = self._get_frame(feed)
                if frame is not None:
                    self._process_frame(feed, frame)
                    
        except Exception as e:
            self.handle_error(e)
            
    def add_camera_feed(self, feed_url):
        """Add a new camera feed to monitor"""
        self.camera_feeds.append({
            "url": feed_url,
            "last_check": None,
            "status": "active"
        })
        self.log_event("Feed", f"Added new camera feed: {feed_url}")
        
    def _get_frame(self, feed):
        """Get a frame from the camera feed"""
        try:
            cap = cv2.VideoCapture(feed["url"])
            ret, frame = cap.read()
            cap.release()
            
            if ret:
                feed["last_check"] = datetime.now()
                return frame
            else:
                self.log_event("Error", f"Failed to get frame from {feed['url']}")
                return None
                
        except Exception as e:
            self.log_event("Error", f"Error accessing camera feed {feed['url']}: {str(e)}")
            return None
            
    def _process_frame(self, feed, frame):
        """Process a single frame for suspicious activities"""
        # Add frame to buffer
        self.frame_buffer.append(frame)
        if len(self.frame_buffer) > self.max_buffer_size:
            self.frame_buffer.pop(0)
            
        # Detect motion
        if len(self.frame_buffer) > 1:
            motion_detected = self._detect_motion(self.frame_buffer[-2], frame)
            if motion_detected:
                self._analyze_motion(feed, frame)
                
    def _detect_motion(self, prev_frame, curr_frame):
        """Detect motion between two frames"""
        # Convert frames to grayscale
        prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
        curr_gray = cv2.cvtColor(curr_frame, cv2.COLOR_BGR2GRAY)
        
        # Calculate absolute difference
        frame_diff = cv2.absdiff(prev_gray, curr_gray)
        
        # Apply threshold
        _, thresh = cv2.threshold(frame_diff, 25, 255, cv2.THRESH_BINARY)
        
        # Calculate motion score
        motion_score = np.sum(thresh) / (thresh.shape[0] * thresh.shape[1])
        
        return motion_score > 1000  # Threshold for motion detection
        
    def _analyze_motion(self, feed, frame):
        """Analyze detected motion for suspicious activities"""
        # This is where you would implement more sophisticated analysis
        # For demo purposes, we'll use a simple heuristic
        
        # Save frame for evidence
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"suspicious_activity_{timestamp}.jpg"
        cv2.imwrite(filename, frame)
        
        # Record suspicious activity
        activity = {
            "timestamp": datetime.now().isoformat(),
            "camera_url": feed["url"],
            "evidence_file": filename,
            "confidence": 0.8  # This would be calculated based on analysis
        }
        
        self.suspicious_activities.append(activity)
        self._trigger_crime_alert(activity)
        
    def _trigger_crime_alert(self, activity):
        """Trigger alert for suspicious activity"""
        alert_data = {
            "type": "crime_alert",
            "timestamp": activity["timestamp"],
            "location": activity["camera_url"],
            "evidence": activity["evidence_file"],
            "confidence": activity["confidence"]
        }
        
        self.log_event("Alert", f"Crime alert triggered: {json.dumps(alert_data)}")
        # Here we would notify other agents through a message queue or event system
        return alert_data
        
    def get_state(self):
        """Get extended state information including monitoring details"""
        state = super().get_state()
        state.update({
            "active_feeds": len(self.camera_feeds),
            "suspicious_activities": len(self.suspicious_activities),
            "buffer_size": len(self.frame_buffer)
        })
        return state 