from flask import Flask
from models.database import init_db
from routes.auth import auth_bp
from routes.officer import officer_bp
from routes.admin import admin_bp
import os

app = Flask(__name__)
app.secret_key = 'borderwatch_secret_key_2024'
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

app.register_blueprint(auth_bp)
app.register_blueprint(officer_bp)
app.register_blueprint(admin_bp)

# Initialize database on startup (works with both gunicorn and direct run)
init_db()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
