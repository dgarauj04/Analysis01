import os
from dotenv import load_dotenv
load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret")
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URI", "mysql+mysqlconnector://user:pass@localhost:3306/enemdb")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.environ.get("UPLOAD_FOLDER", os.path.join(os.path.dirname(BASE_DIR), "data", "uploads"))
    RAW_OUTPUT = os.environ.get("RAW_OUTPUT", os.path.join(os.path.dirname(BASE_DIR), "data", "raw"))
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB
    ALLOWED_EXTENSIONS = {"pdf", "docx", "txt"}
    TESSERACT_LANG = os.environ.get("TESSERACT_LANG", "por")
