from flask import Flask
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['SECRET_KEY'] = '260fa31c72684ad278f65cac970229bd'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///C:\\Users\\carlo\\Documents\\nutrideli\\instance\\site.db'
db = SQLAlchemy(app)

from nutrideli_web import routes