from flask import render_template, url_for, flash, redirect, request, Blueprint
from flask_login import login_user, current_user, logout_user, login_required
from nutrideli_web import db, bcrypt
from nutrideli_web.models import User, Post
from nutrideli_web.users.forms import Registro, Iniciar_sesion, Actualizar_informacion, RequestResetForm, ResetPasswordForm
from nutrideli_web.users.utils import save_picture, send_reset_email

users = Blueprint('users', __name__)


@users.route("/registro", methods=['GET', 'POST'])
def registro():
    if current_user.is_authenticated:
         return redirect(url_for('main.inicio'))
    form = Registro()
    if form.validate_on_submit():
                 hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
                 user = User(username=form.username.data, email=form.email.data, password=hashed_password)
                 db.session.add(user)
                 db.session.commit()
                 flash(f'¡Tu cuenta ha sido creada exitosamente, ahora inicia sesión para comenzar a usar NutriDeli!', 'success')
                 return redirect(url_for('users.iniciar_sesion'))
    return render_template ('registro.html', titulo_pagina='Registro', form=form, es_inicio=False)

@users.route("/iniciar_sesion", methods=['GET', 'POST'])
def iniciar_sesion():
    if current_user.is_authenticated:
         return redirect(url_for('main.inicio'))
    form = Iniciar_sesion()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.inicio'))
        else:
            flash('Lo sentimos, no se ha podido iniciar sesión. Compruebe que el correo y la contraseña sean correctos.', 'danger')
    return render_template ('iniciar_sesion.html', titulo_pagina='Iniciar sesión', form=form, es_inicio=False)

@users.route("/cerrar_sesion")
def cerrar_sesion():
     logout_user()
     return redirect(url_for('main.inicio'), es_inicio=False)


@users.route("/cuenta", methods=['GET', 'POST'])
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
          return redirect(url_for('users.cuenta'))
     elif request.method == 'GET':
          form.username.data = current_user.username
          form.email.data = current_user.email
     image_file =url_for('static', filename='profile_pics/' + current_user.image_file)
     return render_template ('cuenta.html', titulo_pagina='Cuenta', image_file=image_file, form=form, es_inicio=False)


@users.route("/usuario/<string:username>")
def user_posts(username):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    publicaciones = Post.query.filter_by(author=user).order_by(Post.date_posted.desc()).paginate(page=page, per_page=10)
    return render_template ('publicaciones_usuario.html', publicaciones=publicaciones, titulo_pagina='Publicaciones de usuario', user=user, es_inicio=False)


@users.route("/reestablecer_password", methods=['GET', 'POST'])
def reset_request():
     if current_user.is_authenticated:
         return redirect(url_for('main.inicio'))
     form = RequestResetForm()
     if form.validate_on_submit():
          user = User.query.filter_by(email=form.email.data).first()
          send_reset_email(user)
          flash('Un correo con instrucciones se ha enviado a tu correo para reestablecer tu contraseña.', 'info')
          return redirect(url_for('users.iniciar_sesion'))
     return render_template('reestablecer_password.html', title='Reestablecer Password', form=form, es_inicio=False)


@users.route("/reestablecer_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
     if current_user.is_authenticated:
         return redirect(url_for('main.inicio'))
     user = User.verify_reset_token(token)
     if user is None:
          flash('Ese token es inválido o ya ha expirado.', 'warning')
          return redirect(url_for('users.reset_request'))
     form = ResetPasswordForm()
     if form.validate_on_submit():
                 hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
                 user.password = hashed_password
                 db.session.commit()
                 flash(f'¡Tu contraseña ha sido reestablecida exitosamente, ahora inicia sesión para volver a usar NutriDeli!', 'success')
                 return redirect(url_for('users.iniciar_sesion'))
     return render_template('reestablecer_token.html', title='Reestablecer Password', form=form, es_inicio=False)