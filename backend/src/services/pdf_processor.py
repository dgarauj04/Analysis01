import os
import json
import re
import logging
import pdfplumber
from .ocr import ocr_pdf_images
from typing import List, Dict

logger = logging.getLogger(__name__)

QUESTAO_HEADER_RE = re.compile(r"QUEST[ÕO]A?\s*\.?\s*(?P<num>\d{1,3})", re.IGNORECASE)
ALTERNATIVA_RE = re.compile(r"(?P<label>[A-E])\)\s*(?P<text>.+?)(?=(?:\n[A-E]\)|\nGabarito|$))", re.DOTALL|re.IGNORECASE)
GABARITO_TABLE_RE = re.compile(r"(\d{1,3}\s+[A-EX])", re.IGNORECASE)

class PDFProcessor:
    def __init__(self, ocr_lang="por"):
        self.ocr_lang = ocr_lang

    def extract_text(self, pdf_path: str, use_ocr: bool = False) -> str:
        
        logger.info("Extracting text from %s", pdf_path)
        text_parts = []
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for p in pdf.pages:
                    t = p.extract_text() or ""
                    text_parts.append(t)
        except Exception as e:
            logger.exception("pdfplumber error: %s", e)

        text = "\n".join(text_parts).strip()
        if len(text) < 200 or use_ocr:
            logger.info("Falling back to OCR for %s", pdf_path)
            ocr_text = ocr_pdf_images(pdf_path, lang=self.ocr_lang)
            text = (text + "\n" + ocr_text).strip()
        return text

    def split_by_questoes_enem(self, text: str) -> List[Dict]:
       
        lines = text.splitlines()
        blocks = []
        current = None
        for i, line in enumerate(lines):
            m = QUESTAO_HEADER_RE.search(line)
            if m:
                if current:
                    blocks.append(current)
                current = {"numero": int(m.group("num")), "lines": [line]}
            else:
                if current:
                    current["lines"].append(line)
        if current:
            blocks.append(current)
        # join lines
        for b in blocks:
            b["text"] = "\n".join(b["lines"]).strip()
            b.pop("lines", None)
        return blocks

    def _parse_gabarito_table(self, text: str) -> Dict[int,str]:
        
        gmap = {}
        tail = text[-12000:]
        tail = tail.replace("\t", " ").replace("\r", "\n")
        seq_matches = re.findall(r"(\d{1,3})\s+([A-EX])", tail, re.IGNORECASE)
        for num, let in seq_matches:
            try:
                gmap[int(num)] = let.upper()
            except:
                pass
            v_matches = re.findall(r"(\d{1,3})\s*\n\s*([A-EX])", tail, re.IGNORECASE)
        for num, let in v_matches:
            gmap[int(num)] = let.upper()
        return gmap

    def parse_gabarito_pdf(self, pdf_path: str) -> dict:   
        try:
            text = ""
            with pdfplumber.open(pdf_path) as pdf:
                for p in pdf.pages:
                    text += "\n" + (p.extract_text() or "")
        except Exception:
            text = self.extract_text(pdf_path, use_ocr=True)
        text = text.replace('\r','\n')
        gmap = {}
        for m in re.finditer(r"(\b\d{1,3}\b)\s+([A-EX])\b", text, re.IGNORECASE):
            num = int(m.group(1))
            let = m.group(2).upper()
            gmap[num] = let
        for m in re.finditer(r"(\b\d{1,3}\b)\s*\n\s*([A-EX])\b", text, re.IGNORECASE):
            num = int(m.group(1))
            let = m.group(2).upper()
            gmap[num] = let

        return gmap


    def parse_questions(self, text: str) -> List[Dict]:
        text = text.replace("\r\n", "\n")
        blocks = []
        gmap = self._parse_gabarito_table(text)
        if re.search(r'\bQUEST(?:ÃO|AO)\b', text, re.IGNORECASE):
            blocks = self.split_by_questoes_enem(text)
        else:
            # numeric splitter
            parts = re.split(r"\n(?=\d{1,3}[ \.\-])", text)
            for part in parts:
                m = re.match(r"^\s*(?P<numero>\d{1,3})[ \.\-]+(?P<body>.+)$", part, re.DOTALL)
                if not m: continue
                numero = int(m.group("numero"))
                body = m.group("body").strip()
                blocks.append({"numero": numero, "text": body})
        questions = []
        for b in blocks:
            num = b["numero"]
            block_text = b["text"]
            # find alternatives
            alts = {}
            for m in ALTERNATIVA_RE.finditer(block_text):
                label = m.group("label").upper()
                val = m.group("text").strip()
                val = re.sub(r"\s+", " ", val)
                alts[label] = val

            first_alt = re.search(r"\n[A-E]\)", block_text)
            if first_alt:
                enunciado = block_text[:first_alt.start()].strip()
            else:
                enunciado = block_text.strip()[:1200]
            g = None
            gm = re.search(r"Gabarito\W*[:\-]?\s*([A-EX])", block_text, re.IGNORECASE)
            if gm:
                g = gm.group(1).upper()
            elif num in gmap:
                g = gmap[num]

            questions.append({
                "numero": num, "enunciado": enunciado, "alternativas": alts, "gabarito": g})
        try:
            self.validate_structure(questions)
        except Exception as e:
            logger.warning("Validation raised: %s", e)
        return questions

    def validate_structure(self, questions):
        nums = [q["numero"] for q in questions if q.get("numero") is not None]
        if len(nums) != len(set(nums)):
            raise ValueError("Duplicate question numbers detected")
        if any(not q.get("enunciado") for q in questions):
            raise ValueError("Empty enunciado found")
        return True

    def save_raw_json(self, out_path: str, data):
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
