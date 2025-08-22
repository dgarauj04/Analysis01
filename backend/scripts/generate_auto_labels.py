# scripts/generate_auto_labels.py
# Gera um CSV auto-rotulado a partir de PDFs em /mnt/data
import os, re, csv, hashlib, json
from collections import Counter

# Tenta usar pdfplumber, senão PyPDF2
PDFLIB = None
try:
    import pdfplumber
    PDFLIB = "pdfplumber"
except Exception:
    try:
        import PyPDF2
        PDFLIB = "pypdf2"
    except Exception:
        PDFLIB = None

# Snowball stemmer (NLTK)
try:
    from nltk.stem.snowball import SnowballStemmer
    stemmer = SnowballStemmer("portuguese")
except Exception:
    stemmer = None

# Stopwords / metadados (amplie conforme precisar)
METADATA_WORDS = {
    "dia", "caderno", "azul", "amarelo", "roxo", "prova", "provas",
    "enunciado", "enunciados", "questão", "questao", "questões", "questoes",
    "inep", "gabarito", "gabaritos", "cartela"
}
STOPWORDS = {
    "o","a","os","as","um","uma","uns","umas","de","do","da","dos","das","em",
    "no","na","nos","nas","e","que","por","para","com","sem","se","como","mais",
    "já","esta","está","foi","ser","são","ao","pelo","pela","poder","entre","sobre",
    "sob","também","ou","mas","quando","onde","qual","quais","quem","há","tem","ter",
    "sua","seu","suas","seus"
}
STOPWORDS = STOPWORDS.union(METADATA_WORDS)

