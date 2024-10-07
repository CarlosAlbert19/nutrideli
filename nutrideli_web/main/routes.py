from flask import render_template, request, Blueprint, flash, redirect, url_for, session
from nutrideli_web.models import Post
from flask_login import login_required, current_user
from nutrideli_web.main.forms import CrearDietaForm
from nutrideli_web import db
from nutrideli_web.ai_model.dieta_modelo import calculate_calories_basic, better_model
from datetime import datetime
import json

main = Blueprint('main', __name__)


@main.route("/")
@main.route("/inicio")
def inicio():
    return render_template ('inicio.html', titulo_pagina='Inicio', es_inicio=True)

@main.context_processor
def inject_consejo_del_dia():
    dia_actual = datetime.now().day
    with open('C:\\Users\\carlo\\Documents\\nutrideli\\nutrideli_web\\static\\consejos.json', 'r', encoding='utf-8') as f:
        consejos = json.load(f)
    consejo_del_dia = consejos.get(str(dia_actual))

    return dict(consejo_del_dia=consejo_del_dia)

@main.route("/publicaciones")
def blog_publicaciones():
    page = request.args.get('page', 1, type=int)
    publicaciones = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=10)
    return render_template ('publicaciones.html', publicaciones=publicaciones, titulo_pagina='Publicaciones', es_inicio=False)

@main.route("/nutripedia")
def nutripedia():
    return render_template ('nutripedia.html', titulo_pagina='Nutripedia', es_inicio=False)


@main.route('/buscar_alimento', methods=['POST'])
def buscar_alimento():
    # Obtener el nombre del alimento desde el formulario
    alimento_buscado = request.form['alimento'].capitalize()

    # Cargar el archivo JSON de alimentos
    try:
        with open('C:\\Users\\carlo\\Documents\\nutrideli\\nutrideli_web\\static\\alimentos-nutrimentos.json', 'r', encoding='utf-8') as file:
            data = json.load(file)

        # Buscar el alimento en el archivo JSON
        resultado = next((item for item in data['alimentos'] if item['nombre'] == alimento_buscado), None)

        if resultado:
            # Si el alimento se encuentra, mostrar la página con los detalles
            return render_template('nutripedia-res.html', alimento=resultado)
        else:
            # Si el alimento no se encuentra, mostrar un mensaje de error
            flash("El alimento no fue encontrado en la enciclopedia.", 'warning')
            return redirect(url_for('main.nutripedia'))
    
    except FileNotFoundError:
        flash("El archivo de datos no se encuentra.", 'danger')
        return redirect(url_for('main.nutripedia'))



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

        calorias = calculate_calories_basic(peso, altura, sexo)
        dieta = better_model(peso, calorias)

        # print(dieta)
        # print(calorias)
        
        # Aquí es donde procesarías los datos, por ejemplo:
        # dieta = Dieta(altura=altura, peso=peso, sexo=sexo, objetivo=objetivo, author=current_user)
        # db.session.add(dieta)
        # db.session.commit()
        
        # Por ahora, simplemente mostraremos un mensaje de éxito

        flash('¡Tu dieta ha sido creada exitosamente!', 'success')
        #return redirect(url_for('main.dieta_creada'))
        return render_template('dieta_creada.html', titulo_pagina='Dieta creada', dieta=dieta, calorias=calorias, es_inicio=False)
    return render_template('crear_dieta.html', titulo_pagina='Crear Dieta', form=form, es_inicio=False)


@main.route("/dieta_creada")
def dieta_creada():
    dieta = session.get('dieta', None)
    if not dieta:
        flash('Por favor, crea una dieta primero.', 'warning')
        return redirect(url_for('main.crear_dieta'))
    return render_template ('dieta_creada.html', titulo_pagina='Dieta creada', dieta=dieta, es_inicio=False)