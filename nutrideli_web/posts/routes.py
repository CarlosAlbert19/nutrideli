from flask import render_template, url_for, flash, redirect, request, abort, Blueprint
from flask_login import current_user, login_required
from nutrideli_web import db
from nutrideli_web.models import Post
from nutrideli_web.posts.forms import Publicacion

posts = Blueprint('posts', __name__)

@posts.route("/publicaciones/nueva", methods=['GET', 'POST'])
@login_required
def nueva_publicacion():
    form = Publicacion()
    if form.validate_on_submit():
         post = Post(title=form.title.data, content=form.content.data, author=current_user)
         db.session.add(post)
         db.session.commit()
         flash('¡Tu publicación ha sido creada!', 'success')
         return redirect(url_for('main.blog_publicaciones'))
    return render_template ('crear_publicacion.html', titulo_pagina='Nueva Publicacion', form=form, legend='¡Comparte tus experiencias con los demás usuarios!', es_inicio=False)


@posts.route("/publicaciones/<int:post_id>")
def post(post_id):
     post = Post.query.get_or_404(post_id)
     return render_template ('publi.html', title=post.title, publicacion=post, es_inicio=False)


@posts.route("/publicaciones/<int:post_id>/modificar", methods=['GET', 'POST'])
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
          return redirect(url_for('posts.post', post_id=post.id))
     elif request.method == 'GET':
          form.title.data = post.title
          form.content.data = post.content
     return render_template ('crear_publicacion.html', titulo_pagina='Modificar Publicacion', form=form, legend='Modificar Publicación', es_inicio=False)


@posts.route("/publicaciones/<int:post_id>/eliminar", methods=['POST'])
@login_required
def eliminar_post(post_id):
     post = Post.query.get_or_404(post_id)
     if post.author != current_user:
          abort(403)
     db.session.delete(post)
     db.session.commit()
     flash('¡Tu publicación ha sido eliminada!', 'success')
     return redirect(url_for('main.blog_publicaciones'))