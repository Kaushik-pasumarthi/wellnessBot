import json
import os
import numpy as np
import logging
from datetime import datetime
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix
from sklearn.model_selection import train_test_split, cross_val_score
import joblib
import pandas as pd

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('training.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def load_intents(file_path='bot_intents.json'):
    """Load and validate intents from JSON file."""
    try:
        # Try with utf-8-sig first to handle BOM, then fallback to utf-8
        try:
            with open(file_path, 'r', encoding='utf-8-sig') as f:
                data = json.load(f)
        except UnicodeDecodeError:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        
        if 'intents' not in data:
            raise ValueError("JSON file must contain 'intents' key")
        
        logger.info(f"Successfully loaded {len(data['intents'])} intents from {file_path}")
        return data
    except FileNotFoundError:
        logger.error(f"File {file_path} not found")
        raise
    except json.JSONDecodeError:
        logger.error(f"Invalid JSON format in {file_path}")
        raise

def prepare_data(data):
    """Extract texts and labels from intents data."""
    texts = []
    labels = []
    
    for intent in data['intents']:
        tag = intent.get('tag')
        patterns = intent.get('patterns', [])
        
        if not tag:
            logger.warning(f"Intent missing 'tag' field: {intent}")
            continue
            
        if not patterns:
            logger.warning(f"Intent '{tag}' has no patterns")
            continue
            
        for pattern in patterns:
            if pattern.strip():  # Only add non-empty patterns
                texts.append(pattern.strip())
                labels.append(tag)
    
    logger.info(f"Prepared {len(texts)} training samples across {len(set(labels))} classes")
    
    # Display class distribution
    label_counts = pd.Series(labels).value_counts()
    logger.info("Class distribution:")
    for label, count in label_counts.items():
        logger.info(f"  {label}: {count} samples")
    
    return texts, labels

def create_models():
    """Create and configure ML models."""
    vectorizer = TfidfVectorizer(
        max_features=5000,
        ngram_range=(1, 2),
        stop_words='english',
        lowercase=True,
        strip_accents='ascii'
    )
    
    classifier = LogisticRegression(
        max_iter=2000,
        random_state=42,
        C=1.0,
        class_weight='balanced'  # Handle class imbalance
    )
    
    label_encoder = LabelEncoder()
    
    return vectorizer, classifier, label_encoder

def train_and_evaluate(texts, labels):
    """Train models and perform comprehensive evaluation."""
    logger.info("Starting model training and evaluation...")
    
    # Create models
    vectorizer, classifier, label_encoder = create_models()
    
    # Encode labels
    y = label_encoder.fit_transform(labels)
    
    # Vectorize texts
    X = vectorizer.fit_transform(texts)
    
    # Split data for proper evaluation
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    # Train classifier
    logger.info("Training classifier...")
    classifier.fit(X_train, y_train)
    
    # Cross-validation on training data
    cv_scores = cross_val_score(classifier, X_train, y_train, cv=5)
    logger.info(f"Cross-validation scores: {cv_scores}")
    logger.info(f"Average CV score: {cv_scores.mean():.4f} (+/- {cv_scores.std() * 2:.4f})")
    
    # Evaluate on test set
    y_pred = classifier.predict(X_test)
    test_accuracy = accuracy_score(y_test, y_pred)
    
    logger.info(f"Test set accuracy: {test_accuracy:.4f}")
    
    # Detailed classification report
    print("\n" + "="*50)
    print("CLASSIFICATION REPORT (Test Set)")
    print("="*50)
    print(classification_report(y_test, y_pred, target_names=label_encoder.classes_))
    
    # Confusion matrix
    cm = confusion_matrix(y_test, y_pred)
    logger.info("Confusion Matrix:")
    logger.info(f"\n{cm}")
    
    # Feature importance (top TF-IDF features for each class)
    feature_names = vectorizer.get_feature_names_out()
    for i, class_name in enumerate(label_encoder.classes_):
        top_features_idx = classifier.coef_[i].argsort()[-10:][::-1]
        top_features = [feature_names[idx] for idx in top_features_idx]
        logger.info(f"Top features for '{class_name}': {top_features}")
    
    return vectorizer, classifier, label_encoder, test_accuracy

def save_models(vectorizer, classifier, label_encoder, accuracy, models_dir='models'):
    """Save trained models and metadata."""
    os.makedirs(models_dir, exist_ok=True)
    
    # Save models
    model_files = {
        'vectorizer': f'{models_dir}/vectorizer.joblib',
        'classifier': f'{models_dir}/classifier.joblib',
        'label_encoder': f'{models_dir}/label_encoder.joblib'
    }
    
    joblib.dump(vectorizer, model_files['vectorizer'])
    joblib.dump(classifier, model_files['classifier'])
    joblib.dump(label_encoder, model_files['label_encoder'])
    
    # Save metadata
    metadata = {
        'training_date': datetime.now().isoformat(),
        'test_accuracy': float(accuracy),
        'n_classes': len(label_encoder.classes_),
        'classes': label_encoder.classes_.tolist(),
        'vectorizer_features': vectorizer.max_features,
        'model_files': model_files
    }
    
    with open(f'{models_dir}/metadata.json', 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
    
    logger.info(f"Models and metadata saved to '{models_dir}/' folder")
    logger.info(f"Model files: {list(model_files.values())}")

def main():
    """Main training pipeline."""
    try:
        logger.info("Starting bot training pipeline...")
        
        # Load data
        data = load_intents()
        texts, labels = prepare_data(data)
        
        if len(texts) == 0:
            raise ValueError("No valid training data found")
        
        if len(set(labels)) < 2:
            raise ValueError("Need at least 2 different intent classes for training")
        
        # Train and evaluate
        vectorizer, classifier, label_encoder, accuracy = train_and_evaluate(texts, labels)
        
        # Save models
        save_models(vectorizer, classifier, label_encoder, accuracy)
        
        logger.info(f"Training completed successfully! Final test accuracy: {accuracy:.4f}")
        
    except Exception as e:
        logger.error(f"Training failed: {str(e)}")
        raise

if __name__ == "__main__":
    main()
