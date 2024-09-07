from flask import render_template, url_for, flash, redirect, request
from nutrideli_web import app, db, bcrypt
from nutrideli_web.forms import Registro, Iniciar_sesion
from nutrideli_web.models import User, Post
from flask_login import login_user, current_user, logout_user, login_required


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
    if current_user.is_authenticated:
         return redirect(url_for('inicio'))
    form = Registro()
    if form.validate_on_submit():
                 hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
                 user = User(username=form.username.data, email=form.email.data, password=hashed_password)
                 db.session.add(user)
                 db.session.commit()
                 flash(f'¡Tu cuenta ha sido creada exitosamente, ahora inicia sesión para comenzar a usar NutriDeli!', 'success')
                 return redirect(url_for('iniciar_sesion'))
    return render_template ('registro.html', titulo_pagina='Registro', form=form)

@app.route("/iniciar_sesion", methods=['GET', 'POST'])
def iniciar_sesion():
    if current_user.is_authenticated:
         return redirect(url_for('inicio'))
    form = Iniciar_sesion()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('inicio'))
        else:
            flash('Lo sentimos, no se ha podido iniciar sesión. Compruebe que el correo y la contraseña sean correctos.', 'danger')
    return render_template ('iniciar_sesion.html', titulo_pagina='Iniciar sesión', form=form)

@app.route("/cerrar_sesion")
def cerrar_sesion():
     logout_user()
     return redirect(url_for('inicio'))

@app.route("/cuenta")
@login_required
def cuenta():
     return render_template ('cuenta.html', titulo_pagina='Cuenta')

