# rasa_health_bot.py
import json
import random
import time
import os
import csv
import re
import requests
from typing import Dict, List, Optional, Any

# Rasa integration
RASA_SERVER_URL = "http://localhost:5005"  # Default Rasa server URL

LOG_DIR = "logs"
LOGFILE = os.path.join(LOG_DIR, "conversations.csv")
os.makedirs(LOG_DIR, exist_ok=True)

def log_turn(session_id, user, bot, intent, confidence, entities=None):
    exists = os.path.exists(LOGFILE)
    with open(LOGFILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not exists:
            writer.writerow(["timestamp", "session_id", "user", "bot", "intent", "confidence", "entities"])
        writer.writerow([time.time(), session_id, user, bot, intent, confidence, str(entities or {})])

class RasaHealthBot:
    def __init__(self, rasa_url=RASA_SERVER_URL):
        self.rasa_url = rasa_url
        self.sessions = {}
        self.fallback_responses = True  # Enable smart fallbacks when Rasa is down
    
    def start_session(self, sid="default"):
        self.sessions[sid] = {
            "history": [],
            "context": {},
            "user_name": None,
            "symptoms": [],
            "entities": {},
            "conversation_stage": "greeting"
        }
    
    def end_session(self, sid="default"):
        if sid in self.sessions:
            # Send session end to Rasa
            self._send_to_rasa("/conversations/{}/tracker/events".format(sid), {
                "event": "session_started",
                "timestamp": time.time()
            })
            del self.sessions[sid]
    
    def _send_to_rasa(self, endpoint, data=None, method="POST"):
        """Send request to Rasa server"""
        try:
            url = f"{self.rasa_url}{endpoint}"
            if method == "POST":
                response = requests.post(url, json=data, timeout=5)
            else:
                response = requests.get(url, timeout=5)
            return response.json() if response.status_code == 200 else None
        except Exception as e:
            print(f"Rasa connection error: {e}")
            return None
    
    def _parse_rasa_response(self, rasa_response):
        """Parse Rasa response and extract useful information"""
        if not rasa_response:
            return None, 0.0, [], ""
        
        # Extract intent
        intent_data = rasa_response.get("intent", {})
        intent = intent_data.get("name", "unknown")
        confidence = intent_data.get("confidence", 0.0)
        
        # Extract entities
        entities = rasa_response.get("entities", [])
        
        # Extract response text (if any)
        response_text = ""
        if "response" in rasa_response:
            response_text = rasa_response["response"].get("text", "")
        
        return intent, confidence, entities, response_text
    
    def _extract_entities_info(self, entities):
        """Extract useful information from Rasa entities"""
        extracted = {
            "symptoms": [],
            "severity": None,
            "duration": None,
            "body_parts": [],
            "person": None
        }
        
        for entity in entities:
            entity_type = entity.get("entity")
            entity_value = entity.get("value")
            
            if entity_type == "symptom":
                extracted["symptoms"].append(entity_value)
            elif entity_type == "severity":
                extracted["severity"] = entity_value
            elif entity_type == "duration":
                extracted["duration"] = entity_value
            elif entity_type == "body_part":
                extracted["body_parts"].append(entity_value)
            elif entity_type == "PERSON":
                extracted["person"] = entity_value
        
        return extracted
    
    def _generate_smart_response(self, intent, entities_info, user_input, session):
        """Generate intelligent responses using Rasa insights + our logic"""
        user_name = session.get("user_name") or entities_info.get("person", "")
        if user_name and not session.get("user_name"):
            session["user_name"] = user_name
        
        name_part = f" {user_name}" if user_name else ""
        
        # Update session with extracted info
        if entities_info["symptoms"]:
            session["symptoms"].extend(entities_info["symptoms"])
        session["entities"].update(entities_info)
        
        # Intent-based responses enhanced with entity information
        if intent == "greet":
            if user_name:
                return f"Hi {user_name}! Great to meet you. I'm your health assistant. What can I help you with today?"
            return f"Hey there{name_part}! I'm here to help with any health questions. How are you feeling?"
        
        elif intent == "inform_symptom" or intent == "ask_symptom":
            symptoms = entities_info["symptoms"]
            severity = entities_info["severity"]
            duration = entities_info["duration"]
            body_parts = entities_info["body_parts"]
            
            if not symptoms:
                symptoms = self._extract_symptoms_fallback(user_input)
            
            response_parts = []
            
            if symptoms:
                primary_symptom = symptoms[0]
                
                # Emergency check
                if any(emergency in user_input.lower() for emergency in ["chest pain", "can't breathe", "heart attack"]):
                    return f"🚨 This sounds serious{name_part}. Please call 911 immediately!"
                
                # Acknowledge the symptom with context
                if severity:
                    response_parts.append(f"I understand you're experiencing {severity} {primary_symptom}{name_part}.")
                else:
                    response_parts.append(f"I hear you're dealing with {primary_symptom}{name_part}.")
                
                # Add duration context
                if duration:
                    if duration in ["sudden", "just now"]:
                        response_parts.append("Since this just started, let's figure out what might be causing it.")
                    elif duration in ["chronic", "weeks", "months"]:
                        response_parts.append("Ongoing symptoms like this definitely deserve attention.")
                
                # Specific symptom advice
                advice = self._get_symptom_advice(primary_symptom, severity, duration)
                if advice:
                    response_parts.append(advice)
                
                # Ask for more details
                response_parts.append("Can you tell me more about what you're experiencing?")
                
            else:
                response_parts.append(f"I want to help you with your symptoms{name_part}. Can you describe what you're feeling in more detail?")
            
            return " ".join(response_parts)
        
        elif intent == "ask_medication" or intent == "medication_query":
            return f"I can provide general information about medications{name_part}, but please always consult your doctor or pharmacist for specific medical advice. What medication are you curious about?"
        
        elif intent == "wellness_tips" or intent == "ask_wellness":
            tips = [
                "Regular exercise, even just 30 minutes of walking, can boost both physical and mental health!",
                "Getting 7-9 hours of quality sleep is one of the best things you can do for your health.",
                "Staying hydrated helps with energy, skin health, and overall body function.",
                "Managing stress through deep breathing or meditation can prevent many health issues.",
                "Eating plenty of fruits and vegetables gives your body the nutrients it needs to thrive."
            ]
            return f"Here's a great wellness tip{name_part}: {random.choice(tips)} What aspect of wellness interests you most?"
        
        elif intent == "goodbye" or intent == "stop":
            if session["symptoms"]:
                return f"Take care{name_part}! Keep monitoring your symptoms and don't hesitate to see a doctor if you're concerned. Stay healthy!"
            return f"Take care{name_part}! Remember to prioritize your health. I'm here anytime you need guidance!"
        
        elif intent == "affirm":
            return f"Great{name_part}! What else would you like to know?"
        
        elif intent == "deny":
            return f"No problem{name_part}. What else can I help you with?"
        
        else:
            # Smart fallback using context
            if session.get("conversation_stage") == "greeting":
                return f"I'm here to help with your health questions{name_part}. Are you dealing with any symptoms, or do you have wellness questions?"
            else:
                return f"I want to make sure I understand you correctly{name_part}. Could you rephrase that or tell me more about what you need help with?"
    
    def _extract_symptoms_fallback(self, text):
        """Fallback symptom extraction when Rasa entities don't catch everything"""
        symptoms = []
        symptom_keywords = [
            "headache", "fever", "pain", "ache", "cough", "nausea", "dizzy", 
            "tired", "fatigue", "stomach", "chest", "breathe", "breathing"
        ]
        
        text_lower = text.lower()
        for symptom in symptom_keywords:
            if symptom in text_lower:
                symptoms.append(symptom)
        
        return symptoms
    
    def _get_symptom_advice(self, symptom, severity, duration):
        """Get specific advice for symptoms"""
        advice_map = {
            "headache": {
                "mild": "Try resting in a dark room, staying hydrated, and gentle neck stretches.",
                "severe": "This might need medical attention, especially if it's unusual for you."
            },
            "fever": {
                "mild": "Rest, fluids, and monitoring your temperature should help.",
                "severe": "High fevers over 103°F should be evaluated by a doctor."
            },
            "cough": {
                "mild": "Honey and warm water can be soothing. A humidifier might help too.",
                "severe": "If you're coughing up blood or having trouble breathing, seek medical care."
            }
        }
        
        symptom_advice = advice_map.get(symptom, {})
        if severity and severity in symptom_advice:
            return symptom_advice[severity]
        elif symptom_advice:
            return list(symptom_advice.values())[0]
        
        return None
    
    def handle(self, user_input, sid="default"):
        if sid not in self.sessions:
            self.start_session(sid)
        
        session = self.sessions[sid]
        session["history"].append(("user", user_input))
        
        # Send to Rasa for NLU processing
        rasa_payload = {
            "sender": sid,
            "message": user_input
        }
        
        rasa_response = self._send_to_rasa("/model/parse", rasa_payload)
        
        if rasa_response:
            # Parse Rasa response
            intent, confidence, entities, rasa_text = self._parse_rasa_response(rasa_response)
            entities_info = self._extract_entities_info(entities)
            
            # Generate intelligent response
            if confidence > 0.6:  # High confidence in Rasa's understanding
                bot_response = self._generate_smart_response(intent, entities_info, user_input, session)
            else:
                # Low confidence - use smart fallback
                bot_response = f"I want to make sure I understand you correctly. Are you asking about symptoms, medications, or general wellness? Feel free to be more specific!"
            
            # Log with Rasa insights
            log_turn(sid, user_input, bot_response, intent, confidence, entities_info)
            
        else:
            # Rasa is down - use basic fallback
            intent, confidence = "fallback", 0.3
            bot_response = self._smart_fallback_response(user_input, session)
            log_turn(sid, user_input, bot_response, intent, confidence)
        
        session["history"].append(("bot", bot_response))
        return bot_response
    
    def _smart_fallback_response(self, user_input, session):
        """Smart fallback when Rasa is unavailable"""
        text = user_input.lower()
        name_part = f" {session.get('user_name', '')}" if session.get('user_name') else ""
        
        # Basic pattern matching for emergencies
        if any(emergency in text for emergency in ["chest pain", "can't breathe", "heart attack", "emergency"]):
            return f"🚨 This sounds serious{name_part}. Please call 911 immediately!"
        
        # Basic symptom responses
        if any(symptom in text for symptom in ["headache", "head"]):
            return f"Headaches can be really tough{name_part}. Try resting in a dark room and staying hydrated. If it's severe or unusual, consider seeing a doctor. What seems to trigger it?"
        
        if "tired" in text or "fatigue" in text:
            return f"Being tired all the time is frustrating{name_part}. Are you getting enough sleep? Sometimes stress or poor nutrition can cause fatigue too."
        
        # Greetings
        if any(greeting in text for greeting in ["hi", "hello", "hey"]):
            return f"Hey there{name_part}! I'm your health assistant. What can I help you with today?"
        
        # General fallback
        return f"I'm here to help with your health questions{name_part}. Could you tell me more about what you're experiencing or what you'd like to know?"

def create_rasa_training_data():
    """Generate Rasa training data for health bot"""
    
    nlu_data = {
        "version": "3.1",
        "nlu": [
            {
                "intent": "greet",
                "examples": "- hey\n- hello\n- hi\n- hello there\n- good morning\n- good evening\n- moin\n- hey there\n- let's go\n- hey dude\n- goodmorning\n- goodevening\n- good afternoon"
            },
            {
                "intent": "goodbye",
                "examples": "- cu\n- good by\n- cee you later\n- good night\n- bye\n- goodbye\n- have a nice day\n- see you around\n- bye bye\n- see you later\n- thanks bye\n- thank you goodbye"
            },
            {
                "intent": "inform_symptom",
                "examples": "- I have a [headache](symptom)\n- I'm experiencing [chest pain](symptom)\n- My [stomach](body_part) [hurts](symptom)\n- I have [severe](severity) [back pain](symptom)\n- I've been having [headaches](symptom) for [two days](duration)\n- I feel [nauseous](symptom)\n- I have a [fever](symptom)\n- I'm [dizzy](symptom)\n- I can't [breathe](symptom) properly\n- I have [chronic](duration) [pain](symptom)\n- My [head](body_part) is [killing me](symptom:pain)"
            },
            {
                "intent": "ask_medication",
                "examples": "- What medication should I take?\n- Can I take ibuprofen?\n- Is it safe to take aspirin?\n- What's the dosage for paracetamol?\n- Can I mix these medications?\n- What are the side effects?\n- Should I take medicine for this?"
            },
            {
                "intent": "wellness_tips",
                "examples": "- Give me health tips\n- How to stay healthy?\n- What's good for my health?\n- Wellness advice\n- How to improve my health?\n- Health recommendations\n- Fitness tips\n- Nutrition advice"
            },
            {
                "intent": "affirm",
                "examples": "- yes\n- y\n- indeed\n- of course\n- that sounds good\n- correct\n- yes please\n- yeah\n- right\n- exactly"
            },
            {
                "intent": "deny",
                "examples": "- no\n- n\n- never\n- I don't think so\n- don't like that\n- no way\n- not really\n- nope\n- not interested"
            }
        ]
    }
    
    # Save training data
    os.makedirs("rasa_data", exist_ok=True)
    with open("rasa_data/nlu.yml", "w") as f:
        import yaml
        yaml.dump(nlu_data, f, default_flow_style=False)
    
    # Create domain file
    domain_data = {
        "version": "3.1",
        "intents": [
            "greet", "goodbye", "inform_symptom", "ask_medication", 
            "wellness_tips", "affirm", "deny"
        ],
        "entities": ["symptom", "severity", "duration", "body_part", "PERSON"],
        "responses": {
            "utter_greet": [
                {"text": "Hey! How can I help you with your health today?"}
            ],
            "utter_goodbye": [
                {"text": "Take care! Stay healthy!"}
            ]
        }
    }
    
    with open("rasa_data/domain.yml", "w") as f:
        import yaml
        yaml.dump(domain_data, f, default_flow_style=False)
    
    print("✅ Rasa training data created in 'rasa_data' folder!")
    print("📋 Next steps:")
    print("1. Install Rasa: pip install rasa")
    print("2. Train the model: rasa train --data rasa_data")
    print("3. Start Rasa server: rasa run --model models --enable-api --cors '*'")
    print("4. Run your health bot with Rasa power!")

if __name__ == "__main__":
    # Check if user wants to create Rasa training data
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "setup":
        create_rasa_training_data()
    else:
        # Run the bot
        bot = RasaHealthBot()
        sid = "demo"
        bot.start_session(sid)
        
        print("🚀 Rasa-Powered Health Bot")
        print("=" * 40)
        print("Make sure Rasa server is running on localhost:5005")
        print("Type 'exit' to quit.\n")
        
        while True:
            user_input = input("You: ")
            if user_input.lower() in ['exit', 'quit']:
                print(f"Bot: {bot.handle('goodbye', sid)}")
                break
            if user_input.strip():
                response = bot.handle(user_input, sid)
                print(f"Bot: {response}\n")