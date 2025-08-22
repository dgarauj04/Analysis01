# app/utils/text_clean.py
import re

DEFAULT_METADATA_WORDS = {
    "dia", "caderno", "azul", "amarelo", "roxo", "prova", "enunciado",
    "questão", "questao", "questões", "questoes", "provas", "diário", 
    "capítulo", "pagina", "página", "obs", "observação", "caderno", "imprimir",
    "inep", "inep.", "inep", "cartela", "gabarito", "gabaritos"
}

# Lista base de stopwords (amplie conforme necessário). Use NLTK lista se preferir.
DEFAULT_STOPWORDS = {
    "o","a","os","as","um","uma","uns","umas","de","do","da","dos","das","em","no","na","nos","nas",
    "e","que","por","para","com","sem","se","como","mais","já","esta","está","foi","ser","são","ao",
    "os","das","dos","pelo","pela","poder","entre","sobre","sob","também","ou","mas","quando","onde",
    "qual","quais","quem","há","há","tem","temos","ter","sua","seu","suas","seus"
}
# unifica
STOPWORDS = DEFAULT_STOPWORDS.union(DEFAULT_METADATA_WORDS)

def normalize_text(text: str) -> str:
    if not text:
        return ""
    t = text.replace("\r", " ").replace("\n", " ").replace("\t", " ")
    t = re.sub(r"\s+", " ", t)
    t = re.sub(r"http\S+|www\.\S+|\S+@\S+", " ", t)
    t = re.sub(r"[^0-9A-Za-zÀ-ÿ\s]", " ", t)
    return t.strip()

def filter_tokens(tokens):
    # recebe lista de tokens (lowercase) e remove stopwords/metadados e tokens curtos
    cleaned = [t for t in tokens if t not in STOPWORDS and len(t) > 2]
    return cleaned
