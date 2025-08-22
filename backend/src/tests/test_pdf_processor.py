import pytest
from src.services.pdf_processor import PDFProcessor

def test_parse_simple_questions():
    text = """
1. Qual é a capital do Brasil?
A) São Paulo
B) Rio de Janeiro
C) Brasília
D) Belo Horizonte
E) Salvador
Gabarito: C

2. (enunciado) Segunda questão
A) Op1
B) Op2
C) Op3
D) Op4
E) Op5
Gabarito: A
"""
    p = PDFProcessor()
    qs = p.parse_questions(text)
    assert len(qs) == 2
    assert qs[0]["numero"] == 1
    assert qs[0]["gabarito"] == "C"