# >>> Cole aqui sua versão ampliada do KEYWORDS (usei a versão que você forneceu) <<<
KEYWORDS = {
    "Matemática": {
        "função":"Funções","funções":"Funções","gráfico":"Gráficos","quadrática":"Funções","polinômio":"Álgebra",
        "polinomial":"Álgebra","matriz":"Algebra Linear","determinante":"Algebra Linear","probabilidade":"Probabilidade",
        "probabilidades":"Probabilidade","combinatória":"Contagem/Combinatória","permuta":"Contagem/Combinatória",
        "combinação":"Contagem/Combinatória","porcentagem":"Porcentagem","porcento":"Porcentagem","percentual":"Porcentagem",
        "equação":"Equações","inequação":"Equações","equações":"Equações","integração":"Cálculo","derivada":"Cálculo",
        "integral":"Cálculo","derivação":"Cálculo","deriv":"Cálculo","vetor":"Geometria Analítica","geometria":"Geometria",
        "triângulo":"Geometria","círculo":"Geometria","quadrado":"Geometria","reta":"Geometria","logaritmo":"Logaritmos",
        "log":"Logaritmos","logarítmico":"Logaritmos","exponencial":"Exponenciais","juros":"Matemática Financeira",
        "taxa":"Matemática Financeira","estatística":"Estatística","média":"Estatística","mediana":"Estatística",
        "moda":"Estatística","desvio":"Estatística","variância":"Estatística","trigonometria":"Trigonometria",
        "seno":"Trigonometria","cosseno":"Trigonometria","tangente":"Trigonometria","progressão":"Progressões",
        "aritmética":"Progressões","geométrica":"Progressões","sequência":"Sequências","razão":"Proporções",
        "escala":"Proporções","plana":"Geometria Plana","espacial":"Geometria Espacial","volume":"Geometria Espacial",
        "área":"Geometria Plana","prisma":"Geometria Espacial","pirâmide":"Geometria Espacial","cilindro":"Geometria Espacial"
    },
    "Ciências": {
        "mitocôndria":"Citologia","membrana":"Citologia","ácido":"Química Inorgânica","base":"Química Inorgânica",
        "reação":"Estequiometria","estequiometria":"Estequiometria","oxid":"Reações de Oxidação/Redução","redução":"Reações de Oxidação/Redução",
        "oxidação":"Reações de Oxidação/Redução","ph":"Química Analítica","equilíbrio":"Química","força":"Mecânica",
        "aceleração":"Mecânica","campo":"Física","DNA":"Genética","velocidade":"Mecânica","energia":"Energia e Trabalho",
        "potência":"Energia e Trabalho","corrente":"Eletromagnetismo","carga":"Eletromagnetismo","resistência":"Eletromagnetismo",
        "capacitância":"Eletromagnetismo","vacina":"Biologia","célula":"Citologia","dna":"Genética","rna":"Genética",
        "ecologia":"Ecologia","átomo":"Estrutura Atômica","molécula":"Ligações Químicas","ligação":"Ligações Químicas",
        "covalente":"Ligações Químicas","iônica":"Ligações Químicas","tabela periódica":"Tabela Periódica","elemento":"Tabela Periódica",
        "orgânica":"Química Orgânica","hidrocarboneto":"Química Orgânica","função orgânica":"Química Orgânica","solução":"Soluções",
        "concentração":"Soluções","movimento":"Cinemática","uniforme":"Cinemática","acelerado":"Cinemática","newton":"Dinâmica",
        "leis de newton":"Dinâmica","óptica":"Óptica","lente":"Óptica","espelho":"Óptica","termodinâmica":"Termodinâmica",
        "calor":"Termodinâmica","temperatura":"Termodinâmica","onda":"Ondulatória","som":"Ondulatória","luz":"Ondulatória",
        "evolução":"Evolução","darwin":"Evolução","ecossistema":"Ecologia","cadeia alimentar":"Ecologia","fotossíntese":"Fisiologia Vegetal",
        "respiração":"Fisiologia","sistema nervoso":"Fisiologia Humana","circulatório":"Fisiologia Humana","vírus":"Virologia","bactéria":"Microbiologia",
        "meio ambiente":"Ecologia","fisiologia":"Fisiologia","mercúrio":"Química Ambiental","alumínio":"Química Inorgânica","latas":"Química Aplicada",
        "câmera":"Instrumentação/Óptica","ton":"Unidades/Medições"
    },
    "Linguagens": {
        "texto":"Interpretação de Texto","interpretação":"Interpretação de Texto","ortografia":"Gramática","gramática":"Gramática",
        "poema":"Poema/Poética","poesia":"Poema/Poética","poeta":"Poema/Poética","poética":"Poema/Poética","narrativa":"Gênero Narrativo",
        "autor":"Literatura","literatura":"Literatura","argumento":"Argumentação","argumentação":"Argumentação","coerência":"Coerência e Coesão",
        "coesão":"Coerência e Coesão","letra":"Interpretação de Texto","redução":"Redação","figura de linguagem":"Figuras de Linguagem",
        "metáfora":"Figuras de Linguagem","metonímia":"Figuras de Linguagem","hipérbole":"Figuras de Linguagem","modernismo":"Movimentos Literários",
        "romantismo":"Movimentos Literários","realismo":"Movimentos Literários","concordância":"Gramática","regência":"Gramática","crase":"Gramática",
        "variação linguística":"Variação Linguística","função da linguagem":"Funções da Linguagem","gênero textual":"Gêneros Textuais",
        "semântica":"Semântica","domínio lexical":"Semântica","argumentativo":"Interpretação/Literatura","figura":"Figuras de Linguagem"
    },
    "Humanas": {
        "sociologia":"Sociologia","sociedade":"Sociologia","história":"História","filosofia":"Filosofia","geografia":"Geografia",
        "território":"Geografia","povo":"Geografia","colonização":"Colonização","cultura":"Cultura","economia":"Economia",
        "constitui":"Direito/Política","constituição":"Direito/Política","legislação":"Direito/Política","legislações":"Direito/Política",
        "direito":"Direito/Política","política":"Direito/Política","colonizador":"Colonização","colonizado":"Colonização","imperial":"História",
        "independência":"História do Brasil","república":"História do Brasil","ditadura":"História do Brasil","segunda guerra":"História Geral",
        "idade média":"História Geral","renascimento":"História Geral","clima":"Climatologia","relevo":"Geomorfologia","hidrografia":"Hidrografia",
        "urbanização":"Geografia Urbana","globalização":"Globalização","agrária":"Geografia Agrária","meio ambiente":"Meio Ambiente",
        "sócrates":"Filosofia Antiga","platão":"Filosofia Antiga","aristóteles":"Filosofia Antiga","ética":"Ética","epistemologia":"Teoria do Conhecimento",
        "marx":"Sociologia","durkheim":"Sociologia","weber":"Sociologia","classe social":"Estrutura Social","mobilidade social":"Estrutura Social",
        "oferta":"Microeconomia","demanda":"Microeconomia","inflação":"Macroeconomia","pib":"Macroeconomia","capitalismo":"Sistemas Econômicos",
        "democracia":"Sistemas Políticos","totalitarismo":"Sistemas Políticos","constituição 1988":"Direito Constitucional","cidadania":"Cidadania",
        "trabalho":"Trabalho e Sociedade","desigualdade":"Desigualdades Sociais"
    }
}

# Build stem map
stem_to_assunto = {}
if stemmer:
    for mat, mapping in KEYWORDS.items():
        for kw, assunto in mapping.items():
            token = re.sub(r"[^0-9A-Za-zÀ-ÿ\s]", " ", kw).strip().lower()
            stem_to_assunto[stemmer.stem(token)] = (assunto, mat)
else:
    for mat, mapping in KEYWORDS.items():
        for kw, assunto in mapping.items():
            token = re.sub(r"[^0-9A-Za-zÀ-ÿ\s]", " ", kw).strip().lower()
            stem_to_assunto[token] = (assunto, mat)

