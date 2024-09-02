from flask import render_template, url_for, flash, redirect
from nutrideli_web import app
from nutrideli_web.forms import Registro, Iniciar_sesion
from nutrideli_web.models import User, Post


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