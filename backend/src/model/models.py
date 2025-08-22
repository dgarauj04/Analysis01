from src.extensions import db
from sqlalchemy import UniqueConstraint
from sqlalchemy.dialects.mysql import ENUM, JSON

class Prova(db.Model):
    __tablename__ = "provas"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column(db.String(50), nullable=False)
    ano = db.Column(db.SmallInteger, nullable=False)
    dia = db.Column(db.SmallInteger, nullable=True)
    origem = db.Column(db.String(255), nullable=True)
    arquivos = db.relationship("Questao", backref="prova", cascade="all, delete-orphan")

class Questao(db.Model):
    __tablename__ = "questoes"
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    prova_id = db.Column(db.Integer, db.ForeignKey("provas.id", ondelete="CASCADE"), nullable=False)
    numero = db.Column(db.SmallInteger, nullable=False)
    enunciado = db.Column(db.Text, nullable=False)
    alternativas = db.Column(JSON, nullable=False)
    gabarito = db.Column(db.String(1), nullable=True)
    materia = db.Column(ENUM('Matemática','Física','Química','Biologia','História','Geografia','Filosofia','Sociologia','Linguagens'), nullable=True)
    assunto = db.Column(db.String(50), nullable=True)
    lingua = db.Column(ENUM('PT','INGLES','ESPANHOL'), default='PT')
    definicao = db.Column(db.Text, nullable=True)
    formula = db.Column(db.Text, nullable=True)
    exemplos = db.Column(db.Text, nullable=True)
    dicas = db.Column(db.Text, nullable=True)

    __table_args__ = (UniqueConstraint('prova_id','numero', name='idx_prova_questao'),)

class Assunto(db.Model):
    __tablename__ = "assuntos"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column(db.String(255), unique=True, nullable=False)
    frequencia = db.Column(db.Integer, default=0)
