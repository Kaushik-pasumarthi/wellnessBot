import torch
from transformers import BertTokenizer, BertForSequenceClassification
import torch.nn.functional as F
import json
import os

model_dir = "checkpoints/intent_model"

# load tokenizer + model
tokenizer = BertTokenizer.from_pretrained(model_dir, local_files_only=True)
model = BertForSequenceClassification.from_pretrained(model_dir, local_files_only=True)
model.eval()

# Load label map if available, otherwise build from dataset.json
if os.path.exists("label_map.json"):
    with open("label_map.json","r",encoding="utf-8") as f:
        tag_to_id = json.load(f)
    id_to_tag = {int(v): k for k, v in tag_to_id.items()}
else:
    with open("dataset.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    tag_to_id = {intent["intent"]: idx for idx, intent in enumerate(data["intents"])}
    id_to_tag = {idx: tag for tag, idx in tag_to_id.items()}

def predict_intent(text):
    inputs = tokenizer(text, padding=True, truncation=True, max_length=64, return_tensors="pt")
    with torch.no_grad():
        outputs = model(**inputs)
        logits = outputs.logits
        probs = F.softmax(logits, dim=-1)
        pred_id = int(torch.argmax(probs, dim=-1))
        confidence = float(probs[0][pred_id])
    intent = id_to_tag.get(pred_id, "unknown")
    return intent, confidence

def predict_topk(text, k=3):
    inputs = tokenizer(text, padding=True, truncation=True, max_length=64, return_tensors="pt")
    with torch.no_grad():
        outputs = model(**inputs)
        probs = F.softmax(outputs.logits, dim=-1)[0].cpu().numpy()
    topk_idx = probs.argsort()[-k:][::-1]
    return [(id_to_tag[int(i)], float(probs[int(i)])) for i in topk_idx]

if __name__ == "__main__":
    while True:
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit"]:
            print("Exiting...")
            break
        intent_pred, confidence_score = predict_intent(user_input)
        print(f"Predicted Intent: {intent_pred}")
        print(f"Confidence score: {confidence_score:.2f}")
        print("Top 3 predictions:", predict_topk(user_input, k=3))
