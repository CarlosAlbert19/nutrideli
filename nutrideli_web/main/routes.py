from flask import render_template, request, Blueprint
from nutrideli_web.models import Post

main = Blueprint('main', __name__)


@main.route("/")
@main.route("/inicio")
def inicio():
    return render_template ('inicio.html', titulo_pagina='Inicio')

@main.route("/publicaciones")
def blog_publicaciones():
    page = request.args.get('page', 1, type=int)
    publicaciones = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=10)
    return render_template ('publicaciones.html', publicaciones=publicaciones, titulo_pagina='Publicaciones')

@main.route("/nutripedia")
def nutripedia():
    return render_template ('nutripedia.html', titulo_pagina='Nutripedia')

@main.route("/acerca_de")
def acerca_de():
    return render_template ('acerca_de.html', titulo_pagina='Acerca de')