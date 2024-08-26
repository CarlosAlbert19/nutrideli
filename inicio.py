from flask import Flask
app = Flask(__name__)


@app.route("/")
@app.route("/inicio")
def inicio():
    return "<h1>Home Page</h1>"

@app.route("/acerca_de")
def acerca_de():
    return "<h1>Acerca de nosotros</h1>"



if __name__ == '__main__':
        app.run(debug=True)