import requests
import json
import logging
from geopy.distance import geodesic
from datetime import datetime
import random

logger = logging.getLogger(__name__)

class OllamaAgent:
    def __init__(self, model="gemma:2b", order_agent=None):
        self.base_url = "http://localhost:11434/api"
        self.model = model
        self.context = []
        self.order_agent = order_agent
        self.instacart_agents = [
            {"id": "IC001", "name": "John", "phone": "+1234567890"},
            {"id": "IC002", "name": "Sarah", "phone": "+1234567891"},
            {"id": "IC003", "name": "Mike", "phone": "+1234567892"},
            {"id": "IC004", "name": "Emma", "phone": "+1234567893"},
            {"id": "IC005", "name": "David", "phone": "+1234567894"}
        ]
        
    def generate_response(self, prompt, system_prompt=None):
        """Generate response using Ollama's Gemma model"""
        try:
            # Add conciseness instruction to system prompt
            if system_prompt:
                system_prompt = f"{system_prompt}\nKeep responses under 10 words and action-focused."
            else:
                system_prompt = "Keep responses under 10 words and action-focused."

            # Add formatting hints to prompt
            prompt = f"""Context: Emergency response situation
            Task: {prompt}
            Requirements:
            - Be direct and clear
            - Focus on immediate actions
            - No unnecessary words
            - If I am saying I am not safe then immediately send emergency response team to my location"""
            headers = {"Content-Type": "application/json"}
            data = {
                "model": self.model,
                "prompt": prompt,
                "system": system_prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "top_k": 40,
                    "max_tokens": 50  # Limit response length
                }
            }
            
            response = requests.post(f"{self.base_url}/generate", headers=headers, json=data)
            response.raise_for_status()
            
            result = response.json()
            if "error" in result:
                logger.error(f"Ollama API error: {result['error']}")
                return None
                
            # Post-process response to ensure conciseness
            response_text = result.get("response", "")
            if response_text:
                # Remove any unnecessary pleasantries or padding
                response_text = response_text.replace("please", "").replace("would you", "do you")
                response_text = response_text.strip()
                # Limit to first sentence if multiple sentences
                if "." in response_text:
                    response_text = response_text.split(".")[0].strip() + "."
            
            return response_text
        except requests.exceptions.RequestException as e:
            logger.error(f"Error connecting to Ollama API: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Error generating response from Ollama: {str(e)}")
            return None

    def process_instacart_order(self, user_location, needed_items, emergency_type, priority="normal"):
        """Process emergency supply order through OrderAgent"""
        try:
            if not self.order_agent:
                logger.error("OrderAgent not initialized")
                return None

            # Find closest delivery agent
            closest_agent = self._find_closest_agent(user_location)
            if not closest_agent:
                closest_agent = random.choice(self.instacart_agents)

            # Generate order items
            system_prompt = "You are an emergency supply coordinator. List essential items."
            prompt = f"Emergency: {emergency_type}. User needs: {needed_items}"
            
            items_list = self.generate_response(prompt, system_prompt)
            if not items_list:
                return None

            # Create order with priority
            order = {
                "order_id": f"EM{datetime.now().strftime('%Y%m%d%H%M%S')}",
                "items": items_list,
                "delivery_partner": closest_agent,
                "status": "processing",
                "estimated_delivery": "10-20 minutes" if priority == "high" else "15-30 minutes",
                "priority": priority
            }

            return order

        except Exception as e:
            logger.error(f"Error processing order: {str(e)}")
            return None

    def _find_closest_agent(self, user_location):
        """Find the closest delivery agent based on location"""
        try:
            # Simulate finding closest agent
            # In real implementation, would calculate actual distances
            return random.choice(self.instacart_agents)
        except Exception:
            return None

    def process_emergency_alert(self, user_location, emergency_type, emergency_location):
        """Process emergency alert and generate initial safety check using NLP"""
        try:
            if emergency_type == "severe_storm":
                if user_location and emergency_location:
                    try:
                        distance = geodesic(
                            (user_location["lat"], user_location["lon"]),
                            (emergency_location["lat"], emergency_location["lon"])
                        ).kilometers
                        return f"Severe storm {distance:.1f} km away. Are you safe?"
                    except Exception:
                        pass
                return "Severe storm detected nearby. Are you safe?"

            system_prompt = """You are an emergency response coordinator.
            Keep initial contact brief and focused on safety."""
            
            # Calculate distance if available
            distance_info = ""
            if user_location and emergency_location:
                try:
                    distance = geodesic(
                        (user_location["lat"], user_location["lon"]),
                        (emergency_location["lat"], emergency_location["lon"])
                    ).kilometers
                    distance_info = f"{distance:.1f} km away."
                except Exception:
                    pass

            prompt = f"""Emergency: {emergency_type} {distance_info}
            Create a brief safety check message."""
            
            initial_message = self.generate_response(prompt, system_prompt)
            
            if initial_message:
                self.context = [{
                    "emergency_type": emergency_type,
                    "distance": distance_info,
                    "time": datetime.now().strftime("%H:%M"),
                    "stage": "safety_check",
                    "last_response": initial_message
                }]
                return initial_message
            
            return None
            
        except Exception as e:
            logger.error(f"Error processing emergency alert: {str(e)}")
            return None

    def process_user_response(self, response_text, emergency_type="severe_storm", voice_emotion="neutral"):
        """Process user's voice response and emotion to generate appropriate follow-up"""
        try:
            if not self.context:
                self.context = [{
                    "emergency_type": emergency_type,
                    "stage": "safety_check",
                    "time": datetime.now().strftime("%H:%M")
                }]
            
            response_text = response_text.lower()
            user_location = self.context[-1].get("user_location", {"lat": 0, "lon": 0})
            current_stage = self.context[-1].get("stage", "safety_check")
            
            # Check for unsafe situation through text or voice emotion
            is_unsafe = any(word in response_text for word in ["not safe", "help", "emergency", "danger", "scared", "hurt"])
            is_distressed = voice_emotion in ["distressed", "scared", "panicked", "anxious"]
            
            # Immediate emergency response if unsafe or distressed
            if is_unsafe or is_distressed:
                self.context[-1]["stage"] = "emergency_dispatch"
                
                # Get appropriate emergency services
                emergency_services = {
                    "severe_storm": ["rescue", "medical"],
                    "fire": ["fire", "medical"],
                    "medical_emergency": ["medical"],
                    "gun_detected": ["police", "medical"],
                    "suspicious_activity": ["police"]
                }.get(emergency_type, ["rescue", "medical"])
                
                # Dispatch emergency team
                if self.order_agent:
                    try:
                        dispatch_info = self.order_agent.dispatch_emergency_team(
                            emergency_type=emergency_type,
                            location=user_location,
                            services=emergency_services,
                            priority="high" if is_distressed else "normal"
                        )
                        
                        # Store dispatch info
                        self.context[-1]["dispatch_info"] = dispatch_info
                        
                        # Generate response based on emotion
                        if is_distressed:
                            return "Emergency team is on the way. Stay on the line with me."
                        else:
                            eta = dispatch_info.get("eta", "15") if dispatch_info else "15"
                            return f"Help is coming in {eta} minutes. Stay where you are, I'm here with you."
                    except Exception as e:
                        logger.error(f"Error dispatching emergency team: {str(e)}")
                        return "Emergency team is coming. Stay put, I'll stay with you."

                return "Emergency team is on their way. Stay where you are, I'm here with you."

            # Handle safe responses and move to supply needs
            if current_stage == "safety_check" and any(word in response_text for word in ["yes", "safe", "okay", "fine"]):
                self.context[-1]["stage"] = "needs_check"
                return "I'm glad you're safe. Do you need any emergency supplies or groceries?"
            
            # Handle supply needs
            if current_stage == "needs_check":
                supply_keywords = ["food", "grocery", "groceries", "supplies", "water", "drink", "medical", "medicine", "need", "yes"]
                if any(word in response_text for word in supply_keywords):
                    self.context[-1]["stage"] = "arranging_help"
                    order = None
                    if self.order_agent:
                        order = self.process_instacart_order(
                            user_location=user_location,
                            needed_items=response_text,
                            emergency_type=emergency_type,
                            priority="high" if voice_emotion == "urgent" else "normal"
                        )
                    
                    if order:
                        return f"I've ordered supplies for you. They'll arrive in {order['estimated_delivery']}. Is there anything else you need?"
                    return "I'm arranging supplies for you now. What specific items do you need?"
                elif any(word in response_text for word in ["no", "don't need", "good"]):
                    self.context[-1]["stage"] = "final_instructions"
                    return "Okay, let me give you some important safety instructions."
            
            # Handle final instructions
            if current_stage == "final_instructions":
                return "Stay safe and don't hesitate to ask for help if anything changes. I'm here for you."
            
            # Default response based on context
            return self._get_context_based_response(current_stage, emergency_type)
            
        except Exception as e:
            logger.error(f"Error processing user response: {str(e)}")
            return None

    def _get_context_based_response(self, stage, emergency_type):
        """Get appropriate response based on conversation context"""
        if stage == "safety_check":
            return "Please tell me - are you in a safe place right now?"
        elif stage == "needs_check":
            return "Would you like me to arrange any emergency supplies for you?"
        elif stage == "arranging_help":
            return "What specific supplies do you need? I can help arrange them."
        else:
            return "I'm here to help. What do you need right now?"

    def _get_final_safety_message(self, emergency_type):
        """Get final safety message without monitoring notification"""
        messages = {
            "severe_storm": """Generate brief final instructions that:
                1. Remind them to stay indoors and away from windows
                2. Suggest having emergency supplies ready""",
            
            "tornado": """Generate brief final instructions that:
                1. Emphasize staying in the lowest level/basement
                2. Remind them to monitor official weather updates""",
            
            "gun_detected": """Generate brief final instructions that:
                1. Reinforce staying in a secure location
                2. Assure that police are actively responding""",
            
            "suspicious_activity": """Generate brief final instructions that:
                1. Advise continuing to stay inside
                2. Remind them that police are patrolling the area""",
            
            "fire_building": """Generate brief final instructions that:
                1. Reinforce evacuation instructions
                2. Confirm fire services are actively responding""",
            
            "medical_emergency": """Generate brief final instructions that:
                1. Provide reassurance about paramedic response
                2. Give relevant basic first aid reminder if needed"""
        }
        
        return messages.get(emergency_type, """Generate a brief final message that:
            1. Provides reassurance about emergency response
            2. Gives clear next steps""")
    
    def generate_store_request(self, user_location, needed_items):
        """Generate a structured request for nearby stores through Instacart"""
        try:
            # Select a random Instacart agent
            agent = random.choice(self.instacart_agents)
            
            system_prompt = """You are an emergency response coordinator working with Instacart.
            Generate clear, professional requests for emergency supply delivery.
            Focus on essential items and urgency."""
            
            prompt = f"""Create an emergency Instacart request with:
            Location: {user_location}
            Needed items: {needed_items}
            Priority: Emergency Response
            Assigned Agent: {agent['name']} (ID: {agent['id']})
            
            Generate a clear, structured request emphasizing:
            1. Emergency priority status
            2. Specific items needed with quantities
            3. Delivery urgency (30-45 minute target)
            4. Special handling instructions
            
            Format it as a natural request that an Instacart shopper would understand."""
            
            store_request = self.generate_response(prompt, system_prompt)
            if store_request:
                return {
                    "request": store_request,
                    "agent": agent,
                    "estimated_delivery": "30-45 minutes",
                    "priority": "HIGH"
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error generating store request: {str(e)}")
            return None 