from flask import Flask
from config import LocalDevelopmentConfig
from models import db, create_admin
from routes import api, register_blueprints
from security import jwt
from flask_cors import CORS
import os

app = None

def create_app():
    app = Flask(__name__)
    app.config.from_object(LocalDevelopmentConfig)
    db.init_app(app)
    jwt.init_app(app)
    api.init_app(app)
    CORS(
        app,
        origins="http://localhost:5173",
        supports_credentials=True,
    )
    register_blueprints(app)


    with app.app_context():
        db.create_all()
        admin_email = os.getenv("ADMIN_EMAIL")
        admin_password = os.getenv("ADMIN_PASSWORD")
        create_admin(app,admin_email,admin_password)

    return app

app = create_app()

if __name__ == "__main__":
    app.run()