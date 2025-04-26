
from flask_wtf import FlaskForm
from wtforms.fields import StringField,EmailField, SubmitField, PasswordField, DateField, TextAreaField, TimeField
from wtforms.validators import DataRequired, Email, Length
from wtforms import IntegerField

class MiFormulario(FlaskForm):
    name = StringField('Nombre', validators=[DataRequired(), Length(max=64)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    email = EmailField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Registrar')
    

class EventoForm(FlaskForm):
    nombre = StringField('Nombre del Evento', validators=[DataRequired()])
    fecha = DateField('Fecha', format='%Y-%m-%d', validators=[DataRequired()])
    hora = TimeField('Hora', format='%H:%M', validators=[DataRequired()])
    tiquetes = IntegerField('Número de tiquetes', validators=[DataRequired()])
    precio = StringField('Precio', validators=[DataRequired()])
    ubicacion = StringField('Ubicación', validators=[DataRequired()])
    descripcion = TextAreaField('Descripción', validators=[DataRequired()])
    submit = SubmitField('Agregar Evento')
    
class LoginForm(FlaskForm):
    email = StringField('Correo Electrónico', validators=[DataRequired()])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    submit = SubmitField('Iniciar Sesión')
    
    
class RegistroClienteForm(FlaskForm):
    nombre = StringField('Nombre', validators=[DataRequired(), Length(max=100)])
    correo = EmailField('Correo Electrónico', validators=[DataRequired(), Email()])
    password = PasswordField('Contraseña', validators=[DataRequired(), Length(min=6)])
    submit = SubmitField('Registrarse')
