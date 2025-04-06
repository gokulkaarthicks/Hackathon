import logging
from datetime import datetime
import random

logger = logging.getLogger(__name__)

class OrderAgent:
    def __init__(self):
        self.orders = {}
        self.delivery_partners = [
            {"id": "IC001", "name": "David", "phone": "+18128227804", "rating": 4.9},
            {"id": "IC002", "name": "Sarah", "phone": "+18128227805", "rating": 4.8},
            {"id": "IC003", "name": "Mike", "phone": "+18128227806", "rating": 4.9},
            {"id": "IC004", "name": "Emma", "phone": "+18128227807", "rating": 4.7},
            {"id": "IC005", "name": "John", "phone": "+18128227808", "rating": 4.8}
        ]
    
    def create_order(self, items, user_location, emergency_type):
        """Create a new emergency order"""
        try:
            # Select best available delivery partner
            delivery_partner = self._select_delivery_partner()
            
            # Generate unique order ID
            order_id = f"EM{int(datetime.now().timestamp())}"
            
            # Create order object
            order = {
                "order_id": order_id,
                "status": "CREATED",
                "items": items,
                "delivery_partner": delivery_partner,
                "user_location": user_location,
                "emergency_type": emergency_type,
                "created_at": datetime.now().isoformat(),
                "estimated_delivery": "30-45 minutes",
                "priority": "HIGH",
                "special_instructions": "Emergency Response Order - Priority Delivery"
            }
            
            # Store order
            self.orders[order_id] = order
            
            logger.info(f"Created emergency order {order_id} assigned to {delivery_partner['name']}")
            return order
            
        except Exception as e:
            logger.error(f"Error creating order: {str(e)}")
            return None
    
    def _select_delivery_partner(self):
        """Select the best available delivery partner based on rating"""
        return max(self.delivery_partners, key=lambda x: x['rating'])
    
    def get_order_status(self, order_id):
        """Get current status of an order"""
        return self.orders.get(order_id, {}).get("status", "NOT_FOUND")
    
    def update_order_status(self, order_id, status):
        """Update order status"""
        if order_id in self.orders:
            self.orders[order_id]["status"] = status
            logger.info(f"Updated order {order_id} status to {status}")
            return True
        return False
    
    def process_order(self, order_id):
        """Process the order and update its status"""
        if order_id not in self.orders:
            return False
            
        order = self.orders[order_id]
        
        # Update status to processing
        order["status"] = "PROCESSING"
        logger.info(f"Processing order {order_id}")
        
        # Simulate order acceptance by delivery partner
        order["status"] = "ACCEPTED"
        logger.info(f"Order {order_id} accepted by {order['delivery_partner']['name']}")
        
        return {
            "order_id": order_id,
            "status": "ACCEPTED",
            "delivery_partner": order["delivery_partner"],
            "estimated_delivery": order["estimated_delivery"]
        } 