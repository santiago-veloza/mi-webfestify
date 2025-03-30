from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, DateField, TextAreaField
from wtforms.validators import DataRequired, Email, Length


class MiFormulario(FlaskForm):
    name = StringField('Nombre', validators=[DataRequired(), Length(max=64)])
    password = PasswordField('Password', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Registrar')
    

class EventoForm(FlaskForm):
    nombre = StringField('Nombre del Evento', validators=[DataRequired()])
    fecha = DateField('Fecha', format='%Y-%m-%d', validators=[DataRequired()])
    ubicacion = StringField('Ubicación', validators=[DataRequired()])
    descripcion = TextAreaField('Descripción', validators=[DataRequired()])
    submit = SubmitField('Agregar Evento')