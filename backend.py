from flask import Flask, request, jsonify
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import json
import re
import string
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import numpy as np

class IntentRecognizer:
    """
    Intent Recognition class using TF-IDF + Logistic Regression
    """
    
    def __init__(self, intents_file='bot_intents.json'):
        """
        Initialize the IntentRecognizer
        
        Args:
            intents_file (str): Path to the intents JSON file
        """
        self.intents_file = intents_file
        self.vectorizer = TfidfVectorizer(
            max_features=1000,
            ngram_range=(1, 2),
            stop_words='english',
            lowercase=True
        )
        self.classifier = LogisticRegression(
            max_iter=1000,
            random_state=42
        )
        self.label_encoder = LabelEncoder()
        self.intents_data = None
        self.is_trained = False
        
        # Load and train on initialization
        self.load_intents()
        self.train_model()
    
    def load_intents(self):
        """Load intents from JSON file"""
        try:
            with open(self.intents_file, 'r', encoding='utf-8') as f:
                self.intents_data = json.load(f)
            print(f"✅ Loaded {len(self.intents_data.get('intents', []))} intents")
        except FileNotFoundError:
            print(f"❌ Error: {self.intents_file} not found")
            self.intents_data = {"intents": []}
        except json.JSONDecodeError:
            print(f"❌ Error: Invalid JSON in {self.intents_file}")
            self.intents_data = {"intents": []}
    
    def preprocess_text(self, text):
        """
        Preprocess text: lowercase, remove punctuation
        
        Args:
            text (str): Input text
            
        Returns:
            str: Preprocessed text
        """
        if not text:
            return ""
        
        # Convert to lowercase
        text = text.lower()
        
        # Remove punctuation
        text = text.translate(str.maketrans('', '', string.punctuation))
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def prepare_training_data(self):
        """
        Extract and preprocess training data from intents
        
        Returns:
            tuple: (texts, labels) for training
        """
        texts = []
        labels = []
        
        for intent in self.intents_data.get('intents', []):
            tag = intent.get('tag')
            patterns = intent.get('patterns', [])
            
            if not tag or not patterns:
                continue
                
            for pattern in patterns:
                if pattern.strip():  # Only add non-empty patterns
                    preprocessed_text = self.preprocess_text(pattern)
                    if preprocessed_text:  # Only add if preprocessing didn't remove everything
                        texts.append(preprocessed_text)
                        labels.append(tag)
        
        return texts, labels
    
    def train_model(self):
        """Train the intent classification model"""
        print("🤖 Training intent recognition model...")
        
        # Prepare training data
        texts, labels = self.prepare_training_data()
        
        if len(texts) == 0:
            print("❌ No training data available")
            return
        
        if len(set(labels)) < 2:
            print("❌ Need at least 2 different intent classes for training")
            return
        
        print(f"📊 Training data: {len(texts)} samples, {len(set(labels))} classes")
        
        # Encode labels
        y = self.label_encoder.fit_transform(labels)
        
        # Vectorize texts
        X = self.vectorizer.fit_transform(texts)
        
        # Split data for evaluation
        if len(texts) > 4:  # Only split if we have enough data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42, stratify=y
            )
            
            # Train classifier
            self.classifier.fit(X_train, y_train)
            
            # Evaluate
            y_pred = self.classifier.predict(X_test)
            accuracy = accuracy_score(y_test, y_pred)
            print(f"🎯 Model accuracy: {accuracy:.2f}")
        else:
            # Train on all data if dataset is too small
            self.classifier.fit(X, y)
            print("📝 Trained on full dataset (small dataset)")
        
        self.is_trained = True
        print("✅ Intent recognition model trained successfully!")
    
    def predict_intent(self, user_input):
        """
        Predict the most likely intent for user input
        
        Args:
            user_input (str): User's input text
            
        Returns:
            dict: {
                'intent': str,
                'confidence': float,
                'all_probabilities': dict
            }
        """
        if not self.is_trained:
            return {
                'intent': 'unknown',
                'confidence': 0.0,
                'all_probabilities': {}
            }
        
        if not user_input or not user_input.strip():
            return {
                'intent': 'unknown',
                'confidence': 0.0,
                'all_probabilities': {}
            }
        
        # Preprocess input
        processed_input = self.preprocess_text(user_input)
        
        if not processed_input:
            return {
                'intent': 'unknown',
                'confidence': 0.0,
                'all_probabilities': {}
            }
        
        try:
            # Vectorize input
            X = self.vectorizer.transform([processed_input])
            
            # Get prediction and probabilities
            prediction = self.classifier.predict(X)[0]
            probabilities = self.classifier.predict_proba(X)[0]
            
            # Decode prediction
            predicted_intent = self.label_encoder.inverse_transform([prediction])[0]
            confidence = max(probabilities)
            
            # Get all probabilities
            all_probs = {}
            for i, prob in enumerate(probabilities):
                intent_name = self.label_encoder.inverse_transform([i])[0]
                all_probs[intent_name] = float(prob)
            
            return {
                'intent': predicted_intent,
                'confidence': float(confidence),
                'all_probabilities': all_probs
            }
            
        except Exception as e:
            print(f"❌ Error predicting intent: {e}")
            return {
                'intent': 'unknown',
                'confidence': 0.0,
                'all_probabilities': {}
            }
    
    def get_intent_info(self, intent_name):
        """
        Get information about a specific intent
        
        Args:
            intent_name (str): Name of the intent
            
        Returns:
            dict: Intent information or None if not found
        """
        for intent in self.intents_data.get('intents', []):
            if intent.get('tag') == intent_name:
                return intent
        return None
    
    def get_response_for_intent(self, intent_name):
        """
        Get a random response for a given intent
        
        Args:
            intent_name (str): Name of the intent
            
        Returns:
            str: Random response or default message
        """
        intent_info = self.get_intent_info(intent_name)
        if intent_info and intent_info.get('responses'):
            import random
            return random.choice(intent_info['responses'])
        return "I'm not sure how to respond to that."

