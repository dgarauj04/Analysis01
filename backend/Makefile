.PHONY: init db migrate run test docker-build download-model install-spacy preprocess train

init:
	python -m venv .venv
	. .venv/bin/activate && pip install -r requirements.txt

run:
	python run.py

test:
	pytest -q

docker-build:
	docker build -t enem-analyzer .

download-model:
	python scripts/download_model.py --repo neuralmind/bert-base-portuguese-cased --out models/transformer/bert-base-portuguese-cased

install-spacy:
	bash scripts/download_spacy_pt.sh

preprocess:
	python scripts/preprocess_dataset.py --raw_dir data/raw --out data/labels/training_dataset_lemmatized.csv

train:
	python scripts/train_classifier.py --data data/labels/training_dataset_lemmatized.csv --model_dir models/transformer/bert-base-portuguese-cased --out_dir models/classifier --epochs 3 --batch_size 8
