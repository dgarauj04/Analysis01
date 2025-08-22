# scripts/preprocess_dataset.py
import os
import csv
import json
import argparse
from src.utils.text_clean import normalize_text, filter_tokens
try:
    import spacy
    nlp = spacy.load("pt_core_news_sm")
    USE_SPACY = True
except Exception:
    nlp = None
    USE_SPACY = False
from nltk.stem.snowball import SnowballStemmer
stemmer = SnowballStemmer("portuguese")

def lemmatize_text(text):
    if USE_SPACY and nlp:
        doc = nlp(text)
        lemmas = [t.lemma_.lower() for t in doc if len(t.text) > 1]
        return " ".join(lemmas)
    # fallback: tokenize + stem
    tokens = [t.lower() for t in normalize_text(text).split() if len(t) > 2]
    tokens = filter_tokens(tokens)
    stems = [stemmer.stem(t) for t in tokens]
    return " ".join(stems)

def gather_from_raw(raw_dir):
    rows = []
    for root, dirs, files in os.walk(raw_dir):
        for fn in files:
            if fn.endswith(".json"):
                with open(os.path.join(root, fn), "r", encoding="utf-8") as f:
                    try:
                        data = json.load(f)
                    except Exception:
                        continue
                    for q in data:
                        texto = (q.get("enunciado","") or "") + " " + " ".join((q.get("alternativas") or {}).values())
                        texto = normalize_text(texto)
                        texto = lemmatize_text(texto)
                        label = q.get("assunto") or "UNKNOWN"
                        rows.append({"text": texto, "label": label})
    return rows

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw_dir", default="data/raw", help="diretório com JSONs raw")
    parser.add_argument("--out", default="data/labels/training_dataset_lemmatized.csv")
    args = parser.parse_args()
    rows = gather_from_raw(args.raw_dir)
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "w", encoding="utf-8", newline="") as csvf:
        writer = csv.DictWriter(csvf, fieldnames=["text","label"])
        writer.writeheader()
        for r in rows:
            writer.writerow(r)
    print(f"Wrote {len(rows)} examples to {args.out}")

if __name__ == "__main__":
    main()
