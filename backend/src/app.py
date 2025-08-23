from flask import Flask, jsonify
import logging
from logging.handlers import RotatingFileHandler
from config import Config, BASE_DIR
from flask_swagger_ui import get_swaggerui_blueprint 
from flask_cors import CORS
from src.extensions import db  
from src.model import models
import os 
  
def create_app(config_object=Config):
    app = Flask(__name__, static_folder="static")
    app.config.from_object(config_object)
    
    CORS(app, resources={r"/*": {"origins": "*"}})

    log_dir = os.path.join(os.path.dirname(BASE_DIR), "logs")
    os.makedirs(log_dir, exist_ok=True)
    log_path = os.path.join(log_dir, "app.log")
    
    handler = RotatingFileHandler(log_path, maxBytes=10*1024*1024, backupCount=5)
    handler.setLevel(logging.INFO)
    fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    handler.setFormatter(fmt)
    app.logger.addHandler(handler)
    app.logger.setLevel(logging.INFO)

    # DB
    db.init_app(app)
    with app.app_context():
        db.create_all()

    from .controllers.upload_controller import upload_bp
    from .controllers.prova_controller import prova_bp

    # Blueprints / controllers
    app.register_blueprint(upload_bp, url_prefix="/api")
    app.register_blueprint(prova_bp, url_prefix="/api")

    # Swagger UI
    SWAGGER_URL = '/docs'
    API_URL = '/static/swagger.yaml'  # serve static file
    swaggerui_blueprint = get_swaggerui_blueprint(SWAGGER_URL, API_URL, config={'app_name': "ENEM Analyzer"})
    app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

    # Error handlers
    @app.errorhandler(413)
    def request_entity_too_large(error):
        return jsonify({"error": "File too large"}), 413

    @app.route("/health")
    def health():
        return jsonify({"status": "ok"})

    return app
