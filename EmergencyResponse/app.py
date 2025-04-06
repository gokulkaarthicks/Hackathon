from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO
import threading
import time
import logging
from agents.weather_agent import WeatherAgent
from agents.notification_agent import NotificationAgent
from agents.crime_detection_agent import CrimeDetectionAgent
from agents.medical_emergency_agent import MedicalEmergencyAgent
from agents.fire_detection_agent import FireDetectionAgent
from agents.traffic_monitoring_agent import TrafficMonitoringAgent
from agents.resource_coordinator_agent import ResourceCoordinatorAgent
from agents.ollama_agent import OllamaAgent
from agents.order_agent import OrderAgent
from datetime import datetime
import json
import random

# Configure logging with more detailed format
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# Initialize all agents
weather_agent = WeatherAgent()
notification_agent = NotificationAgent()
crime_agent = CrimeDetectionAgent()
medical_agent = MedicalEmergencyAgent()
fire_agent = FireDetectionAgent()
traffic_agent = TrafficMonitoringAgent()
resource_coordinator = ResourceCoordinatorAgent()
order_agent = OrderAgent()
ollama_agent = OllamaAgent(order_agent=order_agent)

# Emergency response zones (in a real system, this would be in a database)
EMERGENCY_ZONES = [
    {
        "id": "zone1",
        "name": "Downtown",
        "location": {"lat": 51.5074, "lon": -0.1278},
        "resources": {
            "ambulances": 5,
            "fire_trucks": 3,
            "police_units": 4
        }
    },
    {
        "id": "zone2",
        "name": "Suburban Area",
        "location": {"lat": 51.5200, "lon": -0.1300},
        "resources": {
            "ambulances": 3,
            "fire_trucks": 2,
            "police_units": 3
        }
    }
]

# Test users with enhanced information
TEST_USERS = [
    {
        "id": "user1",
        "phone": "+18128227804",
        "location": {"lat": 51.5074, "lon": -0.1278},
        "name": "Test User 1",
        "emergency_contacts": ["+18128227804"],
        "medical_conditions": ["diabetes"],
        "preferred_hospital": "City General Hospital",
        "language": "en",
        "notifications_enabled": True
    }
]

