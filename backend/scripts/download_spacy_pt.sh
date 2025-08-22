#!/usr/bin/env bash
python -m pip install --upgrade pip
pip install spacy
python -m spacy download pt_core_news_sm
echo "spaCy and pt_core_news_sm installed."
