from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import InputRequired, DataRequired, Length, Email, EqualTo, ValidationError
from nutrideli_web.models import User

class Registro(FlaskForm):
    username = StringField('Nombre de usuario', validators=[DataRequired(), Length(min=2, max=25)])
    email = StringField('Correo', validators=[DataRequired(), Email()])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    confirm_password = PasswordField('Confirmar contraseña', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Registrarse')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Este nombre de usuario ya se encuentra en uso. Por favor, ingrese uno diferente.')
        
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Ese correo ya se encuentra en uso. Por favor, ingrese uno diferente.')

class Iniciar_sesion(FlaskForm):
    email = StringField('Correo', validators=[DataRequired(), Email()])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    remember = BooleanField('Recuérdame')
    submit = SubmitField('Iniciar sesión')


class Actualizar_informacion(FlaskForm):
    username = StringField('Nombre de usuario', validators=[DataRequired(), Length(min=2, max=25)])
    email = StringField('Correo', validators=[DataRequired(), Email()])
    picture = FileField('Actualizar foto de perfil', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Actualizar')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('Este nombre de usuario ya se encuentra en uso. Por favor, ingrese uno diferente.')
        
    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('Ese correo ya se encuentra en uso. Por favor, ingrese uno diferente.')