class EntityExtractor:
    """
    Entity Extraction class for symptom recognition from knowledge base
    """
    
    def __init__(self, kb_file='kb.json'):
        """
        Initialize the EntityExtractor
        
        Args:
            kb_file (str): Path to the knowledge base JSON file
        """
        self.kb_file = kb_file
        self.kb_data = None
        self.symptom_patterns = {}
        
        # Load knowledge base and build patterns
        self.load_knowledge_base()
        self.build_symptom_patterns()
    
    def load_knowledge_base(self):
        """Load knowledge base from JSON file"""
        try:
            # Try to load CSV knowledge base first
            try:
                with open('kb_csv.json', 'r', encoding='utf-8') as f:
                    self.kb_data = json.load(f)
                print(f"✅ Loaded CSV knowledge base with {self.kb_data['total_symptoms']} symptoms")
                return
            except FileNotFoundError:
                print("⚠️ CSV knowledge base not found, falling back to basic KB")
            
            # Fallback to original kb.json
            with open(self.kb_file, 'r', encoding='utf-8') as f:
                self.kb_data = json.load(f)
            print(f"✅ Loaded knowledge base with {len(self.kb_data.get('symptoms', []))} symptoms")
        except FileNotFoundError:
            print(f"❌ Error: {self.kb_file} not found")
            self.kb_data = {"symptoms": []}
        except json.JSONDecodeError:
            print(f"❌ Error: Invalid JSON in {self.kb_file}")
            self.kb_data = {"symptoms": []}
    
    def preprocess_text(self, text):
        """
        Preprocess text for entity extraction
        
        Args:
            text (str): Input text
            
        Returns:
            str: Preprocessed text
        """
        if not text:
            return ""
        
        # Convert to lowercase and strip whitespace
        text = text.lower().strip()
        
        # Normalize common variations
        text = re.sub(r'\s+', ' ', text)  # Multiple spaces to single space
        
        return text
    
    def build_symptom_patterns(self):
        """Build regex patterns for symptom matching"""
        self.symptom_patterns = {}
        
        for symptom in self.kb_data.get('symptoms', []):
            name = symptom.get('name', '')
            synonyms = symptom.get('synonyms', [])
            
            if not name:
                continue
            
            # Create pattern from all synonyms (including the name itself)
            all_terms = list(set([name] + synonyms))  # Remove duplicates
            
            # Escape special regex characters and create word boundary patterns
            escaped_terms = []
            for term in all_terms:
                if term and term.strip():
                    # Escape special characters but preserve spaces
                    escaped_term = re.escape(term.strip())
                    escaped_terms.append(escaped_term)
            
            if escaped_terms:
                # Create pattern with word boundaries for exact matching
                pattern = r'\b(?:' + '|'.join(escaped_terms) + r')\b'
                self.symptom_patterns[name] = re.compile(pattern, re.IGNORECASE)
        
        print(f"📊 Built {len(self.symptom_patterns)} symptom patterns")
    
    def extract_entities(self, user_input):
        """
        Extract symptom entities from user input
        
        Args:
            user_input (str): User's input text
            
        Returns:
            list: List of canonical symptom names found in the input
        """
        if not user_input or not user_input.strip():
            return []
        
        # Preprocess input
        processed_input = self.preprocess_text(user_input)
        
        if not processed_input:
            return []
        
        found_symptoms = []
        
        # Check each symptom pattern
        for symptom_name, pattern in self.symptom_patterns.items():
            if pattern.search(processed_input):
                found_symptoms.append(symptom_name)
        
        # Remove duplicates while preserving order
        unique_symptoms = []
        for symptom in found_symptoms:
            if symptom not in unique_symptoms:
                unique_symptoms.append(symptom)
        
        return unique_symptoms
    
    def extract_single_entity(self, user_input):
        """
        Extract the first symptom entity from user input
        
        Args:
            user_input (str): User's input text
            
        Returns:
            str or None: Canonical symptom name if found, else None
        """
        entities = self.extract_entities(user_input)
        return entities[0] if entities else None
    
    def get_symptom_info(self, symptom_name):
        """
        Get detailed information about a symptom
        
        Args:
            symptom_name (str): Canonical symptom name
            
        Returns:
            dict or None: Symptom information or None if not found
        """
        for symptom in self.kb_data.get('symptoms', []):
            if symptom.get('name') == symptom_name:
                return symptom
        return None
    
    def get_symptom_advice(self, symptom_name):
        """
        Get advice for a specific symptom
        
        Args:
            symptom_name (str): Canonical symptom name
            
        Returns:
            str: Advice text or default message
        """
        symptom_info = self.get_symptom_info(symptom_name)
        if symptom_info:
            return symptom_info.get('advice', 'No specific advice available for this symptom.')
        return 'Symptom not found in knowledge base.'
    
    def get_symptom_description(self, symptom_name):
        """
        Get description for a specific symptom
        
        Args:
            symptom_name (str): Canonical symptom name
            
        Returns:
            str: Description text or default message
        """
        symptom_info = self.get_symptom_info(symptom_name)
        if symptom_info:
            return symptom_info.get('description', 'No description available for this symptom.')
        return 'Symptom not found in knowledge base.'
    
    def get_all_symptoms(self):
        """
        Get list of all available symptoms
        
        Returns:
            list: List of dictionaries with symptom information
        """
        return self.kb_data.get('symptoms', [])
    
    def is_valid_symptom(self, symptom_name):
        """
        Check if a symptom name exists in the knowledge base
        
        Args:
            symptom_name (str): Symptom name to check
            
        Returns:
            bool: True if symptom exists, False otherwise
        """
        return self.get_symptom_info(symptom_name) is not None

