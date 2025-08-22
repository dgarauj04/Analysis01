import click
import requests
import os
from src.app import create_app, db
from src.services.pdf_processor import PDFProcessor
from src.services.db_service import DBService
from src.model.models import Prova
from flask import current_app

app = create_app()

@click.group()
def cli():
    pass

@cli.command()
@click.option("--file", required=True, type=click.Path(exists=True))
@click.option("--prova", required=True)
@click.option("--ano", required=True, type=int)
@click.option("--dia", type=int, default=None)
@click.option("--materia", default="Geral")
def upload(file, prova, ano, dia, materia):
    """Upload via CLI (local)"""
    with app.app_context():
        pdf_proc = PDFProcessor()
        text = pdf_proc.extract_text(file)
        questions = pdf_proc.parse_questions(text)
        dbs = DBService(db)
        p = dbs.get_or_create_prova(nome=prova, ano=ano, dia=dia, origem=file)
        dbs.insert_questions_batch(p.id, questions, materia)
        click.echo(f"Uploaded {len(questions)} questions to prova {prova}-{ano}")

@cli.command()
@click.option("--step", default="all")
def run_pipeline(step):
    click.echo(f"Running pipeline step={step}")
    if step in ("all","ingest"):
        click.echo("Ingest step - not implemented in CLI demo")

if __name__ == "__main__":
    cli()
