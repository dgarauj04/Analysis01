# scripts/train_classifier.py
import os
import argparse
from transformers import AutoTokenizer, AutoModelForSequenceClassification, Trainer, TrainingArguments
import torch
import pandas as pd
from sklearn.model_selection import train_test_split
from torch.utils.data import Dataset

class CsvDataset(Dataset):
    def __init__(self, texts, labels, tokenizer, max_len=256):
        self.texts = texts
        self.labels = labels
        self.tokenizer = tokenizer
        self.max_len = max_len

    def __len__(self):
        return len(self.texts)

    def __getitem__(self, idx):
        enc = self.tokenizer(self.texts[idx], truncation=True, padding='max_length', max_length=self.max_len, return_tensors="pt")
        item = {k: v.squeeze(0) for k,v in enc.items()}
        item["labels"] = torch.tensor(self.labels[idx], dtype=torch.long)
        return item

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", default="data/labels/training_dataset.csv", help="CSV with columns: text,label")
    parser.add_argument("--model_dir", default="models/transformer/bert-base-portuguese-cased")
    parser.add_argument("--out_dir", default="models/classifier")
    parser.add_argument("--epochs", type=int, default=3)
    parser.add_argument("--batch_size", type=int, default=8)
    args = parser.parse_args()

    df = pd.read_csv(args.data)
    df = df.dropna(subset=['text', 'label'])
    labels = sorted(df['label'].unique())
    label2id = {l:i for i,l in enumerate(labels)}
    df['label_id'] = df['label'].map(label2id)

    train_df, val_df = train_test_split(df, test_size=0.15, random_state=42, stratify=df['label_id'])

    tokenizer = AutoTokenizer.from_pretrained(args.model_dir, local_files_only=True)
    model = AutoModelForSequenceClassification.from_pretrained(args.model_dir, num_labels=len(labels), local_files_only=True)

    train_ds = CsvDataset(train_df['text'].tolist(), train_df['label_id'].tolist(), tokenizer)
    val_ds = CsvDataset(val_df['text'].tolist(), val_df['label_id'].tolist(), tokenizer)

    training_args = TrainingArguments(
        output_dir=args.out_dir,
        num_train_epochs=args.epochs,
        per_device_train_batch_size=args.batch_size,
        per_device_eval_batch_size=args.batch_size,
        evaluation_strategy="epoch",
        save_strategy="epoch",
        logging_strategy="steps",
        logging_steps=100,
        fp16=torch.cuda.is_available(),
        push_to_hub=False
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_ds,
        eval_dataset=val_ds,
        tokenizer=tokenizer
    )

    trainer.train()
    trainer.save_model(args.out_dir)
    import json
    with open(os.path.join(args.out_dir, "label2id.json"), "w", encoding="utf-8") as f:
        json.dump(label2id, f, ensure_ascii=False, indent=2)
    print("Modelo treinado e salvo em", args.out_dir)

if __name__ == "__main__":
    main()
