# app/services/classifier.py
import os
import json
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import numpy as np

class ClassifierService:
    def __init__(self, model_dir="models/classifier", base_model_dir="models/transformer/bert-base-portuguese-cased"):
        self.model_dir = model_dir
        self.base_model_dir = base_model_dir
        # load label map
        with open(os.path.join(model_dir, "label2id.json"), "r", encoding="utf-8") as f:
            self.label2id = json.load(f)
        self.id2label = {v:k for k,v in self.label2id.items()}
        # load tokenizer + model (local files only)
        self.tokenizer = AutoTokenizer.from_pretrained(base_model_dir, local_files_only=True)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_dir, local_files_only=True)
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model.to(self.device)
        self.model.eval()

    def predict(self, text, top_k=3):
        enc = self.tokenizer(text, truncation=True, padding=True, return_tensors="pt", max_length=256)
        enc = {k:v.to(self.device) for k,v in enc.items()}
        with torch.no_grad():
            out = self.model(**enc)
            probs = torch.softmax(out.logits, dim=-1).cpu().numpy()[0]
        top_idx = np.argsort(probs)[::-1][:top_k]
        return [{"assunto": self.id2label[int(i)], "score": float(probs[int(i)])} for i in top_idx]
