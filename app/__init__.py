import os
from flask import Flask
from dotenv import load_dotenv

from .extension import db,bcrypt,migrate,login_manager

from .admin import admin_bp
from .auth import auth_bp
from .main import main_bp


from app.models import Operator

from config import DevelopmentConfig,ProductionConfig


load_dotenv()


def create_app(test_config:dict | None=None):
    app=Flask(__name__)

    #++++++++++++++++++++++ DEMO MODE +++++++++++++++++++++++++++++++++++#
    env = os.getenv("FLASK_ENV", "development")
    app.config.from_object(
        DevelopmentConfig if env == "development" else ProductionConfig
    )
    #++++++++++++++++++++++ DEMO MODE +++++++++++++++++++++++++++++++++++#


    if test_config:
        app.config.update(test_config)

    
    
    #initializing extensions
    db.init_app(app)
    bcrypt.init_app(app)
    migrate.init_app(app,db)

    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return Operator.query.get(int(user_id))

    #registering blueprints
    app.register_blueprint(admin_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)

    return app