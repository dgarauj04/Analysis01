from src.model.models import Prova, Questao, Assunto
from sqlalchemy.exc import IntegrityError
from flask import current_app
import logging

logger = logging.getLogger(__name__)

class DBService:
    def __init__(self, db):
        self.db = db

    def get_or_create_prova(self, nome, ano, dia=None, origem=None):
        p = Prova.query.filter_by(nome=nome, ano=ano, dia=dia).first()
        if p:
            return p
        p = Prova(nome=nome, ano=ano, dia=dia, origem=origem)
        self.db.session.add(p)
        self.db.session.commit()
        return p

    def insert_questions_batch(self, prova_id, questions, materia):
        from src.extensions import db
        sess = db.session
        try:
            for q in questions:
                q_obj = Questao(
                    prova_id=prova_id,
                    numero=q.get("numero"),
                    enunciado=q.get("enunciado"),
                    alternativas=q.get("alternativas") or {},
                    gabarito=q.get("gabarito"),
                    materia=materia
                )
                sess.add(q_obj)
            sess.commit()
            logger.info("Inserted %d questions into prova %d", len(questions), prova_id)
        except IntegrityError as e:
            sess.rollback()
            logger.exception("DB integrity error during batch insert")
            raise
        except Exception:
            sess.rollback()
            logger.exception("Unexpected DB error")
            raise