app = Flask(__name__)
DATABASE = "users.db"

# Initialize Intent Recognizer and Entity Extractor
intent_recognizer = IntentRecognizer()
entity_extractor = EntityExtractor()

# Initialize Disease Predictor
disease_predictor = None
try:
    from disease_predictor import DiseasePredictor
    disease_predictor = DiseasePredictor()
    if disease_predictor.load_models():
        print("✅ Disease prediction system loaded in backend")
    else:
        print("⚠️ Disease prediction models not found in backend")
        disease_predictor = None
except Exception as e:
    print(f"⚠️ Disease predictor not available in backend: {e}")
    disease_predictor = None

# Initialize Wellness Bot
wellness_bot = None
try:
    from wellness_bot import WellnessBot
    wellness_bot = WellnessBot()
    print("✅ Wellness bot loaded in backend")
except Exception as e:
    print(f"⚠️ Wellness bot not available in backend: {e}")
    wellness_bot = None

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            name TEXT,
            age_group TEXT,
            language TEXT
        )
    """)
    
    conn.execute("""
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            user_message TEXT NOT NULL,
            bot_response TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (username) REFERENCES users (email)
        )
    """)
    
    conn.commit()
    conn.close()

init_db()

# Conversation management functions
def save_conversation(username, user_message, bot_response):
    """Save a conversation to the database"""
    try:
        conn = get_db_connection()
        conn.execute(
            "INSERT INTO conversations (username, user_message, bot_response) VALUES (?, ?, ?)",
            (username, user_message, bot_response)
        )
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error saving conversation: {e}")
        return False

def get_user_conversations(username, limit=50):
    """Get recent conversations for a user"""
    try:
        conn = get_db_connection()
        conversations = conn.execute(
            """SELECT user_message, bot_response, timestamp 
               FROM conversations 
               WHERE username = ? 
               ORDER BY timestamp DESC 
               LIMIT ?""",
            (username, limit)
        ).fetchall()
        conn.close()
        
        # Convert to list of dictionaries and reverse to show oldest first
        conv_list = []
        for conv in reversed(conversations):
            conv_list.append({
                "user": conv["user_message"],
                "bot": conv["bot_response"],
                "timestamp": conv["timestamp"]
            })
        
        return conv_list
    except Exception as e:
        print(f"Error fetching conversations: {e}")
        return []

def clear_user_conversations(username):
    """Clear all conversations for a user"""
    try:
        conn = get_db_connection()
        conn.execute("DELETE FROM conversations WHERE username = ?", (username,))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error clearing conversations: {e}")
        return False

# Intent Recognition API Endpoints
@app.route("/predict_intent", methods=["POST"])
def predict_intent():
    """API endpoint to predict intent from user input"""
    data = request.json
    user_input = data.get("text", "")
    
    if not user_input.strip():
        return jsonify({"success": False, "message": "Text input required"}), 400
    
    try:
        result = intent_recognizer.predict_intent(user_input)
        return jsonify({
            "success": True,
            "intent": result["intent"],
            "confidence": result["confidence"],
            "all_probabilities": result["all_probabilities"]
        })
    except Exception as e:
        return jsonify({"success": False, "message": f"Error: {str(e)}"}), 500

@app.route("/get_response", methods=["POST"])
def get_response():
    """API endpoint to get response for user input using wellness bot"""
    data = request.json
    user_input = data.get("text", "")
    session_id = data.get("session_id", "default")
    
    if not user_input.strip():
        return jsonify({"success": False, "message": "Text input required"}), 400
    
    try:
        if wellness_bot:
            # Use wellness bot for comprehensive response with disease prediction
            intent_result = intent_recognizer.predict_intent(user_input)
            entities = entity_extractor.extract_entities(user_input)
            
            response = wellness_bot.generate_response(
                intent=intent_result["intent"],
                confidence=intent_result["confidence"],
                entities=entities,
                session_id=session_id,
                user_input=user_input
            )
            
            return jsonify({
                "success": True,
                "intent": intent_result["intent"],
                "confidence": intent_result["confidence"],
                "entities": entities,
                "response": response
            })
        else:
            # Fallback to basic intent recognition
            result = intent_recognizer.predict_intent(user_input)
            intent = result["intent"]
            confidence = result["confidence"]
            
            # Get response for the intent
            response = intent_recognizer.get_response_for_intent(intent)
            
            return jsonify({
                "success": True,
                "intent": intent,
                "confidence": confidence,
                "response": response
            })
    except Exception as e:
        return jsonify({"success": False, "message": f"Error: {str(e)}"}), 500

@app.route("/intents", methods=["GET"])
def get_intents():
    """API endpoint to get all available intents"""
    try:
        intents = []
        for intent in intent_recognizer.intents_data.get('intents', []):
            intents.append({
                "tag": intent.get("tag"),
                "patterns": intent.get("patterns", []),
                "responses": intent.get("responses", [])
            })
        
        return jsonify({
            "success": True,
            "intents": intents,
            "total_intents": len(intents)
        })
    except Exception as e:
        return jsonify({"success": False, "message": f"Error: {str(e)}"}), 500

# Entity Extraction API Endpoints
@app.route("/extract_entities", methods=["POST"])
def extract_entities():
    """API endpoint to extract symptom entities from text"""
    data = request.json
    user_input = data.get("text", "")
    
    if not user_input.strip():
        return jsonify({"success": False, "message": "Text input required"}), 400
    
    try:
        entities = entity_extractor.extract_entities(user_input)
        single_entity = entity_extractor.extract_single_entity(user_input)
        
        return jsonify({
            "success": True,
            "entities": entities,
            "primary_entity": single_entity,
            "total_entities": len(entities)
        })
    except Exception as e:
        return jsonify({"success": False, "message": f"Error: {str(e)}"}), 500

@app.route("/get_symptom_info", methods=["POST"])
def get_symptom_info():
    """API endpoint to get information about a specific symptom"""
    data = request.json
    symptom_name = data.get("symptom", "")
    
    if not symptom_name.strip():
        return jsonify({"success": False, "message": "Symptom name required"}), 400
    
    try:
        symptom_info = entity_extractor.get_symptom_info(symptom_name)
        
        if symptom_info:
            return jsonify({
                "success": True,
                "symptom": symptom_info
            })
        else:
            return jsonify({
                "success": False,
                "message": "Symptom not found in knowledge base"
            }), 404
    except Exception as e:
        return jsonify({"success": False, "message": f"Error: {str(e)}"}), 500

@app.route("/get_symptom_advice", methods=["POST"])
def get_symptom_advice():
    """API endpoint to get advice for a specific symptom"""
    data = request.json
    symptom_name = data.get("symptom", "")
    
    if not symptom_name.strip():
        return jsonify({"success": False, "message": "Symptom name required"}), 400
    
    try:
        advice = entity_extractor.get_symptom_advice(symptom_name)
        description = entity_extractor.get_symptom_description(symptom_name)
        
        return jsonify({
            "success": True,
            "symptom": symptom_name,
            "advice": advice,
            "description": description
        })
    except Exception as e:
        return jsonify({"success": False, "message": f"Error: {str(e)}"}), 500

@app.route("/symptoms", methods=["GET"])
def get_all_symptoms():
    """API endpoint to get all available symptoms"""
    try:
        symptoms = entity_extractor.get_all_symptoms()
        
        # Create simplified list for API response
        symptom_list = []
        for symptom in symptoms:
            symptom_list.append({
                "name": symptom.get("name"),
                "synonyms": symptom.get("synonyms", []),
                "description": symptom.get("description", "")
            })
        
        return jsonify({
            "success": True,
            "symptoms": symptom_list,
            "total_symptoms": len(symptom_list)
        })
    except Exception as e:
        return jsonify({"success": False, "message": f"Error: {str(e)}"}), 500

@app.route("/analyze_text", methods=["POST"])
def analyze_text():
    """API endpoint to analyze text for both intent and entities"""
    data = request.json
    user_input = data.get("text", "")
    
    if not user_input.strip():
        return jsonify({"success": False, "message": "Text input required"}), 400
    
    try:
        # Get intent prediction
        intent_result = intent_recognizer.predict_intent(user_input)
        
        # Extract entities
        entities = entity_extractor.extract_entities(user_input)
        primary_entity = entity_extractor.extract_single_entity(user_input)
        
        # Get response
        response = intent_recognizer.get_response_for_intent(intent_result["intent"])
        
        return jsonify({
            "success": True,
            "text": user_input,
            "intent": {
                "name": intent_result["intent"],
                "confidence": intent_result["confidence"],
                "all_probabilities": intent_result["all_probabilities"]
            },
            "entities": {
                "all": entities,
                "primary": primary_entity,
                "count": len(entities)
            },
            "response": response
        })
    except Exception as e:
        return jsonify({"success": False, "message": f"Error: {str(e)}"}), 500

# Conversation API Endpoints
@app.route("/save_conversation", methods=["POST"])
def save_conversation_api():
    """API endpoint to save a conversation"""
    data = request.json
    username = data.get("username", "")
    user_message = data.get("user_message", "")
    bot_response = data.get("bot_response", "")
    
    if not all([username, user_message, bot_response]):
        return jsonify({"success": False, "message": "Username, user_message, and bot_response required"}), 400
    
    success = save_conversation(username, user_message, bot_response)
    
    if success:
        return jsonify({"success": True, "message": "Conversation saved successfully"})
    else:
        return jsonify({"success": False, "message": "Failed to save conversation"}), 500

@app.route("/get_conversations", methods=["GET"])
def get_conversations_api():
    """API endpoint to get user conversations"""
    username = request.args.get("username", "")
    limit = int(request.args.get("limit", 50))
    
    if not username:
        return jsonify({"success": False, "message": "Username required"}), 400
    
    conversations = get_user_conversations(username, limit)
    
    return jsonify({
        "success": True,
        "conversations": conversations,
        "total": len(conversations)
    })

@app.route("/clear_conversations", methods=["POST"])
def clear_conversations_api():
    """API endpoint to clear user conversations"""
    data = request.json
    username = data.get("username", "")
    
    if not username:
        return jsonify({"success": False, "message": "Username required"}), 400
    
    success = clear_user_conversations(username)
    
    if success:
        return jsonify({"success": True, "message": "Conversations cleared successfully"})
    else:
        return jsonify({"success": False, "message": "Failed to clear conversations"}), 500

@app.route("/signup", methods=["POST"])
def signup():
    data = request.json
    email = data.get("email")
    password = data.get("password")
    name = data.get("name")
    age_group = data.get("age_group")
    language = data.get("language")

    if not email or not password:
        return jsonify({"success": False, "message": "Email and password required"}), 400

    hashed_password = generate_password_hash(password)

    try:
        conn = get_db_connection()
        conn.execute(
            "INSERT INTO users (email, password, name, age_group, language) VALUES (?, ?, ?, ?, ?)",
            (email, hashed_password, name, age_group, language)
        )
        conn.commit()
        conn.close()
        return jsonify({"success": True, "message": "User registered successfully"})
    except sqlite3.IntegrityError:
        return jsonify({"success": False, "message": "Email already exists"}), 400

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"success": False, "message": "Email and password required"}), 400

    conn = get_db_connection()
    user = conn.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
    conn.close()

    if user and check_password_hash(user["password"], password):
        return jsonify({"success": True, "message": "Login successful"})
    return jsonify({"success": False, "message": "Invalid email or password"}), 401

@app.route("/profile", methods=["GET"])
def get_profile():
    email = request.args.get("email")
    if not email:
        return jsonify({"success": False, "message": "Email required"}), 400

    conn = get_db_connection()
    user = conn.execute("SELECT name, age_group, language FROM users WHERE email=?", (email,)).fetchone()
    conn.close()

    if user:
        profile = {
            "name": user["name"] or "",
            "age_group": user["age_group"] or "18-25",
            "language": user["language"] or "English"
        }
        return jsonify({"success": True, "profile": profile})
    else:
        return jsonify({"success": False, "message": "User not found"}), 404

@app.route("/profile", methods=["POST"])
def profile():
    data = request.json
    email = data.get("email")
    name = data.get("name")
    age_group = data.get("age_group")
    language = data.get("language")

    if not email:
        return jsonify({"success": False, "message": "Email required"}), 400

    conn = get_db_connection()
    conn.execute(
        "UPDATE users SET name=?, age_group=?, language=? WHERE email=?",
        (name, age_group, language, email)
    )
    conn.commit()
    conn.close()

    return jsonify({"success": True, "message": "Profile updated successfully"})

@app.route("/reset_password", methods=["POST"])
def reset_password():
    data = request.json
    email = data.get("email")
    old_password = data.get("old_password")
    new_password = data.get("new_password")

    if not email or not old_password or not new_password:
        return jsonify({"success": False, "message": "All fields required"}), 400

    conn = get_db_connection()
    user = conn.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()

    if user and check_password_hash(user["password"], old_password):
        hashed_new = generate_password_hash(new_password)
        conn.execute("UPDATE users SET password=? WHERE email=?", (hashed_new, email))
        conn.commit()
        conn.close()
        return jsonify({"success": True, "message": "Password updated successfully"})
    
    conn.close()
    return jsonify({"success": False, "message": "Invalid old password"}), 401

@app.route("/predict_diseases", methods=["POST"])
def predict_diseases():
    """Predict diseases based on symptoms"""
    data = request.json
    symptoms_text = data.get("symptoms", "")
    top_k = data.get("top_k", 3)
    
    if not symptoms_text:
        return jsonify({"success": False, "message": "Symptoms text required"}), 400
    
    if not disease_predictor:
        return jsonify({
            "success": False, 
            "message": "Disease prediction not available. Please train models first."
        }), 503
    
    try:
        predictions = disease_predictor.predict_diseases(symptoms_text, top_k=top_k)
        
        return jsonify({
            "success": True,
            "predictions": predictions,
            "input_text": symptoms_text
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Error predicting diseases: {str(e)}"
        }), 500

@app.route("/get_disease_info", methods=["GET"])
def get_disease_info():
    """Get information about a specific disease"""
    disease = request.args.get("disease")
    
    if not disease:
        return jsonify({"success": False, "message": "Disease name required"}), 400
    
    if not disease_predictor:
        return jsonify({
            "success": False, 
            "message": "Disease prediction not available"
        }), 503
    
    try:
        disease_info = disease_predictor.get_disease_info(disease)
        
        return jsonify({
            "success": True,
            "disease_info": disease_info
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Error getting disease info: {str(e)}"
        }), 500

@app.route("/feedback", methods=["POST"])
def submit_feedback():
    """Submit user feedback"""
    data = request.get_json()
    
    required_fields = ["name", "email", "feedback", "rating"]
    if not all(field in data for field in required_fields):
        return jsonify({
            "success": False,
            "message": "Missing required fields"
        }), 400
    
    try:
        from admin_manager import AdminManager
        admin_manager = AdminManager()
        
        # Map to the correct database schema
        admin_manager.add_feedback(
            user_email=data["email"],
            feedback_type="general",
            subject=f"Feedback from {data['name']}",
            message=data["feedback"],
            rating=int(data["rating"])
        )
        
        return jsonify({
            "success": True,
            "message": "Feedback submitted successfully"
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Error submitting feedback: {str(e)}"
        }), 500

@app.route("/review", methods=["POST"])
def submit_review():
    """Submit review after bot response"""
    data = request.get_json()
    
    required_fields = ["user_email", "bot_response", "review_type"]
    if not all(field in data for field in required_fields):
        return jsonify({
            "success": False,
            "message": "Missing required fields"
        }), 400
    
    try:
        from admin_manager import AdminManager
        admin_manager = AdminManager()
        
        # Add review to feedback table
        feedback_message = f"Bot Response: {data['bot_response']}\nUser Review: {data['review_type']}"
        if data.get('comment'):
            feedback_message += f"\nComment: {data['comment']}"
        
        admin_manager.add_feedback(
            user_email=data["user_email"],
            feedback_type="bot_review",
            subject=f"Bot Response Review - {data['review_type']}",
            message=feedback_message,
            rating=5 if data['review_type'] == 'positive' else 1
        )
        
        return jsonify({
            "success": True,
            "message": "Review submitted successfully"
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Error submitting review: {str(e)}"
        }), 500

@app.route("/admin/login", methods=["POST"])
def admin_login():
    """Admin login endpoint"""
    data = request.get_json()
    
    if not all(field in data for field in ["username", "password"]):
        return jsonify({
            "success": False,
            "message": "Username and password required"
        }), 400
    
    try:
        from admin_manager import AdminManager
        admin_manager = AdminManager()
        
        is_valid = admin_manager.authenticate_admin(
            data["username"],
            data["password"]
        )
        
        if is_valid:
            return jsonify({
                "success": True,
                "message": "Login successful"
            })
        else:
            return jsonify({
                "success": False,
                "message": "Invalid credentials"
            }), 401
    
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Error during login: {str(e)}"
        }), 500

if __name__ == "__main__":
    app.run(debug=True)