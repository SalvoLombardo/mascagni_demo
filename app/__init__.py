import os
from flask import Flask

from .extension import db,bcrypt,migrate,login_manager

from .admin import admin_bp
from .auth import auth_bp
from .main import main_bp


from app.models import Operator
def create_app():
    app=Flask(__name__)

    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres@localhost:5432/mascagni_db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    app.config['SECRET_KEY']='0000'
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