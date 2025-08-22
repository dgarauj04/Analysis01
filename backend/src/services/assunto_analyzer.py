from collections import Counter, defaultdict
import re
from nltk.stem.snowball import SnowballStemmer
from src.utils.text_clean import normalize_text, filter_tokens

KEYWORDS = {
    "Matemática": {
        "função": "Funções",
        "funções": "Funções",
        "gráfico": "Gráficos",
        "quadrática": "Funções",
        "polinômio": "Álgebra",
        "polinomial": "Álgebra",
        "matriz": "Álgebra Linear",
        "determinante": "Álgebra Linear",
        "probabilidade": "Probabilidade",
        "probabilidades": "Probabilidade",
        "combinatória": "Contagem/Combinatória",
        "permuta": "Contagem/Combinatória",
        "combinação": "Contagem/Combinatória",
        "porcentagem": "Porcentagem",
        "porcento": "Porcentagem",
        "percentual": "Porcentagem",
        "equação": "Equações",
        "inequação": "Equações",
        "equações": "Equações",
        "integração": "Cálculo",
        "derivada": "Cálculo",
        "integral": "Cálculo",
        "derivação": "Cálculo",
        "deriv": "Cálculo",
        "vetor": "Geometria Analítica",
        "geometria": "Geometria",
        "triângulo": "Geometria",
        "círculo": "Geometria",
        "quadrado": "Geometria",
        "reta": "Geometria",
        "logaritmo": "Logaritmos",
        "log": "Logaritmos",
        "logarítmico": "Logaritmos",
        "exponencial": "Exponenciais",
        "juros": "Matemática Financeira",
        "taxa": "Matemática Financeira",
        "percentual": "Porcentagem",
        "estatística": "Estatística",
        "média": "Estatística",
        "mediana": "Estatística",
        "moda": "Estatística",
        "desvio": "Estatística",
        "variância": "Estatística",
        "trigonometria": "Trigonometria",
        "seno": "Trigonometria",
        "cosseno": "Trigonometria",
        "tangente": "Trigonometria",
        "progressão": "Progressões",
        "aritmética": "Progressões",
        "geométrica": "Progressões",
        "sequência": "Sequências",
        "razão": "Proporções",
        "escala": "Proporções",
        "plana": "Geometria Plana",
        "espacial": "Geometria Espacial",
        "volume": "Geometria Espacial",
        "área": "Geometria Plana",
        "prisma": "Geometria Espacial",
        "pirâmide": "Geometria Espacial",
        "cilindro": "Geometria Espacial"
        },
    "Ciências": {
        "mitocôndria": "Citologia",
        "membrana": "Citologia",
        "ácido": "Química Inorgânica",
        "base": "Química Inorgânica",
        "reação": "Estequiometria",
        "estequiometria": "Estequiometria",
        "oxid": "Reações de Oxidação/Redução",
        "redução": "Reações de Oxidação/Redução",
        "oxidação": "Reações de Oxidação/Redução",
        "ph": "Química Analítica",
        "equilíbrio": "Química",
        "força": "Mecânica",
        "aceleração": "Mecânica",
        "campo": "Física",
        "DNA": "Genética",
        "velocidade": "Mecânica",
        "energia": "Energia e Trabalho",
        "potência": "Energia e Trabalho",
        "campo": "Eletromagnetismo",
        "corrente": "Eletromagnetismo",
        "carga": "Eletromagnetismo",
        "resistência": "Eletromagnetismo",
        "capacitância": "Eletromagnetismo",
        "vacina": "Biologia",
        "célula": "Citologia",
        "mitocôndria": "Citologia",
        "dna": "Genética",
        "rna": "Genética",
        "vacina": "Imunologia",
        "ecologia": "Ecologia",
        "átomo": "Estrutura Atômica",
        "molécula": "Ligações Químicas",
        "ligação": "Ligações Químicas",
        "covalente": "Ligações Químicas",
        "iônica": "Ligações Químicas",
        "tabela periódica": "Tabela Periódica",
        "elemento": "Tabela Periódica",
        "orgânica": "Química Orgânica",
        "hidrocarboneto": "Química Orgânica",
        "função orgânica": "Química Orgânica",
        "solução": "Soluções",
        "concentração": "Soluções",
        "movimento": "Cinemática",
        "uniforme": "Cinemática",
        "acelerado": "Cinemática",
        "newton": "Dinâmica",
        "leis de newton": "Dinâmica",
        "óptica": "Óptica",
        "lente": "Óptica",
        "espelho": "Óptica",
        "termodinâmica": "Termodinâmica",
        "calor": "Termodinâmica",
        "temperatura": "Termodinâmica",
        "onda": "Ondulatória",
        "som": "Ondulatória",
        "luz": "Ondulatória",
        "evolução": "Evolução",
        "darwin": "Evolução",
        "ecossistema": "Ecologia",
        "cadeia alimentar": "Ecologia",
        "fotossíntese": "Fisiologia Vegetal",
        "respiração": "Fisiologia",
        "sistema nervoso": "Fisiologia Humana",
        "circulatório": "Fisiologia Humana",
        "vírus": "Virologia",
        "bactéria": "Microbiologia",
        "meio ambiente": "Ecologia",
        "fisiologia": "Fisiologia"
        },
    "Linguagens": {
        "texto": "Interpretação de Texto",
        "interpretação": "Interpretação de Texto",
        "ortografia": "Gramática",
        "gramática": "Gramática",
        "poema": "Poema/Poética",
        "poesia": "Poema/Poética",
        "poeta": "Poema/Poética",
        "poética": "Poema/Poética",
        "narrativa": "Gênero Narrativo",
        "autor": "Literatura",
        "literatura": "Literatura",
        "argumento": "Argumentação",
        "argumentação": "Argumentação",
        "coerência": "Coerência e Coesão",
        "coesão": "Coerência e Coesão",
        "letra": "Interpretação de Texto",
        "redução": "Redação",
        "figura de linguagem": "Figuras de Linguagem",
        "metáfora": "Figuras de Linguagem",
        "metonímia": "Figuras de Linguagem",
        "hipérbole": "Figuras de Linguagem",
        "modernismo": "Movimentos Literários",
        "romantismo": "Movimentos Literários",
        "realismo": "Movimentos Literários",
        "concordância": "Gramática",
        "regência": "Gramática",
        "crase": "Gramática",
        "variação linguística": "Variação Linguística",
        "função da linguagem": "Funções da Linguagem",
        "gênero textual": "Gêneros Textuais",
        "semântica": "Semântica",
        "domínio lexical": "Semântica"
        },
    "Humanas": {
        "sociologia": "Sociologia",
        "sociedade": "Sociologia",
        "história": "História",
        "filosofia": "Filosofia",
        "geografia": "Geografia",
        "território": "Geografia",
        "povo": "Geografia",
        "colonização": "História",
        "cultura": "Cultura",
        "economia": "Economia",
        "constitui": "Direito/Política",
        "constituição": "Direito/Política",
        "legislação": "Direito/Política",
        "legislações": "Direito/Política",
        "direito": "Direito/Política",
        "política": "Direito/Política",
        "colonização": "Colonização",
        "colonizador": "Colonização",
        "colonizado": "Colonização",
        "imperial": "História",
        "independência": "História do Brasil",
        "república": "História do Brasil",
        "ditadura": "História do Brasil",
        "segunda guerra": "História Geral",
        "idade média": "História Geral",
        "renascimento": "História Geral",
        "clima": "Climatologia",
        "relevo": "Geomorfologia",
        "hidrografia": "Hidrografia",
        "urbanização": "Geografia Urbana",
        "globalização": "Globalização",
        "agrária": "Geografia Agrária",
        "meio ambiente": "Meio Ambiente",
        "sócrates": "Filosofia Antiga",
        "platão": "Filosofia Antiga",
        "aristóteles": "Filosofia Antiga",
        "ética": "Ética",
        "epistemologia": "Teoria do Conhecimento",
        "marx": "Sociologia",
        "durkheim": "Sociologia",
        "weber": "Sociologia",
        "classe social": "Estrutura Social",
        "mobilidade social": "Estrutura Social",
        "oferta": "Microeconomia",
        "demanda": "Microeconomia",
        "inflação": "Macroeconomia",
        "pib": "Macroeconomia",
        "capitalismo": "Sistemas Econômicos",
        "democracia": "Sistemas Políticos",
        "totalitarismo": "Sistemas Políticos",
        "constituição 1988": "Direito Constitucional",
        "cidadania": "Cidadania",
        "trabalho": "Trabalho e Sociedade",
        "desigualdade": "Desigualdades Sociais"
        }
}

