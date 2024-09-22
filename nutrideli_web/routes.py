import os
import secrets
from PIL import Image
from flask import render_template, url_for, flash, redirect, request, abort
from nutrideli_web import app, db, bcrypt, mail
from nutrideli_web.forms import Registro, Iniciar_sesion, Actualizar_informacion, Publicacion, RequestResetForm, ResetPasswordForm
from nutrideli_web.models import User, Post
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message


@app.route("/")
@app.route("/inicio")
def inicio():
    return render_template ('inicio.html', titulo_pagina='Inicio')

@app.route("/publicaciones")
def blog_publicaciones():
    page = request.args.get('page', 1, type=int)
    publicaciones = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=10)
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

def save_picture(form_picture):
     random_hex = secrets.token_hex(8)
     _, f_ext = os.path.splitext(form_picture.filename)
     picture_fn = random_hex + f_ext
     picture_path= os.path.join(app.root_path, 'static/profile_pics', picture_fn)

     output_size = (125, 125)
     i = Image.open(form_picture)
     i.thumbnail(output_size)
     i.save(picture_path)

     return picture_fn

@app.route("/cuenta", methods=['GET', 'POST'])
@login_required
def cuenta():
     form = Actualizar_informacion()
     if form.validate_on_submit():
          if form.picture.data:
               picture_file = save_picture(form.picture.data)
               current_user.image_file = picture_file
          current_user.username = form.username.data
          current_user.email = form.email.data
          db.session.commit()
          flash('¡Tu cuenta ha sido actualizada exitosamente!', 'success')
          return redirect(url_for('cuenta'))
     elif request.method == 'GET':
          form.username.data = current_user.username
          form.email.data = current_user.email
     image_file =url_for('static', filename='profile_pics/' + current_user.image_file)
     return render_template ('cuenta.html', titulo_pagina='Cuenta', image_file=image_file, form=form)


@app.route("/publicaciones/nueva", methods=['GET', 'POST'])
@login_required
def nueva_publicacion():
    form = Publicacion()
    if form.validate_on_submit():
         post = Post(title=form.title.data, content=form.content.data, author=current_user)
         db.session.add(post)
         db.session.commit()
         flash('¡Tu publicación ha sido creada!', 'success')
         return redirect(url_for('blog_publicaciones'))
    return render_template ('crear_publicacion.html', titulo_pagina='Nueva Publicacion', form=form, legend='¡Comparte tus experiencias con los demás usuarios!')


@app.route("/publicaciones/<int:post_id>")
def post(post_id):
     post = Post.query.get_or_404(post_id)
     return render_template ('publi.html', title=post.title, publicacion=post)


@app.route("/publicaciones/<int:post_id>/modificar", methods=['GET', 'POST'])
@login_required
def modificar_post(post_id):
     post = Post.query.get_or_404(post_id)
     if post.author != current_user:
          abort(403)
     form = Publicacion()
     if form.validate_on_submit():
          post.title = form.title.data
          post.content= form.content.data
          db.session.commit()
          flash('¡Tu publicación ha sido modificada!', 'success')
          return redirect(url_for('post', post_id=post.id))
     elif request.method == 'GET':
          form.title.data = post.title
          form.content.data = post.content
     return render_template ('crear_publicacion.html', titulo_pagina='Modificar Publicacion', form=form, legend='Modificar Publicación')


@app.route("/publicaciones/<int:post_id>/eliminar", methods=['POST'])
@login_required
def eliminar_post(post_id):
     post = Post.query.get_or_404(post_id)
     if post.author != current_user:
          abort(403)
     db.session.delete(post)
     db.session.commit()
     flash('¡Tu publicación ha sido eliminada!', 'success')
     return redirect(url_for('blog_publicaciones'))


@app.route("/usuario/<string:username>")
def user_posts(username):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    publicaciones = Post.query.filter_by(author=user).order_by(Post.date_posted.desc()).paginate(page=page, per_page=10)
    return render_template ('publicaciones_usuario.html', publicaciones=publicaciones, titulo_pagina='Publicaciones de usuario', user=user)

def send_reset_email(user):
     token = user.get_reset_token()
     msg = Message('Solicitud de Reestablecimiento de Contraseña', sender='noreply@nutrideli.com', recipients=[user.email])
     msg.body = f'''Para reestablecer tu contraseña, haz clic en el siguiente enlace:
{url_for('reset_token', token=token, _external=True)}

Si no realizaste esta solicitud, simplemente ignora este correo y no se realizará ningún cambio.
'''
     mail.send(msg)


@app.route("/reestablecer_password", methods=['GET', 'POST'])
def reset_request():
     if current_user.is_authenticated:
         return redirect(url_for('inicio'))
     form = RequestResetForm()
     if form.validate_on_submit():
          user = User.query.filter_by(email=form.email.data).first()
          send_reset_email(user)
          flash('Un correo con instrucciones se ha enviado a tu correo para reestablecer tu contraseña.', 'info')
          return redirect(url_for('iniciar_sesion'))
     return render_template('reestablecer_password.html', title='Reestablecer Password', form=form)


@app.route("/reestablecer_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
     if current_user.is_authenticated:
         return redirect(url_for('inicio'))
     user = User.verify_reset_token(token)
     if user is None:
          flash('Ese token es inválido o ya ha expirado.', 'warning')
          return redirect(url_for('reset_request'))
     form = ResetPasswordForm()
     if form.validate_on_submit():
                 hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
                 user.password = hashed_password
                 db.session.commit()
                 flash(f'¡Tu contraseña ha sido reestablecida exitosamente, ahora inicia sesión para volver a usar NutriDeli!', 'success')
                 return redirect(url_for('iniciar_sesion'))
     return render_template('reestablecer_token.html', title='Reestablecer Password', form=form)