base_dir = "/mnt/data"
candidates = []
if os.path.isdir(base_dir):
    for fn in os.listdir(base_dir):
        if fn.lower().endswith(".pdf") and ("enem" in fn.lower() or "gabarito" in fn.lower()):
            candidates.append(os.path.join(base_dir, fn))

def extract_text_from_pdf(path):
    if PDFLIB == "pdfplumber":
        texts = []
        with pdfplumber.open(path) as pdf:
            for p in pdf.pages:
                texts.append(p.extract_text() or "")
        return "\n".join(texts)
    elif PDFLIB == "pypdf2":
        from PyPDF2 import PdfReader
        reader = PdfReader(path)
        return "\n".join([p.extract_text() or "" for p in reader.pages])
    else:
        return ""

question_pattern = re.compile(r'(^|\n)\s*(?P<num>\d{1,3})[ \.\-]+', re.MULTILINE)

def parse_questions_from_text(text):
    matches = list(question_pattern.finditer(text))
    qs = []
    for i, m in enumerate(matches):
        start = m.end()
        end = matches[i+1].start() if i+1 < len(matches) else len(text)
        block = text[start:end].strip()
        num = int(m.group("num"))
        alts = {}
        for am in re.finditer(r'([A-E])\)\s*(.+?)(?=(?:\n[A-E]\)|\nGabarito|$))', block, re.DOTALL|re.IGNORECASE):
            label = am.group(1).upper()
            val = re.sub(r'\s+', ' ', am.group(2)).strip()
            alts[label] = val
        m_alt_any = re.search(r'\n[A-E]\)', block)
        if m_alt_any:
            enun = block[:m_alt_any.start()].strip()
        else:
            enun = block.strip()[:600]
        qs.append({"numero": num, "enunciado": enun, "alternativas": alts, "raw": block})
    return qs

def tokenize_and_stem(text):
    text = re.sub(r"[^0-9A-Za-zÀ-ÿ\s]", " ", text).lower()
    tokens = [t for t in text.split() if len(t)>2 and t not in STOPWORDS]
    if stemmer:
        return [stemmer.stem(t) for t in tokens]
    else:
        return tokens

rows = []
seen_hashes = set()

for path in candidates:
    text = extract_text_from_pdf(path)
    if "QUEST" in text.upper() or re.search(r'\bQUEST', text.upper()):
        txt_norm = re.sub(r'QUEST(?:ÃO|AO)\.?\s*(\d{1,3})', r'\n\1 ', text, flags=re.IGNORECASE)
    else:
        txt_norm = text
    qlist = parse_questions_from_text(txt_norm)
    for q in qlist:
        combined = (q.get("enunciado") or "") + " " + " ".join(q.get("alternativas", {}).values())
        combined = re.sub(r'\s+', ' ', combined).strip()
        if not combined:
            continue
        h = hashlib.sha256(combined.encode('utf-8')).hexdigest()
        if h in seen_hashes:
            continue
        seen_hashes.add(h)
        stems = tokenize_and_stem(combined)
        counts = Counter()
        for s in stems:
            if s in stem_to_assunto:
                assunto, materia = stem_to_assunto[s]
                counts[(assunto, materia)] += 1
        if counts:
            ((assunto,materia), score) = counts.most_common(1)[0]
            label = assunto
            label_source = materia
        else:
            label = "UNKNOWN"
            label_source = ""
        rows.append({
            "text": combined,
            "label": label,
            "materia_suggested": label_source or "",
            "numero": q.get("numero"),
            "source_file": os.path.basename(path)
        })

# Trim to max 500 (configurável)
max_examples = 500
rows = rows[:max_examples]

out_dir = "/mnt/data/data/labels"
os.makedirs(out_dir, exist_ok=True)
out_csv = os.path.join(out_dir, "auto_training_dataset.csv")
with open(out_csv, "w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["text","label","materia_suggested","numero","source_file"])
    writer.writeheader()
    for r in rows:
        writer.writerow(r)

# .gitignore
gitignore_path = "/mnt/data/.gitignore"
gitignore_content = """
# Python
__pycache__/
*.pyc
.env
.venv/
# Data / models
data/
models/
logs/
"""
with open(gitignore_path, "w", encoding="utf-8") as gf:
    gf.write(gitignore_content.strip() + "\n")

report = {
    "pdf_files_processed": candidates,
    "num_examples": len(rows),
    "output_csv": out_csv,
    "gitignore": gitignore_path,
    "pdf_lib_used": PDFLIB,
    "stemmer_available": stemmer is not None
}
with open(os.path.join(out_dir, "auto_labels_report.json"), "w", encoding="utf-8") as rf:
    json.dump(report, rf, ensure_ascii=False, indent=2)
print("Wrote", len(rows), "examples to", out_csv)
