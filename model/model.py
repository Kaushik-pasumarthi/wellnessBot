import json
import torch
from torch.utils.data import Dataset
from transformers import BertTokenizer, BertForSequenceClassification, Trainer, TrainingArguments, logging
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
import numpy as np


logging.set_verbosity_error()

with open("dataset.json", "r", encoding="utf-8") as f:
    data = json.load(f)

texts, labels = [], []
tag_to_id = {intent["intent"]: idx for idx, intent in enumerate(data["intents"])}
id_to_tag = {idx: tag for tag, idx in tag_to_id.items()}

for intent in data["intents"]:
    for pattern in intent["patterns"]:
        texts.append(pattern)
        labels.append(tag_to_id[intent["intent"]])

labels = LabelEncoder().fit_transform(labels)
num_labels = len(np.unique(labels))

train_texts, val_texts, train_labels, val_labels = train_test_split(
    texts, labels, test_size=0.1, random_state=42
)

tokenizer = BertTokenizer.from_pretrained("bert-base-multilingual-cased")


class IntentDataset(Dataset):
    def __init__(self, texts, labels):
        self.encodings = tokenizer(texts, padding=True, truncation=True, max_length=64, return_tensors="pt")
        self.labels = torch.tensor(labels, dtype=torch.long)

    def __len__(self):
        return len(self.labels)

    def __getitem__(self, idx):
        item = {k: v[idx] for k, v in self.encodings.items()}
        item["labels"] = self.labels[idx]
        return item

train_dataset = IntentDataset(train_texts, train_labels)
val_dataset = IntentDataset(val_texts, val_labels)

model = BertForSequenceClassification.from_pretrained(
    "bert-base-multilingual-cased",
    num_labels=num_labels
)

from sklearn.metrics import precision_recall_fscore_support, accuracy_score

def compute_metrics(eval_pred):
    logits, labels = eval_pred
    preds = np.argmax(logits, axis=-1)
    acc = accuracy_score(labels, preds)
    p, r, f, _ = precision_recall_fscore_support(labels, preds, average='weighted', zero_division=0)
    return {"accuracy": acc, "precision": p, "recall": r, "f1": f}


train_args = TrainingArguments(
    output_dir="checkpoints/",
    num_train_epochs=12,
    per_device_train_batch_size=16,
    per_device_eval_batch_size=16,
    learning_rate=5e-5,
    save_total_limit=5,
    report_to=[],
    dataloader_pin_memory=False
)

trainer = Trainer(
    model=model,
    args=train_args,
    train_dataset=train_dataset,
    eval_dataset=val_dataset,
    compute_metrics=compute_metrics,
)

trainer.train()

metrics = trainer.evaluate()
print(f"Final Accuracy: {metrics['eval_accuracy']:.4f}")

model.save_pretrained("intent_model/")
tokenizer.save_pretrained("intent_model/")
print("✅ Model saved'")
model.save_pretrained("checkpoints/intent_model")
tokenizer.save_pretrained("checkpoints/intent_model")
print("✅ Model and tokenizer saved to checkpoints/intent_model")
