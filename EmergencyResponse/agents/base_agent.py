from abc import ABC, abstractmethod
import logging
from datetime import datetime

class BaseAgent(ABC):
    def __init__(self, name):
        self.name = name
        self.status = "Initialized"
        self.last_updated = datetime.now()
        self.logger = logging.getLogger(name)
        
    @abstractmethod
    def process(self):
        """Main processing logic for the agent"""
        pass
    
    def update_status(self, new_status):
        """Update the agent's status"""
        self.status = new_status
        self.last_updated = datetime.now()
        self.logger.info(f"Status updated to: {new_status}")
        
    def get_state(self):
        """Get the current state of the agent"""
        return {
            "name": self.name,
            "status": self.status,
            "last_updated": self.last_updated.isoformat()
        }
    
    def log_event(self, event_type, message):
        """Log an event with timestamp"""
        self.logger.info(f"{event_type}: {message}")
        
    def handle_error(self, error):
        """Handle errors in agent processing"""
        self.logger.error(f"Error in {self.name}: {str(error)}")
        self.update_status("Error") 