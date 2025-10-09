"""
CSV Knowledge Base Generator
Converts the 3 CSV files into a comprehensive JSON knowledge base
"""
import pandas as pd
import json
from collections import defaultdict, Counter

class CSVKnowledgeBaseGenerator:
    def __init__(self):
        self.symptoms_data = {}
        self.diseases_data = {}
        self.precautions_data = {}
        self.symptom_to_diseases = defaultdict(list)
        self.disease_to_symptoms = defaultdict(list)
        
    def load_csv_files(self):
        """Load all CSV files and extract knowledge"""
        print("📊 Loading CSV files to create knowledge base...")
        
        # Load main dataset for symptom-disease relationships
        print("Loading dataset.csv...")
        self.df_main = pd.read_csv('dataset.csv')
        print(f"✅ Loaded {len(self.df_main)} medical records")
        
        # Load disease descriptions
        print("Loading symptom_Description.csv...")
        self.df_descriptions = pd.read_csv('symptom_Description.csv')
        self.diseases_data = dict(zip(self.df_descriptions['Disease'], self.df_descriptions['Description']))
        print(f"✅ Loaded {len(self.diseases_data)} disease descriptions")
        
        # Load precautions
        print("Loading symptom_precaution.csv...")
        self.df_precautions = pd.read_csv('symptom_precaution.csv')
        for _, row in self.df_precautions.iterrows():
            disease = row['Disease']
            precautions = [row[f'Precaution_{i}'] for i in range(1, 5) if pd.notna(row[f'Precaution_{i}'])]
            self.precautions_data[disease] = precautions
        print(f"✅ Loaded precautions for {len(self.precautions_data)} diseases")
        
    def extract_symptoms_knowledge(self):
        """Extract comprehensive symptom knowledge from dataset"""
        print("🔍 Extracting symptom knowledge from dataset...")
        
        # Get all unique symptoms
        all_symptoms = set()
        symptom_frequency = Counter()
        
        for index, row in self.df_main.iterrows():
            disease = row['Disease']
            
            # Extract symptoms for this disease
            symptoms_for_disease = []
            for j in range(1, 18):  # Symptom_1 to Symptom_17
                symptom_col = f'Symptom_{j}'
                if symptom_col in self.df_main.columns:
                    symptom = row[symptom_col]
                    if pd.notna(symptom) and symptom.strip():
                        symptom = symptom.strip()
                        all_symptoms.add(symptom)
                        symptom_frequency[symptom] += 1
                        symptoms_for_disease.append(symptom)
                        
                        # Build relationships
                        self.symptom_to_diseases[symptom].append(disease)
            
            # Store disease-symptom relationship
            if symptoms_for_disease:
                self.disease_to_symptoms[disease] = symptoms_for_disease
        
        print(f"✅ Extracted {len(all_symptoms)} unique symptoms")
        
        # Create symptom data with relationships and synonyms
        for symptom in all_symptoms:
            # Create synonyms based on symptom name
            synonyms = self.generate_symptom_synonyms(symptom)
            
            # Get related diseases
            related_diseases = list(set(self.symptom_to_diseases[symptom]))
            
            # Create description based on frequency and diseases
            frequency = symptom_frequency[symptom]
            description = self.generate_symptom_description(symptom, related_diseases, frequency)
            
            # Create advice based on related diseases
            advice = self.generate_symptom_advice(symptom, related_diseases)
            
            self.symptoms_data[symptom] = {
                "name": symptom,
                "synonyms": synonyms,
                "description": description,
                "advice": advice,
                "frequency": frequency,
                "related_diseases": related_diseases[:5]  # Top 5 most common
            }
        
        return all_symptoms
    
    def generate_symptom_synonyms(self, symptom):
        """Generate synonyms for a symptom based on its name"""
        synonyms = [symptom]
        
        # Remove underscores and add space version
        if '_' in symptom:
            space_version = symptom.replace('_', ' ')
            synonyms.append(space_version)
        
        # Add specific synonyms based on symptom patterns
        symptom_lower = symptom.lower()
        
        # Pain symptoms
        if 'pain' in symptom_lower:
            synonyms.extend(['ache', 'hurt', 'soreness'])
            if 'joint' in symptom_lower:
                synonyms.extend(['joint ache', 'arthritis', 'stiff joints'])
            elif 'muscle' in symptom_lower:
                synonyms.extend(['muscle ache', 'muscle soreness', 'myalgia'])
            elif 'chest' in symptom_lower:
                synonyms.extend(['chest ache', 'chest discomfort'])
            elif 'stomach' in symptom_lower or 'abdominal' in symptom_lower:
                synonyms.extend(['belly pain', 'tummy ache', 'stomach ache'])
        
        # Fever symptoms
        elif 'fever' in symptom_lower:
            synonyms.extend(['fever', 'temperature', 'hot', 'feverish'])  # Add 'fever' explicitly
            if 'high' in symptom_lower:
                synonyms.extend(['high temperature', 'burning fever'])
            elif 'mild' in symptom_lower:
                synonyms.extend(['low fever', 'slight fever'])
        
        # Digestive symptoms
        elif 'nausea' in symptom_lower:
            synonyms.extend(['sick feeling', 'queasy', 'feeling sick'])
        elif 'vomiting' in symptom_lower:
            synonyms.extend(['throwing up', 'being sick', 'puking'])
        elif 'diarrhoea' in symptom_lower:
            synonyms.extend(['diarrhea', 'loose stools', 'watery stools'])
        
        # Respiratory symptoms
        elif 'cough' in symptom_lower:
            synonyms.extend(['coughing', 'throat clearing'])
        elif 'breathlessness' in symptom_lower:
            synonyms.extend(['shortness of breath', 'difficulty breathing', 'hard to breathe'])
        
        # Skin symptoms
        elif 'itching' in symptom_lower:
            synonyms.extend(['itch', 'scratching', 'irritation'])
        elif 'rash' in symptom_lower:
            synonyms.extend(['skin rash', 'skin irritation', 'red spots'])
        
        # Vision symptoms
        elif 'vision' in symptom_lower:
            synonyms.extend(['eyesight', 'sight problems', 'eye problems'])
            if 'blurred' in symptom_lower:
                synonyms.extend(['blurry vision', 'unclear vision'])
        
        # Fatigue symptoms
        elif 'fatigue' in symptom_lower:
            synonyms.extend(['tiredness', 'exhaustion', 'weakness'])
        
        # Urinary symptoms
        elif 'polyuria' in symptom_lower:
            synonyms.extend(['frequent urination', 'urinating often', 'peeing frequently'])
        
        return list(set(synonyms))  # Remove duplicates
    
    def generate_symptom_description(self, symptom, related_diseases, frequency):
        """Generate a description for a symptom"""
        symptom_clean = symptom.replace('_', ' ').title()
        
        if frequency > 100:
            freq_desc = "This is a very common symptom"
        elif frequency > 50:
            freq_desc = "This is a moderately common symptom"
        else:
            freq_desc = "This symptom"
        
        # Get top disease categories
        disease_categories = []
        if related_diseases:
            for disease in related_diseases[:3]:
                disease_categories.append(disease)
        
        if disease_categories:
            diseases_text = ", ".join(disease_categories[:2])
            if len(disease_categories) > 2:
                diseases_text += f" and {len(related_diseases)-2} other conditions"
            
            description = f"{freq_desc} that can be associated with {diseases_text}. {symptom_clean} may indicate various underlying health conditions and should be evaluated properly."
        else:
            description = f"{freq_desc} that may indicate various underlying health conditions and should be evaluated by a healthcare professional."
        
        return description
    
    def generate_symptom_advice(self, symptom, related_diseases):
        """Generate advice for a symptom"""
        symptom_lower = symptom.lower()
        
        # General advice based on symptom type
        if 'pain' in symptom_lower:
            advice = "Rest the affected area and avoid strenuous activities. Apply ice or heat as appropriate. "
        elif 'fever' in symptom_lower:
            advice = "Stay hydrated, rest, and monitor your temperature. "
        elif 'nausea' in symptom_lower:
            advice = "Eat light, bland foods and stay hydrated with small sips of water. "
        elif 'cough' in symptom_lower:
            advice = "Stay hydrated and avoid irritants. Consider warm liquids with honey. "
        elif 'itching' in symptom_lower:
            advice = "Avoid scratching and keep the area clean and dry. "
        elif 'fatigue' in symptom_lower:
            advice = "Ensure adequate rest and maintain a balanced diet. "
        else:
            advice = "Monitor the symptom and note any changes or worsening. "
        
        # Add severity warning
        advice += "If symptoms persist, worsen, or you experience severe discomfort, consult a healthcare professional promptly."
        
        return advice
    
    def create_knowledge_base(self):
        """Create the complete knowledge base JSON"""
        print("🏗️ Creating comprehensive knowledge base...")
        
        # Load and process CSV files
        self.load_csv_files()
        symptoms = self.extract_symptoms_knowledge()
        
        # Create the knowledge base structure
        knowledge_base = {
            "version": "2.0",
            "source": "CSV Medical Database",
            "total_symptoms": len(symptoms),
            "total_diseases": len(self.diseases_data),
            "symptoms": list(self.symptoms_data.values()),
            "diseases": [
                {
                    "name": disease,
                    "description": description,
                    "symptoms": self.disease_to_symptoms.get(disease, []),
                    "precautions": self.precautions_data.get(disease, [])
                }
                for disease, description in self.diseases_data.items()
            ]
        }
        
        return knowledge_base
    
    def save_knowledge_base(self, filename='kb_csv.json'):
        """Save the knowledge base to JSON file"""
        kb = self.create_knowledge_base()
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(kb, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Knowledge base saved to {filename}")
        print(f"   📊 {kb['total_symptoms']} symptoms")
        print(f"   🏥 {kb['total_diseases']} diseases")
        print(f"   💊 {len([d for d in kb['diseases'] if d['precautions']])} diseases with precautions")
        
        return kb

def main():
    """Generate CSV-based knowledge base"""
    print("🔬 CSV Knowledge Base Generator")
    print("="*50)
    
    generator = CSVKnowledgeBaseGenerator()
    kb = generator.save_knowledge_base()
    
    # Show sample data
    print(f"\n📋 Sample Symptoms:")
    for i, symptom in enumerate(kb['symptoms'][:5], 1):
        print(f"   {i}. {symptom['name']} (frequency: {symptom['frequency']})")
        print(f"      Synonyms: {', '.join(symptom['synonyms'][:3])}...")
    
    print(f"\n🏥 Sample Diseases:")
    for i, disease in enumerate(kb['diseases'][:5], 1):
        print(f"   {i}. {disease['name']}")
        print(f"      Symptoms: {len(disease['symptoms'])} | Precautions: {len(disease['precautions'])}")

if __name__ == "__main__":
    main()