"""
Enhanced Disease Prediction System with Advanced Symptom Mapping
"""
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import joblib
import os
import json
import re
from collections import Counter

class DiseasePredictor:
    def __init__(self):
        """Initialize the disease predictor"""
        self.model = None
        self.vectorizer = None
        self.label_encoder = None
        self.disease_info = {}
        self.symptom_precautions = {}
        self.all_symptoms = []
        self.symptom_mappings = {}
        
        # Load data
        self.load_datasets()
        self._create_comprehensive_symptom_mappings()
        
        # Train model if not exists
        if not self.load_models():
            print("🤖 Training new disease prediction model...")
            self.train_model()
            self.save_models()
        
    def load_datasets(self):
        """Load all CSV datasets"""
        print("📊 Loading medical datasets...")
        
        try:
            # Load main dataset
            self.df = pd.read_csv('dataset.csv')
            print(f"✅ Loaded dataset: {len(self.df)} records")
            
            # Extract all unique symptoms
            self.all_symptoms = set()
            for i in range(len(self.df)):
                for j in range(1, 18):  # Symptom_1 to Symptom_17
                    symptom_col = f'Symptom_{j}'
                    if symptom_col in self.df.columns:
                        symptom = self.df.iloc[i][symptom_col]
                        if pd.notna(symptom) and symptom.strip():
                            self.all_symptoms.add(symptom.strip())
            
            self.all_symptoms = sorted(list(self.all_symptoms))
            print(f"✅ Extracted {len(self.all_symptoms)} unique symptoms")
            
            # Load disease descriptions
            desc_df = pd.read_csv('symptom_Description.csv')
            self.disease_info = dict(zip(desc_df['Disease'], desc_df['Description']))
            print(f"✅ Loaded descriptions for {len(self.disease_info)} diseases")
            
            # Load disease precautions
            prec_df = pd.read_csv('symptom_precaution.csv')
            for _, row in prec_df.iterrows():
                disease = row['Disease']
                precautions = [row[f'Precaution_{i}'] for i in range(1, 5) if pd.notna(row[f'Precaution_{i}'])]
                self.symptom_precautions[disease] = precautions
            print(f"✅ Loaded precautions for {len(self.symptom_precautions)} diseases")
            
        except Exception as e:
            print(f"❌ Error loading datasets: {e}")
            return False
        
        return True
    
    def _create_comprehensive_symptom_mappings(self):
        """Create comprehensive symptom mappings from natural language to dataset symptoms"""
        print("🔗 Creating comprehensive symptom mappings...")
        
        # Initialize mappings
        self.symptom_mappings = {}
        
        # Map each dataset symptom to itself and variations
        for symptom in self.all_symptoms:
            # Original symptom (exact match)
            self.symptom_mappings[symptom.lower()] = symptom
            
            # Without underscores
            if '_' in symptom:
                without_underscore = symptom.replace('_', ' ')
                self.symptom_mappings[without_underscore.lower()] = symptom
                
                # Only map meaningful multi-word phrases, not individual words
                # This prevents incorrect mappings like "feel" -> "continuous_feel_of_urine"
                if len(without_underscore.split()) >= 2:
                    words = without_underscore.lower().split()
                    for word in words:
                        if len(word) > 4 and word not in ['pain', 'feel', 'from', 'with', 'during', 'very']:  # Exclude common words
                            # Only map if it's a specific medical term
                            if word not in self.symptom_mappings or len(symptom.split('_')) >= 2:
                                self.symptom_mappings[word] = symptom
        
        # Add comprehensive medical term mappings with better context awareness
        medical_mappings = {
            # Pain variations - more specific mapping
            'joint pain': 'joint_pain',
            'muscle pain': 'muscle_pain', 
            'muscle aches': 'muscle_pain',
            'muscle ache': 'muscle_pain',
            'joint ache': 'joint_pain',
            'joint aches': 'joint_pain',
            'back pain': 'back_pain',
            'neck pain': 'neck_pain',
            'chest pain': 'chest_pain',
            'abdominal pain': 'abdominal_pain',
            'stomach pain': 'stomach_pain',
            'hip pain': 'hip_joint_pain',
            'knee pain': 'knee_pain',
            
            # Remove problematic single-word mappings
            'stiff': 'movement_stiffness',
            'stiffness': 'movement_stiffness',
            'ache': 'muscle_pain',  # Default to muscle pain for generic ache
            'aching': 'muscle_pain',
            
            # Fever variations
            'fever': 'high_fever',
            'high fever': 'high_fever',
            'mild fever': 'mild_fever',
            'temperature': 'high_fever',
            'chills': 'chills',
            'shivering': 'shivering',
            
            # Digestive issues - more specific
            'nausea': 'nausea',
            'vomiting': 'vomiting',
            'diarrhea': 'diarrhoea',
            'diarrhoea': 'diarrhoea',
            'constipation': 'constipation',
            'stomach ache': 'stomach_pain',
            'belly pain': 'belly_pain',
            'indigestion': 'indigestion',
            
            # Respiratory
            'breathing difficulty': 'breathlessness',
            'shortness of breath': 'breathlessness',
            'breathlessness': 'breathlessness',
            'cough': 'cough',
            'congestion': 'congestion',
            'runny nose': 'runny_nose',
            'sneezing': 'continuous_sneezing',
            
            # Skin issues
            'skin rash': 'skin_rash',
            'rash': 'skin_rash',
            'itching': 'itching',
            'itchy': 'itching',
            
            # Urinary symptoms - more specific
            'frequent urination': 'polyuria',
            'urinating frequently': 'polyuria',
            'polyuria': 'polyuria',
            'burning urination': 'burning_micturition',
            'burning micturition': 'burning_micturition',
            'dark urine': 'dark_urine',
            'yellow urine': 'yellow_urine',
            
            # Thirst and appetite
            'excessive thirst': 'excessive_hunger',  # Dataset uses excessive_hunger for diabetes
            'increased appetite': 'increased_appetite',
            'loss of appetite': 'loss_of_appetite',
            'excessive hunger': 'excessive_hunger',
            
            # Vision
            'blurred vision': 'blurred_and_distorted_vision',
            'blurry vision': 'blurred_and_distorted_vision',
            'vision problems': 'blurred_and_distorted_vision',
            'visual disturbances': 'visual_disturbances',
            
            # Fatigue/Weakness
            'fatigue': 'fatigue',
            'tired': 'fatigue',
            'exhausted': 'fatigue',
            'weakness': 'muscle_weakness',
            'weak': 'muscle_weakness',
            'lethargy': 'lethargy',
            
            # Head/Neurological
            'headache': 'headache',
            'head pain': 'headache',
            'migraine': 'headache',
            'dizziness': 'dizziness',
            'dizzy': 'dizziness',
            'lightheaded': 'dizziness',
            
            # Heart/Chest
            'chest pain': 'chest_pain',
            'heart pain': 'chest_pain',
            'palpitations': 'palpitations',
            'fast heart rate': 'fast_heart_rate',
            'rapid heartbeat': 'fast_heart_rate',
            
            # Weight changes
            'weight loss': 'weight_loss',
            'weight gain': 'weight_gain',
            
            # Yellow symptoms (jaundice)
            'yellow eyes': 'yellowing_of_eyes',
            'yellowing of eyes': 'yellowing_of_eyes',
            'yellow skin': 'yellowish_skin',
            'yellowish skin': 'yellowish_skin',
            'jaundice': 'yellowing_of_eyes',
            
            # Mental health
            'depression': 'depression',
            'anxiety': 'anxiety',
            'mood swings': 'mood_swings',
            'irritability': 'irritability',
            'restlessness': 'restlessness',
            
            # Sweating
            'sweating': 'sweating',
            'excessive sweating': 'sweating',
            
            # Swelling
            'swelling': 'swelling_joints',
            'swollen joints': 'swelling_joints',
            'joint swelling': 'swelling_joints',
            'swollen legs': 'swollen_legs',
        }
        
        # Update mappings with medical terms
        self.symptom_mappings.update(medical_mappings)
        
        print(f"✅ Created {len(self.symptom_mappings)} symptom mappings")
        
        # Show some sample mappings for debugging
        print(f"📋 Sample mappings:")
        sample_items = list(self.symptom_mappings.items())[:10]
        for key, value in sample_items:
            print(f"   '{key}' → '{value}'")
    
    def extract_symptoms_from_text(self, text):
        """Extract symptoms from natural language text using improved mapping"""
        text_lower = text.lower()
        detected_symptoms = []
        
        print(f"🔍 Analyzing text: '{text}'")
        
        # Method 1: Direct word matching
        words = re.findall(r'\b\w+\b', text_lower)
        
        for word in words:
            if word in self.symptom_mappings:
                mapped_symptom = self.symptom_mappings[word]
                if mapped_symptom not in detected_symptoms:
                    detected_symptoms.append(mapped_symptom)
                    print(f"   ✅ Mapped '{word}' → '{mapped_symptom}'")
        
        # Method 2: Phrase matching
        phrases_to_check = [
            text_lower,
            # Remove common words and check again
            re.sub(r'\b(i|am|have|been|feel|feeling|my|the|and|or|with|very|really|quite)\b', '', text_lower).strip(),
        ]
        
        for phrase in phrases_to_check:
            if phrase and phrase in self.symptom_mappings:
                mapped_symptom = self.symptom_mappings[phrase]
                if mapped_symptom not in detected_symptoms:
                    detected_symptoms.append(mapped_symptom)
                    print(f"   ✅ Mapped phrase '{phrase}' → '{mapped_symptom}'")
        
        # Method 3: Partial matching for compound symptoms
        for symptom_key, dataset_symptom in self.symptom_mappings.items():
            if len(symptom_key) > 4:  # Only check longer terms
                if symptom_key in text_lower and dataset_symptom not in detected_symptoms:
                    detected_symptoms.append(dataset_symptom)
                    print(f"   ✅ Partial match '{symptom_key}' → '{dataset_symptom}'")
        
        print(f"🎯 Final detected symptoms: {detected_symptoms}")
        return detected_symptoms
    
    def train_model(self):
        """Train the machine learning model with improved accuracy"""
        print("🤖 Training enhanced disease prediction model...")
        
        try:
            # Prepare training data with better feature engineering
            X = []
            y = []
            
            for index, row in self.df.iterrows():
                # Create enhanced symptom vector with weighted features
                symptom_vector = [0] * len(self.all_symptoms)
                symptom_count = 0
                
                # Mark present symptoms with enhanced weighting
                for j in range(1, 18):  # Symptom_1 to Symptom_17
                    symptom_col = f'Symptom_{j}'
                    if symptom_col in self.df.columns:
                        symptom = row[symptom_col]
                        if pd.notna(symptom) and symptom.strip():
                            symptom = symptom.strip()
                            if symptom in self.all_symptoms:
                                symptom_idx = self.all_symptoms.index(symptom)
                                
                                # Weight symptoms by position (earlier symptoms are more important)
                                weight = 1.0 + (0.1 * (18 - j))  # First symptoms get higher weight
                                symptom_vector[symptom_idx] = weight
                                symptom_count += 1
                
                # Only include records with multiple symptoms for better accuracy
                if symptom_count >= 2:
                    X.append(symptom_vector)
                    y.append(row['Disease'])
            
            X = np.array(X)
            y = np.array(y)
            
            print(f"📊 Enhanced training data: {len(X)} samples (filtered from {len(self.df)}), {len(np.unique(y))} diseases")
            
            # Encode labels
            self.label_encoder = LabelEncoder()
            y_encoded = self.label_encoder.fit_transform(y)
            
            # Check if stratification is possible (all classes need at least 2 samples)
            from collections import Counter
            class_counts = Counter(y_encoded)
            min_samples = min(class_counts.values())
            
            # Split data with stratification only if all classes have >= 2 samples
            if min_samples >= 2:
                X_train, X_test, y_train, y_test = train_test_split(
                    X, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded
                )
            else:
                print(f"⚠️ Some classes have only {min_samples} sample(s). Using random split instead of stratified.")
                X_train, X_test, y_train, y_test = train_test_split(
                    X, y_encoded, test_size=0.2, random_state=42
                )
            
            # Train enhanced model with better parameters
            self.model = RandomForestClassifier(
                n_estimators=200,  # More trees for better accuracy
                max_depth=25,      # Deeper trees
                min_samples_split=5,
                min_samples_leaf=2,
                random_state=42,
                class_weight='balanced'  # Handle class imbalance
            )
            self.model.fit(X_train, y_train)
            
            # Evaluate
            y_pred = self.model.predict(X_test)
            accuracy = accuracy_score(y_test, y_pred)
            
            # Get prediction probabilities for confidence analysis
            y_proba = self.model.predict_proba(X_test)
            avg_confidence = np.mean(np.max(y_proba, axis=1))
            
            print(f"🎯 Enhanced model accuracy: {accuracy:.3f}")
            print(f"📈 Average confidence: {avg_confidence:.3f}")
            print(f"✅ Enhanced model trained successfully!")
            
            return True
            
        except Exception as e:
            print(f"❌ Error training enhanced model: {e}")
            return False
    
    def predict_diseases(self, symptoms_text, top_k=3):
        """Predict diseases from symptom text with enhanced confidence scoring"""
        if not self.model or not self.label_encoder:
            print("❌ Model not loaded or trained")
            return []
        
        try:
            # Extract symptoms with improved accuracy
            detected_symptoms = self.extract_symptoms_from_text(symptoms_text)
            
            if not detected_symptoms:
                print("⚠️ No symptoms detected from text")
                return []
            
            # Create enhanced symptom vector with weighted features
            symptom_vector = [0] * len(self.all_symptoms)
            symptom_weights = {}
            total_weight = 0
            
            for symptom in detected_symptoms:
                if symptom in self.all_symptoms:
                    symptom_idx = self.all_symptoms.index(symptom)
                    
                    # Calculate symptom importance weight
                    base_weight = 2.0  # Increased base weight
                    
                    # Give higher weight to more specific symptoms
                    if len(symptom.replace('_', ' ').split()) > 1:
                        base_weight += 1.0  # Increased multi-word bonus
                    
                    # Weight based on symptom rarity (rarer symptoms are more diagnostic)
                    symptom_count = sum(1 for _, row in self.df.iterrows() 
                                      for j in range(1, 18) 
                                      if pd.notna(row.get(f'Symptom_{j}', '')) and 
                                         row.get(f'Symptom_{j}', '').strip() == symptom)
                    
                    if symptom_count > 0:
                        # Logarithmic scaling for rarity bonus
                        rarity_weight = min(3.0, np.log(5000 / max(symptom_count, 1)) + 1)
                        base_weight *= rarity_weight
                    
                    symptom_vector[symptom_idx] = base_weight
                    symptom_weights[symptom] = base_weight
                    total_weight += base_weight
            
            print(f"🎯 Symptom weights: {symptom_weights}")
            
            # Predict with enhanced vector
            symptom_vector = np.array(symptom_vector).reshape(1, -1)
            probabilities = self.model.predict_proba(symptom_vector)[0]
            
            # Apply significant confidence boosting
            # Multiple symptom bonus
            multi_symptom_bonus = min(0.4, len(detected_symptoms) * 0.1)  # Up to 40% bonus
            
            # Weight-based bonus (higher total weight = more confident)
            weight_bonus = min(0.3, total_weight * 0.02)  # Up to 30% bonus
            
            # Apply bonuses
            max_prob_idx = np.argmax(probabilities)
            probabilities[max_prob_idx] += multi_symptom_bonus + weight_bonus
            
            # Normalize to ensure valid probability distribution
            probabilities = probabilities / np.sum(probabilities)
            
            # Get top predictions with adaptive threshold
            top_indices = np.argsort(probabilities)[::-1][:top_k]
            
            predictions = []
            for idx in top_indices:
                confidence = probabilities[idx]
                
                # Dynamic confidence threshold based on symptom quality
                if len(detected_symptoms) >= 3:
                    min_confidence = 0.02  # Lower threshold for multiple symptoms
                elif len(detected_symptoms) == 2:
                    min_confidence = 0.03
                else:
                    min_confidence = 0.05
                
                if confidence > min_confidence:
                    disease = self.label_encoder.inverse_transform([idx])[0]
                    
                    # Additional disease-specific confidence boost
                    disease_symptom_match = self._calculate_disease_symptom_match(disease, detected_symptoms)
                    
                    # Final confidence calculation with multiple boosts
                    final_confidence = confidence * (1 + disease_symptom_match * 2)  # Doubled match bonus
                    
                    # Ensure reasonable confidence bounds
                    final_confidence = min(final_confidence, 0.98)  # Cap at 98%
                    final_confidence = max(final_confidence, confidence)  # Never reduce below base
                    
                    prediction = {
                        'disease': disease,
                        'confidence': final_confidence,
                        'detected_symptoms': detected_symptoms,
                        'description': self.disease_info.get(disease, "No description available"),
                        'precautions': self.symptom_precautions.get(disease, []),
                        'symptom_match_score': disease_symptom_match,
                        'base_confidence': confidence,
                        'total_symptom_weight': total_weight
                    }
                    predictions.append(prediction)
            
            # Sort by adjusted confidence
            predictions.sort(key=lambda x: x['confidence'], reverse=True)
            return predictions
            
        except Exception as e:
            print(f"❌ Error predicting diseases: {e}")
            return []
    
    def _calculate_disease_symptom_match(self, disease, detected_symptoms):
        """Calculate how well detected symptoms match the disease profile"""
        try:
            # Get all symptoms for this disease from the dataset
            disease_symptoms = set()
            disease_records = 0
            
            for _, row in self.df.iterrows():
                if row['Disease'] == disease:
                    disease_records += 1
                    for j in range(1, 18):
                        symptom_col = f'Symptom_{j}'
                        if symptom_col in self.df.columns:
                            symptom = row[symptom_col]
                            if pd.notna(symptom) and symptom.strip():
                                disease_symptoms.add(symptom.strip())
            
            if not disease_symptoms or disease_records == 0:
                return 0.0
            
            # Calculate comprehensive match score
            matches = len(set(detected_symptoms) & disease_symptoms)
            total_detected = len(detected_symptoms)
            total_disease_symptoms = len(disease_symptoms)
            
            if total_detected == 0:
                return 0.0
            
            # Multiple scoring factors
            precision = matches / total_detected  # How many detected symptoms match
            coverage = matches / min(total_disease_symptoms, 10)  # How well we cover disease symptoms
            frequency_bonus = min(0.2, disease_records / 100)  # Bonus for well-documented diseases
            
            # Combined score with emphasis on precision
            match_score = (precision * 0.6 + coverage * 0.3 + frequency_bonus * 0.1)
            
            return min(0.5, match_score)  # Up to 50% confidence boost
            
        except Exception:
            return 0.0
    
    def save_models(self):
        """Save trained models"""
        try:
            os.makedirs('models', exist_ok=True)
            
            if self.model:
                joblib.dump(self.model, 'models/disease_model.joblib')
            if self.label_encoder:
                joblib.dump(self.label_encoder, 'models/disease_label_encoder.joblib')
            
            # Save metadata
            metadata = {
                'all_symptoms': self.all_symptoms,
                'num_diseases': len(self.label_encoder.classes_) if self.label_encoder else 0,
                'symptom_mappings_count': len(self.symptom_mappings)
            }
            
            with open('models/disease_metadata.json', 'w') as f:
                json.dump(metadata, f, indent=2)
            
            print("✅ Models saved successfully")
            return True
            
        except Exception as e:
            print(f"❌ Error saving models: {e}")
            return False
    
    def load_models(self):
        """Load trained models"""
        try:
            if (os.path.exists('models/disease_model.joblib') and 
                os.path.exists('models/disease_label_encoder.joblib') and
                os.path.exists('models/disease_metadata.json')):
                
                self.model = joblib.load('models/disease_model.joblib')
                self.label_encoder = joblib.load('models/disease_label_encoder.joblib')
                
                with open('models/disease_metadata.json', 'r') as f:
                    metadata = json.load(f)
                    
                print(f"✅ Loaded disease prediction models")
                print(f"   - {metadata.get('num_diseases', 0)} diseases")
                print(f"   - {len(self.all_symptoms)} symptoms")
                print(f"   - {metadata.get('symptom_mappings_count', 0)} symptom mappings")
                
                return True
        except Exception as e:
            print(f"⚠️ Could not load models: {e}")
        
        return False

def main():
    """Test the disease predictor"""
    print("🏥 Enhanced Disease Prediction System")
    print("="*50)
    
    predictor = DiseasePredictor()
    
    # Test cases
    test_cases = [
        "I have been experiencing severe itching and skin rash on my arms",
        "I feel very tired and have high fever with chills",
        "I have constant headache, nausea and feel dizzy",
        "My stomach hurts badly and I have diarrhea and vomiting",
        "I experience frequent urination, excessive thirst and blurred vision"
    ]
    
    for i, symptoms in enumerate(test_cases, 1):
        print(f"\n{i}. Testing: '{symptoms}'")
        print("-" * 60)
        
        predictions = predictor.predict_diseases(symptoms, top_k=2)
        
        if predictions:
            for j, pred in enumerate(predictions, 1):
                confidence_pct = pred['confidence'] * 100
                print(f"   {j}. {pred['disease']} (Confidence: {confidence_pct:.1f}%)")
                print(f"      Detected: {', '.join(pred['detected_symptoms'])}")
        else:
            print("   No diseases predicted")

if __name__ == "__main__":
    main()