# Define scenarios with detailed interactions and voice messages
scenarios = {
    "severe_storm": {
        "type": "weather",
        "description": "Severe storm warning - Take shelter immediately",
        "voice_message": "Emergency Alert: A severe storm is approaching your area. Please take shelter immediately. Do you need any emergency supplies like flashlights, batteries, or non-perishable food?",
        "interactions": [
            {"from": "Weather Agent", "to": "Notification Agent", "message": "Severe storm detected in area"},
            {"from": "Notification Agent", "to": "Resource Coordinator", "message": "Requesting emergency response units"},
            {"from": "Resource Coordinator", "to": "Traffic Agent", "message": "Requesting traffic optimization for emergency vehicles"}
        ]
    },
    "tornado": {
        "type": "weather",
        "description": "Tornado warning - Seek shelter in basement or interior room",
        "voice_message": "Emergency Alert: A tornado has been detected in your area. Seek shelter immediately in a basement or interior room. Do you have access to a safe shelter? If not, we can dispatch emergency services to assist you.",
        "interactions": [
            {"from": "Weather Agent", "to": "Notification Agent", "message": "Tornado detected - Immediate evacuation required"},
            {"from": "Notification Agent", "to": "Resource Coordinator", "message": "Requesting all available emergency units"},
            {"from": "Resource Coordinator", "to": "Traffic Agent", "message": "Emergency traffic routing activated"}
        ]
    },
    "gun_detected": {
        "type": "crime",
        "description": "Gun detected in camera feed - Immediate response required",
        "voice_message": "Emergency Alert: A firearm has been detected in your area. Please stay indoors and away from windows. Police units are being dispatched. Are you in a safe location? Do you need immediate assistance?",
        "interactions": [
            {"from": "Crime Agent", "to": "Notification Agent", "message": "Gun detected in camera feed"},
            {"from": "Notification Agent", "to": "Resource Coordinator", "message": "Requesting police units"},
            {"from": "Resource Coordinator", "to": "Traffic Agent", "message": "Requesting clear route for police response"}
        ]
    },
    "suspicious_activity": {
        "type": "crime",
        "description": "Suspicious activity detected - Police notified",
        "voice_message": "Emergency Alert: Suspicious activity has been reported in your area. Please remain vigilant and report any unusual behavior. Police patrols have been increased. Do you have any information about the suspicious activity?",
        "interactions": [
            {"from": "Crime Agent", "to": "Notification Agent", "message": "Suspicious activity detected"},
            {"from": "Notification Agent", "to": "Resource Coordinator", "message": "Requesting police patrol"},
            {"from": "Resource Coordinator", "to": "Traffic Agent", "message": "Monitoring traffic for police response"}
        ]
    },
    "fire_building": {
        "type": "fire",
        "description": "Building fire detected - Evacuation required",
        "voice_message": "Emergency Alert: A building fire has been detected in your area. Please evacuate immediately if you are in the affected building. Fire trucks and ambulances are on the way. Do you need assistance with evacuation?",
        "interactions": [
            {"from": "Fire Agent", "to": "Notification Agent", "message": "Building fire detected"},
            {"from": "Notification Agent", "to": "Resource Coordinator", "message": "Requesting fire trucks and ambulances"},
            {"from": "Resource Coordinator", "to": "Traffic Agent", "message": "Emergency route for fire trucks"}
        ]
    },
    "medical_emergency": {
        "type": "medical",
        "description": "Medical emergency - Ambulance dispatched",
        "voice_message": "Emergency Alert: A medical emergency has been reported in your area. An ambulance is being dispatched. Do you need any medications or medical supplies? We can coordinate with nearby pharmacies for immediate delivery.",
        "interactions": [
            {"from": "Medical Agent", "to": "Notification Agent", "message": "Medical emergency reported"},
            {"from": "Notification Agent", "to": "Resource Coordinator", "message": "Requesting ambulance and medical team"},
            {"from": "Resource Coordinator", "to": "Traffic Agent", "message": "Priority route for ambulance"}
        ]
    }
}

# Store agent states with more detailed information
agent_states = {
    "weather": weather_agent.get_state(),
    "notification": notification_agent.get_state(),
    "crime": crime_agent.get_state(),
    "medical": medical_agent.get_state(),
    "fire": fire_agent.get_state(),
    "traffic": traffic_agent.get_state(),
    "resource_coordinator": resource_coordinator.get_state()
}

# Emergency event history
emergency_history = []

