from flask import render_template, request, Blueprint, flash, redirect, url_for
from nutrideli_web.models import Post
from flask_login import login_required, current_user
from nutrideli_web.main.forms import CrearDietaForm

main = Blueprint('main', __name__)


@main.route("/")
@main.route("/inicio")
def inicio():
    return render_template ('inicio.html', titulo_pagina='Inicio', es_inicio=True)

@main.route("/publicaciones")
def blog_publicaciones():
    page = request.args.get('page', 1, type=int)
    publicaciones = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=10)
    return render_template ('publicaciones.html', publicaciones=publicaciones, titulo_pagina='Publicaciones', es_inicio=False)

@main.route("/nutripedia")
def nutripedia():
    return render_template ('nutripedia.html', titulo_pagina='Nutripedia', es_inicio=False)

@main.route("/acerca_de")
def acerca_de():
    return render_template ('acerca_de.html', titulo_pagina='Acerca de', es_inicio=False)

@main.route("/crear_dieta", methods=['GET', 'POST'])
@login_required
def crear_dieta():
    form = CrearDietaForm()
    if form.validate_on_submit():
        altura = form.altura.data
        peso = form.peso.data
        sexo = form.sexo.data
        objetivo = form.objetivo.data
        
        # Aquí es donde procesarías los datos, por ejemplo:
        # dieta = Dieta(altura=altura, peso=peso, sexo=sexo, objetivo=objetivo, author=current_user)
        # db.session.add(dieta)
        # db.session.commit()
        
        # Por ahora, simplemente mostraremos un mensaje de éxito
        flash('¡Tu dieta ha sido creada exitosamente!', 'success')
        return redirect(url_for('main.inicio'))
    return render_template('crear_dieta.html', titulo_pagina='Crear Dieta', form=form, es_inicio=False)
