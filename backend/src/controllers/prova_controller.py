from flask import Blueprint, jsonify, current_app, request, url_for
from src.model.models import Prova, Questao
from src.app import db
from src.services.assunto_analyzer import AssuntoAnalyzer

prova_bp = Blueprint("prova", __name__)

@prova_bp.route("/provas", methods=["GET"])
def list_provas():
    """
    Query params:
      - ano (int)
      - nome (string)
      - page (int, default 1)
      - per_page (int, default 20)
    """
    page = request.args.get("page", default=1, type=int)
    per_page = request.args.get("per_page", default=20, type=int)
    ano = request.args.get("ano", type=int)
    nome = request.args.get("nome", type=str)

    q = Prova.query
    if ano:
        q = q.filter_by(ano=ano)
    if nome:
        q = q.filter(Prova.nome.ilike(f"%{nome}%"))

    total = q.count()
    items = q.order_by(Prova.ano.desc(), Prova.id.desc()).offset((page-1)*per_page).limit(per_page).all()
    out = []
    for p in items:
        out.append({"id": p.id, "nome": p.nome, "ano": p.ano, "dia": p.dia, "origem": p.origem})
    meta = {
        "page": page,
        "per_page": per_page,
        "total": total,
        "pages": (total + per_page - 1) // per_page
    }
    return jsonify({"meta": meta, "items": out})

@prova_bp.route("/provas/<int:prova_id>/questoes", methods=["GET"])
def list_questoes(prova_id):
    q = Questao.query.filter_by(prova_id=prova_id).all()
    out = []
    for item in q:
        out.append({
            "id": item.id,
            "numero": item.numero,
            "enunciado": item.enunciado,
            "alternativas": item.alternativas,
            "gabarito": item.gabarito,
            "materia": item.materia,
            "assunto": item.assunto,
            "lingua": item.lingua
        })
    return jsonify(out)

@prova_bp.route("/provas/<int:prova_id>/assuntos", methods=["GET"])
def prova_assuntos(prova_id):
    qs = Questao.query.filter_by(prova_id=prova_id).all()
    questions = []
    for q in qs:
        questions.append({
            "numero": q.numero,
            "enunciado": q.enunciado,
            "alternativas": q.alternativas,
            "gabarito": q.gabarito,
            "materia": q.materia or "Geral"
        })
    analyzer = AssuntoAnalyzer()
    result = analyzer.analyze_questions(questions)
    return jsonify(result)