def update_agent_states():
    """Update agent states and emit to connected clients"""
    while True:
        try:
            # Get current states from all agents
            current_states = {
                "weather": weather_agent.get_state(),
                "notification": notification_agent.get_state(),
                "crime": crime_agent.get_state(),
                "medical": medical_agent.get_state(),
                "fire": fire_agent.get_state(),
                "traffic": traffic_agent.get_state(),
                "resource_coordinator": resource_coordinator.get_state()
            }
            
            # Add timestamps to each agent's state
            for agent_name, state in current_states.items():
                state["last_update"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Emit updated states to all connected clients
            socketio.emit("agent_states", current_states)
            
            # Log state updates
            logger.info("Agent states updated and emitted to clients")
            
            # Sleep for a short interval
            time.sleep(1)
        except Exception as e:
            logger.error(f"Error updating agent states: {str(e)}")
            time.sleep(5)  # Sleep longer on error

@app.route("/")
def index():
    """Render the main dashboard"""
    return render_template("index.html", 
                         agent_states=agent_states,
                         emergency_zones=EMERGENCY_ZONES)

@app.route("/api/states")
def get_states():
    """API endpoint to get current agent states"""
    return jsonify(agent_states)

@app.route("/api/emergency-history")
def get_emergency_history():
    """API endpoint to get emergency event history"""
    return jsonify(emergency_history)

@app.route("/api/zones")
def get_zones():
    """API endpoint to get emergency response zones"""
    return jsonify(EMERGENCY_ZONES)

@app.route("/api/trigger-alert", methods=["POST"])
def trigger_alert():
    """API endpoint to trigger emergency alerts"""
    try:
        data = request.json
        alert_type = data.get('type')
        location = data.get('location')
        description = data.get('description')
        
        if not all([alert_type, location, description]):
            return jsonify({"error": "Missing required fields"}), 400
        
        # Create alert data
        alert_data = {
            "id": f"alert_{int(datetime.now().timestamp())}",
            "type": alert_type,
            "location": location,
            "description": description,
            "timestamp": datetime.now().isoformat(),
            "status": "new"
        }
        
        # Add to emergency history
        emergency_history.append(alert_data)
        
        # Emit alert to all connected clients
        socketio.emit("emergency_alert", {
            "type": alert_type,
            "message": description,
            "location": location,
            "timestamp": alert_data["timestamp"]
        })
        
        # Coordinate response based on alert type
        if alert_type == "weather":
            weather_agent.process_alert(alert_data)
        elif alert_type == "crime":
            crime_agent.process_alert(alert_data)
        elif alert_type == "fire":
            fire_agent.process_alert(alert_data)
        elif alert_type == "medical":
            medical_agent.add_emergency(alert_data)
        
        # Coordinate resources for the emergency
        resource_coordinator.coordinate_emergency_response(alert_data)
        
        return jsonify({"status": "success", "alert": alert_data})
    except Exception as e:
        logger.error(f"Error triggering alert: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/simulate', methods=['POST'])
def simulate_emergency():
    """API endpoint to simulate various emergency scenarios"""
    try:
        data = request.json
        scenario = data.get('scenario')
        
        if not scenario:
            return jsonify({"error": "Missing scenario parameter"}), 400
        
        # Generate random location within the city
        location = {
            "lat": 51.5074 + (random.random() - 0.5) * 0.1,
            "lon": -0.1278 + (random.random() - 0.5) * 0.1
        }
        
        # Define scenarios
        scenarios = {
            "severe_storm": {
                "type": "weather",
                "description": "Severe storm warning - Take shelter immediately"
            },
            "tornado": {
                "type": "weather",
                "description": "Tornado warning - Seek shelter in basement or interior room"
            },
            "gun_detected": {
                "type": "crime",
                "description": "Gun detected in camera feed - Immediate response required"
            },
            "suspicious_activity": {
                "type": "crime",
                "description": "Suspicious activity detected - Police notified"
            },
            "fire_building": {
                "type": "fire",
                "description": "Building fire detected - Evacuation required"
            },
            "medical_emergency": {
                "type": "medical",
                "description": "Medical emergency - Ambulance dispatched"
            }
        }
        
        if scenario not in scenarios:
            return jsonify({"error": "Invalid scenario"}), 400
        
        # Get scenario details
        scenario_data = scenarios[scenario]
        
        # Create alert data
        alert_data = {
            "id": f"alert_{int(datetime.now().timestamp())}",
            "type": scenario_data["type"],
            "location": location,
            "description": scenario_data["description"],
            "timestamp": datetime.now().isoformat(),
            "status": "new"
        }
        
        # Add to emergency history
        emergency_history.append(alert_data)
        
        # Emit alert to all connected clients
        socketio.emit("emergency_alert", {
            "type": scenario_data["type"],
            "message": scenario_data["description"],
            "location": location,
            "timestamp": alert_data["timestamp"]
        })
        
        # Process the alert based on type
        if scenario_data["type"] == "weather":
            weather_agent.process_alert(alert_data)
        elif scenario_data["type"] == "crime":
            crime_agent.process_alert(alert_data)
        elif scenario_data["type"] == "fire":
            fire_agent.process_alert(alert_data)
        elif scenario_data["type"] == "medical":
            medical_agent.add_emergency(alert_data)
        
        # Coordinate resources for the emergency
        resource_coordinator.coordinate_emergency_response(alert_data)
        
        return jsonify({"status": "success", "alert": alert_data})
    except Exception as e:
        logger.error(f"Error simulating emergency: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route("/simulation")
def simulation():
    """Render the simulation dashboard"""
    return render_template("simulation.html")

@socketio.on('start_simulation')
def handle_simulation(data):
    """Handle simulation start event"""
    try:
        scenario = data.get('scenario')
        if not scenario:
            return
            
        # Get scenario message
        scenario_message = scenarios.get(scenario, {}).get('voice_message', 'Are you safe?')
        
        # Send initial warning message
        socketio.emit('ai_response', {
            'response': "EMERGENCY ALERT: Tornado approaching your area. Are you safe? Please respond immediately.",
            'type': 'emergency'
        })
        
        logger.info(f"Emergency alert sent - Scenario: {scenario}")
            
    except Exception as e:
        logger.error(f"Error starting simulation: {str(e)}")
        socketio.emit('notification', {
            'type': 'error',
            'message': f"Error starting simulation: {str(e)}"
        })

@socketio.on('stop_simulation')
def handle_simulation_stop():
    """Handle simulation stop request"""
    try:
        # Reset agent states
        weather_agent.status = "Monitoring"
        crime_agent.status = "Monitoring"
        fire_agent.status = "Monitoring"
        medical_agent.status = "Monitoring"
        traffic_agent.status = "Monitoring"
        resource_coordinator.status = "Active"
        
        # Emit notification
        socketio.emit("notification", {
            "type": "info",
            "message": "Simulation stopped - All agents reset to monitoring state"
        })
        
    except Exception as e:
        logger.error(f"Error stopping simulation: {str(e)}")
        socketio.emit("notification", {
            "type": "error",
            "message": f"Error stopping simulation: {str(e)}"
        })

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    logger.info("Client connected")
    socketio.emit('ai_response', {'response': 'Connected to emergency response system. How can I help?', 'type': 'normal'})

@socketio.on('user_response')
def handle_user_response(data):
    """Handle user voice response"""
    try:
        response_text = data.get('response', '').lower()
        emergency_type = data.get('emergency_type', 'severe_storm')
        voice_emotion = data.get('emotion', 'neutral')
        
        logger.info(f"Received user response: {response_text} with emotion: {voice_emotion}")
        
        # Get user location (in real app, this would come from client)
        user_location = {
            "lat": 40.7128,
            "lon": -74.0060
        }
        
        # Immediate check for unsafe situation
        if "not safe" in response_text or "help" in response_text:
            logger.info("User indicated they are not safe - Dispatching emergency services")
            
            # Determine emergency services based on type
            emergency_services = {
                "severe_storm": ["rescue", "medical"],
                "fire": ["fire", "medical"],
                "medical_emergency": ["medical"],
                "gun_detected": ["police", "medical"],
                "suspicious_activity": ["police"]
            }.get(emergency_type, ["rescue", "medical"])
            
            # Dispatch emergency team
            if order_agent:
                dispatch_info = order_agent.dispatch_emergency_team(
                    emergency_type=emergency_type,
                    location=user_location,
                    services=emergency_services
                )
                
                # Emit emergency dispatch event
                socketio.emit('emergency_dispatch', {
                    'status': 'dispatched',
                    'location': user_location,
                    'services': emergency_services,
                    'eta': '10 minutes'
                })
            
            # Send immediate response to user
            socketio.emit('ai_response', {
                'response': "Emergency rescue team has been dispatched to your location. Stay where you are. Help is coming in 10 minutes. Stay on the line with me.",
                'type': 'emergency'
            })
            return
        
        # For other responses, process through Ollama agent
        if ollama_agent:
            ai_response = ollama_agent.process_user_response(
                response_text=response_text,
                emergency_type=emergency_type,
                voice_emotion=voice_emotion
            )
            
            if ai_response:
                socketio.emit('ai_response', {
                    'response': ai_response,
                    'type': 'normal'
                })
            else:
                # Fallback response if Ollama fails
                socketio.emit('ai_response', {
                    'response': "Please tell me clearly - are you safe?",
                    'type': 'normal'
                })
        
    except Exception as e:
        logger.error(f"Error processing user response: {str(e)}")
        socketio.emit('ai_response', {
            'response': "I'm having trouble understanding. Please tell me - are you safe?",
            'type': 'error'
        })

@socketio.on('order_status')
def handle_order_status(data):
    """Handle order status updates"""
    try:
        order_id = data.get('order_id')
        if not order_id:
            return
            
        status = order_agent.get_order_status(order_id)
        socketio.emit('order_update', {
            'order_id': order_id,
            'status': status
        })
        
    except Exception as e:
        logger.error(f"Error getting order status: {str(e)}")

def generate_fallback_response(scenario, user_response):
    """Generate a fallback response when Ollama fails"""
    if "yes" in user_response or "okay" in user_response or "sure" in user_response:
        return "I understand you're agreeing. Let me know if you need any emergency supplies or assistance."
    elif "no" in user_response or "don't" in user_response or "not" in user_response:
        return "I understand. Please stay safe and don't hesitate to ask for help if you need it."
    elif any(word in user_response for word in ["help", "emergency", "assistance", "need"]):
        return "I'll make sure to get you the help you need. What specific assistance do you require?"
    else:
        return "Could you please clarify if you need any emergency assistance or supplies?"

def run_agents():
    """Enhanced function to run all agents in separate threads with improved coordination"""
    def run_agent(agent, interval, name):
        logger.info(f"Starting {name} agent")
        while True:
            try:
                # Only process if the agent has active alerts or is required
                if hasattr(agent, 'has_active_alerts') and agent.has_active_alerts():
                    agent.process()
                elif name == "Resource Coordinator" or name == "Notification":
                    # These agents should always run
                    agent.process()
                elif name == "Traffic Monitoring":
                    # Only process traffic if there are emergencies requiring traffic management
                    active_emergencies = [e for e in emergency_history if e.get("requires_traffic_management", False)]
                    if active_emergencies:
                        agent.process()
                time.sleep(interval)
            except Exception as e:
                logger.error(f"Error in {name} agent: {str(e)}")
                time.sleep(5)  # Wait before retrying
    
    # Define agent configurations with adjusted intervals
    agent_configs = [
        (weather_agent, 300, "Weather"),  # 5 minutes
        (notification_agent, 1, "Notification"),  # 1 second
        (crime_agent, 0.1, "Crime Detection"),  # 100ms
        (medical_agent, 1, "Medical Emergency"),  # 1 second
        (fire_agent, 0.5, "Fire Detection"),  # 500ms
        (traffic_agent, 5, "Traffic Monitoring"),  # 5 seconds
        (resource_coordinator, 1, "Resource Coordinator")  # 1 second
    ]
    
    # Start all agent threads
    for agent, interval, name in agent_configs:
        thread = threading.Thread(
            target=run_agent,
            args=(agent, interval, name),
            daemon=True
        )
        thread.start()
        logger.info(f"{name} agent thread started")
    
    # Start state update thread
    threading.Thread(target=update_agent_states, daemon=True).start()

if __name__ == "__main__":
    # Add test camera feeds
    crime_agent.add_camera_feed("rtsp://example.com/camera1")
    crime_agent.add_camera_feed("rtsp://example.com/camera2")
    
    # Initialize fire detection cameras
    fire_agent.add_camera_feed("rtsp://example.com/thermal1")
    fire_agent.add_camera_feed("rtsp://example.com/thermal2")
    
    # Start all agents
    run_agents()
    
    # Print access information
    print("\n" + "="*50)
    print("Emergency Response System is running!")
    print("Access the dashboard at: http://localhost:5001")
    print("If you can't access it, try: http://127.0.0.1:5001")
    print("="*50 + "\n")
    
    # Run the Flask application
    socketio.run(app, host='0.0.0.0', port=5001, debug=True, allow_unsafe_werkzeug=True) 