from flask import Flask, render_template, url_for, flash, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import pytz
from forms import Registro, Iniciar_sesion

app = Flask(__name__)
app.config['SECRET_KEY'] = '260fa31c72684ad278f65cac970229bd'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)

class User(db.Model):
      id = db.Column(db.Integer, primary_key=True)
      username = db.Column(db.String(25), unique=True, nullable=False)
      email = db.Column(db.String(120), unique=True, nullable=False)
      image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
      password = db.Column(db.String(60), nullable=False)
      posts = db.relationship('Post', backref='author', lazy=True)


      def __repr__(self):
            return f"User('{self.username}', '{self.email}', '{self.image_file}')"
      

class Post(db.Model):
      id = db.Column(db.Integer, primary_key=True)
      title = db.Column(db.String(100), nullable=False)
      date_posted = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(pytz.timezone('America/Mexico_City')))
      content = db.Column(db.Text, nullable=False)
      user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

      def __repr__(self):
            return f"Post('{self.title}', '{self.date_posted}')"

publicaciones = [
     {
          'autor': 'Carlos Reyes',
          'titulo': 'Publicacion 1',
          'contenido': 'Primera publicación de la plataforma',
          'fecha_publicada': '1 de agosto de 2024'
     },
     {
          'autor': 'Marcos Guzman',
          'titulo': 'Publicacion 2',
          'contenido': 'Segunda publicación de la plataforma',
          'fecha_publicada': '2 de agosto de 2024'
     }
]

@app.route("/")
@app.route("/inicio")
def inicio():
    return render_template ('inicio.html', titulo_pagina='Inicio')

@app.route("/publicaciones")
def blog_publicaciones():
    return render_template ('publicaciones.html', publicaciones=publicaciones, titulo_pagina='Publicaciones')

@app.route("/nutripedia")
def nutripedia():
    return render_template ('nutripedia.html', titulo_pagina='Nutripedia')

@app.route("/acerca_de")
def acerca_de():
    return render_template ('acerca_de.html', titulo_pagina='Acerca de')

@app.route("/registro", methods=['GET', 'POST'])
def registro():
    form = Registro()
    if form.validate_on_submit():
                 flash(f'¡Cuenta creada para {form.username.data}!', 'success')
                 return redirect(url_for('inicio'))
    return render_template ('registro.html', titulo_pagina='Registro', form=form)
@app.route("/iniciar_sesion", methods=['GET', 'POST'])
def iniciar_sesion():
    form = Iniciar_sesion()
    if form.validate_on_submit():
          if form.email.data == 'admin@blog.com' and form.password.data == 'password':
                flash('¡Se ha iniciado sesión exitosamente!', 'success')
                return redirect(url_for('inicio'))
          else:
                flash('Lo sentimos, no se ha podido iniciar sesión. Compruebe que el correo y la contraseña sean correctos.', 'danger')
    return render_template ('iniciar_sesion.html', titulo_pagina='Iniciar sesión', form=form)



if __name__ == '__main__':
        app.run(debug=True)