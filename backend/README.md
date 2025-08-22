# ENEM Analyzer - Backend

Arquitetura:
- Flask (MVC)
- SQLAlchemy (SQLite/MySQL)
- pdfplumber + pytesseract for OCR
- spaCy (lemmatization) + NLTK (stemmer fallback)
- Transformers (neuralmind/bert-base-portuguese-cased) for classifier

Quick start:
1. python -m venv .venv && source .venv/bin/activate
2. pip install -r requirements.txt
3. (opcional) make install-spacy
4. make download-model
5. make run
6. Use /api/upload to upload PDFs (optionally send gabarito_file)

Training:
- Generate auto-labeled CSV: scripts/generate_auto_labels.py (or created)
- Preprocess: make preprocess
- Train: make train

Tests:
- pytest -q (ensure fixtures in tests/fixtures)
