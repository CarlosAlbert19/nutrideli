from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager


app = Flask(__name__)
app.config['SECRET_KEY'] = '260fa31c72684ad278f65cac970229bd'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///C:\\Users\\carlo\\Documents\\nutrideli\\instance\\site.db'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'iniciar_sesion'
login_manager.login_message_category = 'info'

from nutrideli_web import routes