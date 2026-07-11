import os
from flask import Flask, send_from_directory
from flask_cors import CORS
from config import Config
from extensions import db, security
from security_setup import user_datastore

FRONTEND_DIR = os.path.join(os.path.dirname(__file__), '..', 'frontend')

def create_app(test_config=None):
    app = Flask(__name__)
    app.config.from_object(Config)

    if test_config:
        app.config.update(test_config)

    CORS(app)
    db.init_app(app)
    security.init_app(app, user_datastore)
    security.want_json(lambda req: req.path.startswith('/api/') or req.is_json)

    from routes.auth import auth_bp
    from routes.skills import skills_bp
    from routes.offerings import offerings_bp
    from routes.requests import requests_bp
    from routes.sessions import sessions_bp
    from routes.dashboard import dashboard_bp
    from routes.admin import admin_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(skills_bp, url_prefix='/api/skills')
    app.register_blueprint(offerings_bp, url_prefix='/api/offerings')
    app.register_blueprint(requests_bp, url_prefix='/api')
    app.register_blueprint(sessions_bp, url_prefix='/api')
    app.register_blueprint(dashboard_bp, url_prefix='/api')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')

    @app.route('/')
    def serve_index():
        return send_from_directory(FRONTEND_DIR, 'index.html')

    @app.route('/js/<path:filename>')
    def serve_js(filename):
        return send_from_directory(os.path.join(FRONTEND_DIR, 'js'), filename)

    @app.route('/css/<path:filename>')
    def serve_css(filename):
        return send_from_directory(os.path.join(FRONTEND_DIR, 'css'), filename)

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5001)
