from flask_wtf import FlaskForm
from wtforms import IntegerField, SelectField, SubmitField
from wtforms.validators import DataRequired, NumberRange

class CrearDietaForm(FlaskForm):
    altura = IntegerField('Altura (cm)', validators=[DataRequired(), NumberRange(min=50, max=300, message="Por favor, ingresa una altura válida en cm.")])
    peso = IntegerField('Peso (kg)', validators=[DataRequired(), NumberRange(min=10, max=500, message="Por favor, ingresa un peso válido en kg.")])
    sexo = SelectField('Sexo', choices=[('masculino', 'Masculino'), ('femenino', 'Femenino')], validators=[DataRequired()])
    objetivo = SelectField('Objetivo', choices=[('bajar_peso', 'Bajar de peso'), ('formar_musculo', 'Formar músculo')], validators=[DataRequired()])
    submit = SubmitField('Crear Dieta')