try:
    import spacy
    NLP = spacy.load("pt_core_news_sm")
    USE_SPACY = True
except Exception:
    NLP = None
    USE_SPACY = False    

class AssuntoAnalyzer:
    def __init__(self, keywords=KEYWORDS):
        self.stemmer = SnowballStemmer("portuguese")
        # pre-process keyword map: for each materia, map stem(keyword) -> assunto
        self.keywords = {}
        for mat, mapping in keywords.items():
            d = {}
            for k, assunto in mapping.items():
                stem = self._stem_token(self._normalize_token(k))
                d[stem] = assunto
            self.keywords[mat] = d
            
    def _normalize_token(self, token):
        return re.sub(r"[^0-9A-Za-zÀ-ÿ\s]", " ", token).strip().lower()
        
    def _tokenize(self, text):
        text = normalize_text(text)
        tokens = [t.lower() for t in text.split() if len(t) > 1]
        tokens = filter_tokens(tokens)
        return tokens
    
    def _lemmatize_tokens(self, tokens):
        if USE_SPACY and NLP:
            doc = NLP(" ".join(tokens))
            return [tok.lemma_.lower() for tok in doc if tok.lemma_]
        return [self.stemmer.stem(t) for t in tokens]
    
    def _stem_token(self, token):
       return self.stemmer.stem(token.lower())

    def analyze_questions(self, questions):
        by_materia = defaultdict(list)
        for q in questions:
            mat = q.get("materia") or "Geral"
            by_materia[mat].append(q)

        result = {}
        for mat, qs in by_materia.items():
            counter = Counter()
            examples = defaultdict(list)
            kw_map = self.keywords.get(mat, {})
            if not kw_map:
                kw_map = {}
                for sub in self.keywords.values():
                    kw_map.update(sub)
            for q in qs:
                text = (q.get("enunciado") or "") + " " + " ".join(v for v in (q.get("alternativas") or {}).values())
                tokens = self._tokenize(text)
                lemmas = self._lemmatize_tokens(tokens)
                for s, token in zip(lemmas, tokens):
                        if s in kw_map:
                            assunto = kw_map[s]
                            counter[assunto] += 1
                            if len(examples[assunto]) < 3:
                                examples[assunto].append({"numero": q["numero"], "excerpt": (q["enunciado"] or "")[:300]})
            top = []
            for assunto, sc in counter.most_common(20):
                top.append({"assunto": assunto, "score": sc, "exemplos": examples.get(assunto, [])})
            result[mat] = {"top_assuntos": top, "total_questoes": len(qs)}
        return result
