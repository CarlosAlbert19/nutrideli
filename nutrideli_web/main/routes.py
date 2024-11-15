from flask import render_template, request, Blueprint, flash, redirect, url_for, session
from nutrideli_web.models import Post
from flask_login import login_required, current_user
from nutrideli_web.main.forms import CrearDietaForm
from nutrideli_web import db
from nutrideli_web.ai_model.dieta_modelo import calculate_calories_basic, better_model
from datetime import datetime
import json
import os
from werkzeug.utils import secure_filename
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.models import load_model
import numpy as np

main = Blueprint('main', __name__)


@main.route("/")
@main.route("/inicio")
def inicio():
    return render_template ('inicio.html', titulo_pagina='Inicio', es_inicio=True)

@main.context_processor
def inject_consejo_del_dia():
    dia_actual = datetime.now().day
    with open('nutrideli_web/static/consejos.json', 'r', encoding='utf-8') as f:
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
        with open('nutrideli_web\\static\\alimentos-nutrimentos.json', 'r', encoding='utf-8') as file:
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

@main.route('/procesar_imagen', methods=['POST'])
def procesar_imagen():
    if 'file' not in request.files:
        flash('No se seleccionó ningún archivo', 'warning')
        return redirect(url_for('main.nutripedia'))

    file = request.files['file']
    
    if file.filename == '':
        flash('No se seleccionó ningún archivo', 'warning')
        return redirect(url_for('main.nutripedia'))

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join('nutrideli_web\\main\\uploads', filename)
        file.save(filepath)

        # Procesar la imagen con el modelo de IA
        nombre_alimento = procesar_imagen_con_ia(filepath)

        # Redirigir a la barra de búsqueda con el resultado del modelo
        return redirect(url_for('main.buscar_alimento_automatico', alimento=nombre_alimento))

    flash('Formato de archivo no permitido. Solo se permiten JPG y PNG.', 'danger')
    return redirect(url_for('main.nutripedia'))

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'jpg', 'jpeg', 'png'}

def procesar_imagen_con_ia(filepath):
    model = tf.keras.models.load_model('nutrideli_web\\main\\Image_classify.keras')

    img_height, img_width = 180, 180
    data_cat = ['ajo', 'berenjena', 'cebolla', 'coliflor', 'espinaca', 'frijoles', 'granada', 'guisantes', 'jalepeno', 'jengibre', 'kiwi', 'lechuga', 'limon', 'maiz', 'maiz dulce', 'mango', 'manzana', 'nabo', 'naranja', 'papa', 'papa culce', 'paprica', 'pepino', 'pera', 'pimiento', 'pimiento morron', 'pimiento picante', 'pina', 'platano', 'rabano', 'remolacha', 'repollo', 'sandia', 'tomate', 'uvas', 'zanahoria']
    
    image = tf.keras.utils.load_img(filepath, target_size=(img_height, img_width))
    img_arr = tf.keras.utils.img_to_array(image)
    img_bat = np.expand_dims(img_arr, 0)

    predict = model.predict(img_bat)

    score = tf.nn.softmax(predict)
    
    nombre_alimento = data_cat[np.argmax(score)]
    
    return nombre_alimento.capitalize()

@main.route('/buscar_alimento_automatico', methods=['GET'])
def buscar_alimento_automatico():
    alimento_buscado = request.args.get('alimento')

    # Cargar el archivo JSON de alimentos (igual que en buscar_alimento)
    try:
        with open('nutrideli_web\\static\\alimentos-nutrimentos.json', 'r', encoding='utf-8') as file:
            data = json.load(file)

        # Buscar el alimento en el archivo JSON
        resultado = next((item for item in data['alimentos'] if item['nombre'] == alimento_buscado), None)

        if resultado:
            return render_template('nutripedia-res.html', alimento=resultado)
        else:
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
        
        # dieta = Dieta(altura=altura, peso=peso, sexo=sexo, objetivo=objetivo, author=current_user)
        # db.session.add(dieta)
        # db.session.commit()

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