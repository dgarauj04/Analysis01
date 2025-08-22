import os
import hashlib
from flask import Blueprint, request, current_app, jsonify
from werkzeug.utils import secure_filename
from src.services.pdf_processor import PDFProcessor
from src.services.db_service import DBService
from src.extensions import db
from src.model.models import Prova, Questao

upload_bp = Blueprint("upload", __name__)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.',1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

@upload_bp.route("/upload", methods=["POST"])
def upload_file():
    """
    Expects multipart/form-data:
    - file: binary
    - prova: ENEM
    - ano: 2023
    - dia: 1
    - materia: Matemática
    """
    f = request.files.get("file")
    gfile = request.files.get("gabarito_file")
    prova = request.form.get("prova")
    ano = request.form.get("ano", type=int)
    dia = request.form.get("dia", type=int)
    materia = request.form.get("materia", "Geral")

    if not f or not allowed_file(f.filename):
        return jsonify({"error": "Arquivo inválido"}), 400

    filename = secure_filename(f.filename)
    # build storage path
    folder = os.path.join(current_app.config['UPLOAD_FOLDER'], prova, str(ano), str(dia or 0), materia)
    os.makedirs(folder, exist_ok=True)
    file_path = os.path.join(folder, filename)

    # Read bytes, compute hash
    content = f.read()
    sha = hashlib.sha256(content).hexdigest()
    # check duplicates: if any file with same sha exists -> reject or log
    hash_db_path = os.path.join(folder, f".{sha}.sha")
    if os.path.exists(hash_db_path):
        current_app.logger.info("Arquivo duplicado detectado SHA: %s", sha)
        return jsonify({"error": "Duplicated file", "sha256": sha}), 409

    with open(file_path, "wb") as out:
        out.write(content)
    with open(hash_db_path, "w") as h:
        h.write(sha)

   # Process PDF
    pdf_proc = PDFProcessor()
    try:
        text = pdf_proc.extract_text(file_path)
        questions = pdf_proc.parse_questions(text)

        # if many questions missing gabarito, try to parse gabarito from same PDF
        missing = [q for q in questions if not q.get("gabarito")]
        detected_gabarito = pdf_proc.parse_gabarito_pdf(text)
        if missing and (not detected_gabarito or len(detected_gabarito) < 5):
                if gfile:
                    gname = secure_filename(gfile.filename)
                    gpath = os.path.join(folder, f"gabarito_{gname}")
                    gfile.save(gpath)
                    detected_gabarito = pdf_proc.parse_gabarito_pdf(gpath)
                else:
                        return jsonify({"error": "Gabarito não encontrado no arquivo de questões. Envie 'gabarito_file' (PDF de gabarito)."}), 400
            # apply detected gabarito
            if detected_gabarito:
                for q in questions:
                    if not q.get("gabarito") and q.get("numero") in detected_gabarito:
                        q["gabarito"] = detected_gabarito[q["numero"]]
        # Save raw JSON
        raw_out_dir = os.path.join(current_app.config['RAW_OUTPUT'], prova)
        os.makedirs(raw_out_dir, exist_ok=True)
        raw_path = os.path.join(raw_out_dir, f"{prova}_{ano}.json")
        pdf_proc.save_raw_json(raw_path, questions)

        # Insert into DB
        with current_app.app_context():
            db_svc = DBService(db)
            prova_obj = db_svc.get_or_create_prova(nome=prova, ano=ano, dia=dia, origem=file_path)
            db_svc.insert_questions_batch(prova_obj.id, questions, materia)

        return jsonify({"status": "uploaded", "sha256": sha, "questions_extracted": len(questions)}), 201
    except Exception as e:
        current_app.logger.exception("Erro no processamento do PDF")
        return jsonify({"error": str(e)}), 500
