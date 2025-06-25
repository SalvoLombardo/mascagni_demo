from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_migrate import Migrate



db=SQLAlchemy()
bcrypt=Bcrypt()
migrate=Migrate()
login_manager = LoginManager()



