from src.app import create_app, db
from config import Config
app = create_app(Config)

if __name__ == "__main__":
    # In production use gunicorn
    app.run(host="0.0.0.0", port=5000, debug=False)
