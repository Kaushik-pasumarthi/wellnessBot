import json
import joblib
import re
from typing import Dict, Tuple, Optional, List
import random

class WellnessBot:
    def __init__(self, models_dir='models', kb_file='kb.json', intents_file='bot_intents.json'):
        """Initialize the wellness bot with trained models and knowledge base."""
        self.models_dir = models_dir
        self.kb_file = kb_file
        self.intents_file = intents_file
        
        # Session context storage: session_id -> {last_entity, conversation_history, language}
        self.session_contexts = {}
        
        # Language support
        self.supported_languages = ['english', 'hindi']
        self.default_language = 'english'
        
        # Load trained models
        self.vectorizer = None
        self.classifier = None
        self.label_encoder = None
        self.load_models()
        
        # Load knowledge base and intents
        self.kb_data = self.load_knowledge_base()
        self.intents_data = self.load_intents()
        
        # Build symptom patterns for entity extraction
        self.symptom_patterns = self.build_symptom_patterns()
        
        # Initialize Hindi translations
        self.hindi_translations = self.load_hindi_translations()
        
        # Initialize disease predictor
        self.disease_predictor = None
        self.load_disease_predictor()
        
    def load_models(self):
        """Load the trained models."""
        try:
            self.vectorizer = joblib.load(f'{self.models_dir}/vectorizer.joblib')
            self.classifier = joblib.load(f'{self.models_dir}/classifier.joblib')
            self.label_encoder = joblib.load(f'{self.models_dir}/label_encoder.joblib')
            print("✅ Models loaded successfully")
        except Exception as e:
            print(f"❌ Error loading models: {e}")
            raise
    
    def load_knowledge_base(self):
        """Load the symptom knowledge base."""
        try:
            # Try to load CSV knowledge base first
            if self.load_csv_knowledge_base():
                return self.kb_data
                
            # Fallback to original kb.json
            with open(self.kb_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            print(f"✅ Knowledge base loaded with {len(data.get('symptoms', []))} symptoms")
            return data
        except Exception as e:
            print(f"❌ Error loading knowledge base: {e}")
            return {"symptoms": []}
    
    def load_csv_knowledge_base(self):
        """Load the CSV-generated comprehensive knowledge base."""
        try:
            with open('kb_csv.json', 'r', encoding='utf-8') as f:
                self.kb_data = json.load(f)
            print(f"✅ CSV knowledge base loaded with {self.kb_data['total_symptoms']} symptoms and {self.kb_data['total_diseases']} diseases")
            return True
        except Exception as e:
            print(f"⚠️ Could not load CSV knowledge base: {e}")
            return False
    
    def load_disease_predictor(self):
        """Load the disease prediction system."""
        try:
            from disease_predictor import DiseasePredictor
            self.disease_predictor = DiseasePredictor()
            if self.disease_predictor.load_models():
                print("✅ Disease prediction system loaded")
            else:
                print("⚠️ Disease prediction models not found. Run disease_predictor.py first.")
                self.disease_predictor = None
        except Exception as e:
            print(f"⚠️ Disease predictor not available: {e}")
            self.disease_predictor = None
    
    def load_intents(self):
        """Load the intents data for responses."""
        try:
            # Try with utf-8-sig first to handle BOM, then fallback to utf-8
            try:
                with open(self.intents_file, 'r', encoding='utf-8-sig') as f:
                    data = json.load(f)
            except UnicodeDecodeError:
                with open(self.intents_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            print(f"✅ Intents loaded with {len(data.get('intents', []))} intent types")
            return data
        except Exception as e:
            print(f"❌ Error loading intents: {e}")
            return {"intents": []}
    
    def build_symptom_patterns(self):
        """Build regex patterns for symptom entity extraction."""
        patterns = {}
        for symptom in self.kb_data.get('symptoms', []):
            name = symptom.get('name', '')
            synonyms = symptom.get('synonyms', [])
            
            # Create pattern from all synonyms
            all_terms = [name] + synonyms
            # Escape special regex characters and create word boundary pattern
            escaped_terms = [re.escape(term) for term in all_terms if term]
            pattern = r'\b(?:' + '|'.join(escaped_terms) + r')\b'
            patterns[name] = re.compile(pattern, re.IGNORECASE)
        
        return patterns
    
    def load_hindi_translations(self):
        """Load Hindi translations for medical terms and responses."""
        return {
            # Common medical terms
            'disease': 'रोग',
            'symptom': 'लक्षण',
            'symptoms': 'लक्षण',
            'condition': 'स्थिति',
            'diagnosis': 'निदान',
            'treatment': 'इलाज',
            'precaution': 'सावधानी',
            'precautions': 'सावधानियां',
            'description': 'विवरण',
            'confidence': 'विश्वास',
            'recommendation': 'सिफारिश',
            
            # UI elements
            'Most Likely Condition': 'सबसे संभावित स्थिति',
            'Confidence Score': 'विश्वास स्कोर',
            'Detected Symptoms': 'पहचाने गए लक्षण',
            'Confidence Level': 'विश्वास स्तर',
            'Description': 'विवरण',
            'Recommended Precautions': 'सुझाई गई सावधानियां',
            'Symptom Match Score': 'लक्षण मिलान स्कोर',
            'Total Symptom Weight': 'कुल लक्षण भार',
            'Enhanced Medical Assessment': 'उन्नत चिकित्सा मूल्यांकन',
            'Most likely condition based on your symptoms': 'आपके लक्षणों के आधार पर सबसे संभावित स्थिति',
            
            # Confidence levels
            'Very High': 'बहुत उच्च',
            'High': 'उच्च',
            'Moderate': 'मध्यम',
            'Low-Moderate': 'कम-मध्यम',
            'Low': 'कम',
            
            # Common responses
            'I understand you are experiencing': 'मैं समझता हूं कि आप अनुभव कर रहे हैं',
            'Here is what I recommend': 'यहां मेरी सिफारिश है',
            'Please consult a healthcare professional': 'कृपया एक स्वास्थ्य सेवा पेशेवर से परामर्श लें',
            'This is AI-based analysis': 'यह AI-आधारित विश्लेषण है',
            'Important': 'महत्वपूर्ण',
            'Note': 'नोट',
            
            # Disease names (common ones)
            'Arthritis': 'गठिया',
            'Heart attack': 'दिल का दौरा',
            'Drug Reaction': 'दवा की प्रतिक्रिया',
            'Hepatitis D': 'हेपेटाइटिस डी',
            'Diabetes': 'मधुमेह',
            'Hypertension': 'उच्च रक्तचाप',
            'Migraine': 'माइग्रेन',
            'Pneumonia': 'निमोनिया',
            'Bronchial Asthma': 'ब्रोन्कियल अस्थमा',
            'Malaria': 'मलेरिया',
            'Typhoid': 'टाइफाइड',
            'Common Cold': 'सामान्य सर्दी',
            'Gastroenteritis': 'गैस्ट्रोएंटेराइटिस',
            'Urinary tract infection': 'मूत्र पथ संक्रमण',
            
            # Common symptoms
            'fever': 'बुखार',
            'headache': 'सिरदर्द',
            'cough': 'खांसी',
            'cold': 'सर्दी',
            'pain': 'दर्द',
            'nausea': 'मतली',
            'vomiting': 'उल्टी',
            'diarrhea': 'दस्त',
            'chest pain': 'छाती में दर्द',
            'back pain': 'पीठ दर्द',
            'joint pain': 'जोड़ों का दर्द',
            'stomach pain': 'पेट दर्द',
            'stomach_pain': 'पेट_दर्द',
            'muscle weakness': 'मांसपेशी कमजोरी',
            'breathlessness': 'सांस लेने में कठिनाई',
            'high fever': 'तेज बुखार',
            'abdominal pain': 'पेट में दर्द',
            'swelling_of_stomach': 'पेट_की_सूजन',
            'chest_pain': 'छाती_दर्द',
            
            # Action words and instructions
            'stop irritation': 'जलन रोकें',
            'consult nearest hospital': 'निकटतम अस्पताल से सलाह लें',
            'stop taking drug': 'दवा लेना बंद करें',
            'follow up': 'फॉलो अप करें',
            'Rest the affected area': 'प्रभावित क्षेत्र को आराम दें',
            'avoid strenuous activities': 'कठिन गतिविधियों से बचें',
            'Apply ice or heat as appropriate': 'आवश्यकतानुसार बर्फ या गर्मी लगाएं',
            'If symptoms persist': 'यदि लक्षण बने रहें',
            'worsen': 'बिगड़ जाएं',
            'you experience severe discomfort': 'आप गंभीर परेशानी महसूस करें',
            'consult a healthcare professional promptly': 'तुरंत स्वास्थ्य सेवा पेशेवर से सलाह लें',
            
            # Additional medical terms
            'This is general advice based on symptom analysis': 'यह लक्षण विश्लेषण के आधार पर सामान्य सलाह है',
            'Please consult a healthcare professional for proper diagnosis and treatment': 'उचित निदान और इलाज के लिए कृपया किसी स्वास्थ्य सेवा पेशेवर से सलाह लें',
            
            # Medical descriptions (short versions)
            'An adverse drug reaction (ADR) is an injury caused by taking medication': 'दवा की प्रतिक्रिया (ADR) दवा लेने से होने वाली चोट है',
            'The death of heart muscle due to the loss of blood supply': 'रक्त आपूर्ति की कमी के कारण हृदय की मांसपेशी की मृत्यु',
            'Arthritis is the swelling and tenderness of one or more of your joints': 'गठिया एक या अधिक जोड़ों की सूजन और कोमलता है',
            
            # Greetings and responses
            'Hello': 'नमस्ते',
            'How can I help you today?': 'आज मैं आपकी कैसे सहायता कर सकता हूं?',
            'Thank you': 'धन्यवाद',
            'You are welcome': 'आपका स्वागत है',
            'Goodbye': 'अलविदा',
            'Take care': 'अपना ख्याल रखें'
        }
    
    def translate_to_hindi(self, text):
        """Translate English text to Hindi using the translation dictionary."""
        if not text:
            return text
            
        # Try exact match first
        if text in self.hindi_translations:
            return self.hindi_translations[text]
        
        # Try word-by-word translation for compound phrases
        words = text.split()
        translated_words = []
        
        for word in words:
            # Remove punctuation for translation
            clean_word = word.strip('.,!?:;')
            if clean_word in self.hindi_translations:
                translated_words.append(self.hindi_translations[clean_word])
            else:
                translated_words.append(word)  # Keep original if no translation
        
        return ' '.join(translated_words)
    
    def translate_complex_text_to_hindi(self, text):
        """Translate complex medical advice text to Hindi."""
        if not text:
            return text
        
        # Define comprehensive translation patterns for medical advice
        translations = {
            'Rest the affected area and avoid strenuous activities': 'प्रभावित क्षेत्र को आराम दें और कठिन गतिविधियों से बचें',
            'Apply ice or heat as appropriate': 'आवश्यकतानुसार बर्फ या गर्मी लगाएं',
            'If symptoms persist, worsen, or you experience severe discomfort': 'यदि लक्षण बने रहें, बिगड़ जाएं, या आप गंभीर परेशानी महसूस करें',
            'consult a healthcare professional promptly': 'तुरंत स्वास्थ्य सेवा पेशेवर से सलाह लें',
            'Rest the affected area': 'प्रभावित क्षेत्र को आराम दें',
            'avoid strenuous activities': 'कठिन गतिविधियों से बचें',
            'If symptoms persist': 'यदि लक्षण बने रहें',
            'worsen': 'बिगड़ जाएं',
            'you experience severe discomfort': 'आप गंभीर परेशानी महसूस करें'
        }
        
        # Try to translate the entire text first
        if text.strip() in translations:
            return translations[text.strip()]
        
        # If not found, try partial translations
        result = text
        for english, hindi in translations.items():
            result = result.replace(english, hindi)
        
        # Additional word-by-word translations
        for english, hindi in self.hindi_translations.items():
            result = result.replace(english, hindi)
            
        return result
    
    def set_language(self, session_id, language):
        """Set language preference for a session."""
        if session_id not in self.session_contexts:
            self.session_contexts[session_id] = {
                'last_entity': None,
                'conversation_history': [],
                'language': language
            }
        else:
            self.session_contexts[session_id]['language'] = language
    
    def get_language(self, session_id):
        """Get language preference for a session."""
        if session_id in self.session_contexts:
            return self.session_contexts[session_id].get('language', self.default_language)
        return self.default_language
    
    def predict_intent(self, user_input: str) -> Tuple[str, float]:
        """Predict intent with confidence score."""
        try:
            # Vectorize the input
            X = self.vectorizer.transform([user_input])
            
            # Get prediction and confidence
            prediction = self.classifier.predict(X)[0]
            probabilities = self.classifier.predict_proba(X)[0]
            confidence = max(probabilities)
            
            # Decode the prediction
            intent = self.label_encoder.inverse_transform([prediction])[0]
            
            return intent, confidence
        except Exception as e:
            print(f"❌ Error predicting intent: {e}")
            return "fallback", 0.0
    
    def extract_symptom_entities(self, user_input: str) -> List[str]:
        """Extract symptom entities from user input."""
        found_symptoms = []
        
        for symptom_name, pattern in self.symptom_patterns.items():
            if pattern.search(user_input):
                found_symptoms.append(symptom_name)
        
        return found_symptoms
    
    def get_symptom_advice(self, symptom_name: str) -> str:
        """Get advice for a specific symptom from knowledge base."""
        for symptom in self.kb_data.get('symptoms', []):
            if symptom.get('name') == symptom_name:
                return symptom.get('advice', 'No specific advice available for this symptom.')
        return 'Symptom not found in knowledge base.'
    
    def get_response_by_intent(self, intent: str) -> str:
        """Get a random response for a given intent."""
        for intent_data in self.intents_data.get('intents', []):
            if intent_data.get('tag') == intent:
                responses = intent_data.get('responses', [])
                if responses:
                    return random.choice(responses)
        return "I'm not sure how to help with that."
    
    def update_session_context(self, session_id: str, entities: List[str]):
        """Update session context with new entities."""
        if session_id not in self.session_contexts:
            self.session_contexts[session_id] = {
                'last_entity': None,
                'conversation_history': []
            }
        
        if entities:
            self.session_contexts[session_id]['last_entity'] = entities[-1]  # Store the last mentioned symptom
        
        # Keep conversation history limited
        if len(self.session_contexts[session_id]['conversation_history']) > 10:
            self.session_contexts[session_id]['conversation_history'] = \
                self.session_contexts[session_id]['conversation_history'][-10:]
    
    def get_last_symptom(self, session_id: str) -> Optional[str]:
        """Get the last mentioned symptom from session context."""
        if session_id in self.session_contexts:
            return self.session_contexts[session_id].get('last_entity')
        return None
    
    def reply(self, user_input: str, session_id: str) -> str:
        """
        Main function to generate bot reply based on user input and session.
        
        Args:
            user_input (str): User's message
            session_id (str): Unique session identifier
            
        Returns:
            str: Bot's response
        """
        # Predict intent with confidence
        intent, confidence = self.predict_intent(user_input)
        
        # Extract symptom entities
        entities = self.extract_symptom_entities(user_input)
        
        # Update session context
        self.update_session_context(session_id, entities)
        
        # Log for debugging
        print(f"🤖 Intent: {intent} (confidence: {confidence:.2f})")
        print(f"🎯 Entities: {entities}")
        
        # Generate response based on intent and entities
        response = self.generate_response(intent, confidence, entities, session_id, user_input)
        
        # Add to conversation history
        if session_id in self.session_contexts:
            self.session_contexts[session_id]['conversation_history'].append({
                'user_input': user_input,
                'intent': intent,
                'entities': entities,
                'response': response
            })
        
        return response
    
    def generate_response(self, intent: str, confidence: float, entities: List[str], 
                         session_id: str, user_input: str) -> str:
        """Generate appropriate response based on intent and context."""
        
        # Handle specific intents even with lower confidence
        high_priority_intents = ["greet", "goodbye", "thanks"]
        symptom_related_intents = ["report_symptom", "symptom_duration", "symptom_severity", "ask_info"]
        
        # Check if we have entities detected (symptom mentioned)
        has_entities = len(entities) > 0
        
        # Check for duration/severity keywords in input
        duration_keywords = ["how long", "duration", "last", "persist", "continue", "time"]
        severity_keywords = ["how bad", "severe", "pain level", "intensity", "worse", "better"]
        has_duration_keywords = any(keyword in user_input.lower() for keyword in duration_keywords)
        has_severity_keywords = any(keyword in user_input.lower() for keyword in severity_keywords)
        
        # Low confidence handling with better logic
        if confidence < 0.15:
            # If we have entities, still try to help with symptoms
            if has_entities:
                intent = "report_symptom"  # Override low confidence if we detect symptoms
            elif has_duration_keywords:
                intent = "symptom_duration"  # Override for duration questions
            elif has_severity_keywords:
                intent = "symptom_severity"  # Override for severity questions
            else:
                return "I'm not quite sure what you mean. Could you please rephrase your question or describe your symptoms more clearly?"
        elif confidence < 0.25 and intent not in high_priority_intents and intent not in symptom_related_intents:
            # For non-priority intents with low confidence, check for entity override
            if has_entities:
                intent = "report_symptom"
            elif has_duration_keywords:
                intent = "symptom_duration"
            elif has_severity_keywords:
                intent = "symptom_severity"
            else:
                return "I'm not quite sure what you mean. Could you please rephrase your question or describe your symptoms more clearly?"
        
        # Handle greetings
        if intent == "greet":
            language = self.get_language(session_id)
            if language == 'hindi':
                return "नमस्ते! मैं आपका स्वास्थ्य सहायक हूं। आज मैं आपकी कैसे सहायता कर सकता हूं? कृपया अपने लक्षणों के बारे में बताएं।"
            return self.get_response_by_intent("greet")
        
        # Handle goodbyes
        elif intent == "goodbye":
            language = self.get_language(session_id)
            if language == 'hindi':
                return "अलविदा! अपना ख्याल रखें और स्वस्थ रहें। यदि आपको कोई और सहायता चाहिए तो कभी भी पूछें।"
            return self.get_response_by_intent("goodbye")
        
        # Handle thanks
        elif intent == "thanks":
            language = self.get_language(session_id)
            if language == 'hindi':
                return "आपका स्वागत है! मुझे खुशी है कि मैं आपकी सहायता कर सका। स्वस्थ रहें!"
            return self.get_response_by_intent("thanks")
        
        # Handle symptom reporting
        elif intent == "report_symptom":
            if entities:
                # Provide advice for the first found entity
                symptom = entities[0]
                advice = self.get_symptom_advice(symptom)
                
                # Try disease prediction if available
                disease_info = ""
                if self.disease_predictor:
                    try:
                        predictions = self.disease_predictor.predict_diseases(user_input, top_k=1)  # Only get top 1 result
                        if predictions:
                            pred = predictions[0]  # Get only the most confident prediction
                            confidence_pct = pred['confidence'] * 100
                            
                            disease_info = "\n\n🏥 **Enhanced Medical Assessment:**\n"
                            disease_info += f"\n**🎯 Most Likely Condition:** {pred['disease']}\n"
                            disease_info += f"**📊 Confidence Score:** {confidence_pct:.1f}%\n"
                            disease_info += f"**🔍 Detected Symptoms:** {', '.join(pred['detected_symptoms'])}\n"
                            
                            # Add confidence level interpretation
                            if confidence_pct >= 80:
                                confidence_level = "Very High 🔥"
                            elif confidence_pct >= 60:
                                confidence_level = "High ✅"
                            elif confidence_pct >= 40:
                                confidence_level = "Moderate ⚠️"
                            elif confidence_pct >= 20:
                                confidence_level = "Low-Moderate 📊"
                            else:
                                confidence_level = "Low 💡"
                            
                            disease_info += f"**💯 Confidence Level:** {confidence_level}\n\n"
                            disease_info += f"**� Description:** {pred['description'][:200]}...\n"
                            
                            if pred['precautions']:
                                disease_info += f"\n**⚠️ Recommended Precautions:**\n"
                                for i, precaution in enumerate(pred['precautions'][:4], 1):
                                    disease_info += f"  {i}. {precaution}\n"
                            
                            # Show enhanced diagnostic info
                            if 'symptom_match_score' in pred:
                                disease_info += f"\n**🔗 Symptom Match Score:** {pred['symptom_match_score']:.2f}/0.5\n"
                            if 'total_symptom_weight' in pred:
                                disease_info += f"**⚖️ Total Symptom Weight:** {pred['total_symptom_weight']:.1f}\n"
                    except Exception as e:
                        print(f"Error in disease prediction: {e}")
                
                # Format response based on language
                language = self.get_language(session_id)
                
                if language == 'hindi':
                    # Translate advice to Hindi
                    advice_hindi = self.translate_complex_text_to_hindi(advice)
                    
                    # Translate disease info to Hindi if it exists
                    if disease_info:
                        # Apply Hindi translations to the medical assessment
                        disease_info = disease_info.replace("Enhanced Medical Assessment", self.translate_to_hindi('Enhanced Medical Assessment'))
                        disease_info = disease_info.replace("Most Likely Condition", self.translate_to_hindi('Most Likely Condition'))
                        disease_info = disease_info.replace("Confidence Score", self.translate_to_hindi('Confidence Score'))  
                        disease_info = disease_info.replace("Detected Symptoms", self.translate_to_hindi('Detected Symptoms'))
                        disease_info = disease_info.replace("Confidence Level", self.translate_to_hindi('Confidence Level'))
                        disease_info = disease_info.replace("Description", self.translate_to_hindi('Description'))
                        disease_info = disease_info.replace("Recommended Precautions", self.translate_to_hindi('Recommended Precautions'))
                        disease_info = disease_info.replace("Symptom Match Score", self.translate_to_hindi('Symptom Match Score'))
                        disease_info = disease_info.replace("Total Symptom Weight", self.translate_to_hindi('Total Symptom Weight'))
                        disease_info = disease_info.replace("Very High", self.translate_to_hindi('Very High'))
                        disease_info = disease_info.replace("High", self.translate_to_hindi('High'))
                        disease_info = disease_info.replace("Moderate", self.translate_to_hindi('Moderate'))
                        disease_info = disease_info.replace("Low-Moderate", self.translate_to_hindi('Low-Moderate'))
                        disease_info = disease_info.replace("Low", self.translate_to_hindi('Low'))
                        
                        # Translate disease names
                        for eng_disease, hindi_disease in self.hindi_translations.items():
                            if eng_disease in ['Arthritis', 'Heart attack', 'Drug Reaction', 'Hepatitis D', 'Diabetes', 'Hypertension', 'Migraine', 'Pneumonia', 'Bronchial Asthma', 'Malaria', 'Typhoid', 'Common Cold', 'Gastroenteritis', 'Urinary tract infection']:
                                disease_info = disease_info.replace(eng_disease, hindi_disease)
                        
                        # Translate symptom names (including underscored versions)
                        symptom_translations = {
                            'chest_pain': 'छाती_दर्द',
                            'stomach_pain': 'पेट_दर्द', 
                            'swelling_of_stomach': 'पेट_की_सूजन',
                            'nausea': 'मतली',
                            'breathlessness': 'सांस_लेने_में_कठिनाई',
                            'muscle_weakness': 'मांसपेशी_कमजोरी',
                            'back_pain': 'पीठ_दर्द',
                            'joint_pain': 'जोड़ों_का_दर्द',
                            'high_fever': 'तेज_बुखार',
                            'headache': 'सिरदर्द',
                            'fever': 'बुखार',
                            'cough': 'खांसी'
                        }
                        
                        for eng_symptom, hindi_symptom in symptom_translations.items():
                            disease_info = disease_info.replace(eng_symptom, hindi_symptom)
                        
                        # Translate common precautions
                        precaution_translations = {
                            'stop irritation': 'जलन रोकें',
                            'consult nearest hospital': 'निकटतम अस्पताल से सलाह लें',
                            'stop taking drug': 'दवा लेना बंद करें',
                            'follow up': 'फॉलो अप करें',
                            'call ambulance': 'एम्बुलेंस बुलाएं',
                            'chew or swallow asprin': 'एस्प्रिन चबाएं या निगलें',
                            'keep calm': 'शांत रहें',
                            'exercise': 'व्यायाम करें',
                            'use hot and cold therapy': 'गर्म और ठंडी चिकित्सा का उपयोग करें',
                            'try acupuncture': 'एक्यूपंक्चर करें',
                            'massage': 'मालिश करें',
                            'consult doctor': 'डॉक्टर से सलाह लें',
                            'medication': 'दवा',
                            'eat healthy': 'स्वस्थ भोजन करें'
                        }
                        
                        for eng_precaution, hindi_precaution in precaution_translations.items():
                            disease_info = disease_info.replace(eng_precaution, hindi_precaution)
                        
                        # Translate medical descriptions
                        for eng_desc, hindi_desc in self.hindi_translations.items():
                            if 'adverse drug reaction' in eng_desc.lower() or 'heart muscle' in eng_desc.lower() or 'arthritis' in eng_desc.lower():
                                disease_info = disease_info.replace(eng_desc, hindi_desc)
                    
                    understanding_text = f"{self.translate_to_hindi('I understand you are experiencing')} {self.translate_to_hindi(symptom)}। "
                    recommendation_text = f"{self.translate_to_hindi('Here is what I recommend')}:"
                    important_text = f"⚠️ **{self.translate_to_hindi('Important')}:** यह लक्षण विश्लेषण के आधार पर सामान्य सलाह है। उचित निदान और इलाज के लिए कृपया किसी स्वास्थ्य सेवा पेशेवर से सलाह लें।"
                    return f"{understanding_text}{recommendation_text}\n\n{advice_hindi}{disease_info}\n\n{important_text}"
                else:
                    return f"I understand you're experiencing {symptom}. Here's what I recommend:\n\n{advice}{disease_info}\n\n⚠️ **Important:** This is general advice based on symptom analysis. Please consult a healthcare professional for proper diagnosis and treatment."
            else:
                # No entities detected by traditional extractor, but try disease prediction anyway
                disease_info = ""
                detected_symptoms = []
                
                if self.disease_predictor:
                    try:
                        predictions = self.disease_predictor.predict_diseases(user_input, top_k=1)  # Only get top result
                        if predictions and len(predictions) > 0:
                            # Show only the most confident prediction
                            pred = predictions[0]
                            detected_symptoms = pred.get('detected_symptoms', [])
                            confidence_pct = pred['confidence'] * 100
                            
                            disease_info = "🏥 **Enhanced Medical Assessment Results:**\n\n"
                            disease_info += f"**🎯 Most Likely Condition:** {pred['disease']}\n"
                            disease_info += f"**📊 Confidence Score:** {confidence_pct:.1f}%\n"
                            disease_info += f"**🔍 Detected Symptoms:** {', '.join(detected_symptoms)}\n"
                            
                            # Add confidence level interpretation
                            if confidence_pct >= 80:
                                confidence_level = "Very High 🔥"
                            elif confidence_pct >= 60:
                                confidence_level = "High ✅"
                            elif confidence_pct >= 40:
                                confidence_level = "Moderate ⚠️"
                            elif confidence_pct >= 20:
                                confidence_level = "Low-Moderate 📊"
                            else:
                                confidence_level = "Low 💡"
                            
                            disease_info += f"**💯 Confidence Level:** {confidence_level}\n\n"
                            disease_info += f"**📝 Description:** {pred['description'][:200]}...\n"
                            
                            if pred['precautions']:
                                disease_info += f"\n**⚠️ Recommended Precautions:**\n"
                                for i, precaution in enumerate(pred['precautions'][:4], 1):
                                    disease_info += f"  {i}. {precaution}\n"
                            
                            # Show enhanced diagnostic info
                            if 'symptom_match_score' in pred:
                                disease_info += f"\n**🔗 Symptom Match Score:** {pred['symptom_match_score']:.2f}/0.5\n"
                            if 'total_symptom_weight' in pred:
                                disease_info += f"**⚖️ Total Symptom Weight:** {pred['total_symptom_weight']:.1f}\n"
                            
                            disease_info += "\n⚠️ **Important:** This is AI-based analysis. Please consult a healthcare professional for proper diagnosis and treatment."
                            
                            return disease_info
                    except Exception as e:
                        print(f"Error in disease prediction: {e}")
                
                # If no disease prediction available or no symptoms detected
                return "I can help with symptoms, but I need more specific information. Could you tell me exactly what symptoms you're experiencing? For example: headache, fever, cough, nausea, etc."
        
        # Handle information requests
        elif intent == "ask_info":
            last_symptom = self.get_last_symptom(session_id)
            if last_symptom:
                advice = self.get_symptom_advice(last_symptom)
                return f"Based on our previous conversation about {last_symptom}, here's additional advice:\n\n{advice}\n\nIs there anything specific about {last_symptom} you'd like to know more about?"
            else:
                return "I'd be happy to provide health information! What specific symptom or health topic would you like to know about?"
        
        # Handle symptom duration questions
        elif intent == "symptom_duration":
            last_symptom = self.get_last_symptom(session_id)
            if last_symptom:
                advice = self.get_symptom_advice(last_symptom)
                return f"For {last_symptom}, the duration can vary depending on the cause. Here's what I recommend:\n\n{advice}\n\nIf symptoms persist for more than a few days or worsen, please consult a healthcare professional."
            else:
                return "Could you tell me which symptom you're asking about the duration of? I can provide better guidance about how long it typically lasts and when to seek help."
        
        # Handle symptom severity questions
        elif intent == "symptom_severity":
            last_symptom = self.get_last_symptom(session_id)
            if last_symptom:
                return f"Regarding the severity of {last_symptom}, it's important to monitor how it affects your daily activities. If it's severe, persistent, or concerning you, please don't hesitate to contact a healthcare provider."
            else:
                return "I'd like to help assess severity, but could you specify which symptom you're concerned about?"
        
        # Handle fallback cases
        else:
            fallback_responses = [
                "I'm sorry, I didn't quite understand that. Could you please rephrase your question?",
                "I'm here to help with health-related questions. Could you tell me about any symptoms you're experiencing?",
                "I'd like to help! Try asking about specific symptoms like headache, fever, cough, or other health concerns.",
                "I specialize in providing basic health information. What symptoms or health topics can I help you with?"
            ]
            return random.choice(fallback_responses)

# Global bot instance
wellness_bot = None

def initialize_bot():
    """Initialize the global bot instance."""
    global wellness_bot
    if wellness_bot is None:
        wellness_bot = WellnessBot()
    return wellness_bot

def reply(user_input: str, session_id: str) -> str:
    """
    Main function to get bot reply.
    
    Args:
        user_input (str): User's message
        session_id (str): Unique session identifier
        
    Returns:
        str: Bot's response
    """
    bot = initialize_bot()
    return bot.reply(user_input, session_id)

# Example usage and testing
if __name__ == "__main__":
    # Initialize bot
    bot = initialize_bot()
    
    # Test conversations
    test_sessions = [
        ("user1", "Hello"),
        ("user1", "I have a headache"),
        ("user1", "How can I feel better?"),
        ("user2", "Hi there"),
        ("user2", "I'm feeling dizzy and nauseous"),
        ("user2", "How long does this usually last?"),
        ("user1", "Thank you for the help"),
        ("user1", "Goodbye"),
    ]
    
    print("🤖 Wellness Bot Test Conversation")
    print("=" * 50)
    
    for session_id, message in test_sessions:
        print(f"\n👤 [{session_id}]: {message}")
        response = reply(message, session_id)
        print(f"🤖 Bot: {response}")
    
    print("\n" + "=" * 50)
    print("✅ Test completed!")
