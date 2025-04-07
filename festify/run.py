#run.py

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import mariadb
from festify.forms import MiFormulario, EventoForm, LoginForm  
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)
app.config['SECRET_KEY'] = '7110c8ae51a4b5af97be6534caef90e4bb9bdcb3380af008f90b23a5d1616bf319bc298105da20fe'

# Configuración de la base de datos
class DBConnection:
    _instance = None
    _conn = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DBConnection, cls).__new__(cls)
            try:
                cls._conn = mariadb.connect(
                    host='localhost',
                    user='root',
                    password='ucc2025',
                    database='festify',
                    port=3306
                )
            except mariadb.Error as e:
                print(f"Error de conexión: {e}")
        return cls._instance

    def get_connection(self):
        return self._conn


@app.route('/')
def home():
    return render_template('index.html', title="Inicio")

@app.route('/about')
def about():
    return render_template('about.html', title="Acerca de nosotros")

@app.route('/registro', methods=['GET', 'POST'])
@app.route('/registro', methods=['GET', 'POST'])
def registro():
    form = MiFormulario()
    if request.method == 'POST' and form.validate_on_submit():
        nombre = form.name.data
        email = form.email.data
        password = form.password.data

        conn = DBConnection().get_connection()
        if conn:
            try:
                cursor = conn.cursor()
                
                # Verificar si el correo ya existe
                cursor.execute("SELECT id FROM usuarios WHERE email = ?", (email,))
                existente = cursor.fetchone()
                if existente:
                    flash('Este correo ya está registrado. Intenta con otro.', 'warning')
                    return render_template('registro.html', form=form)

                # Insertar nuevo usuario
                query = "INSERT INTO usuarios (nombre, email, password) VALUES (?, ?, ?)"
                cursor.execute(query, (nombre, email, generate_password_hash(password)))
                conn.commit()
                flash('Registro exitoso. Ahora puedes iniciar sesión.', 'success')
                return redirect(url_for('login'))
            
            except Exception as e:
                flash(f'Error al registrar: {e}', 'danger')
            finally:
                cursor.close()
    return render_template('registro.html', form=form)


@app.route('/agregarevento', methods=['GET', 'POST'])
def agregarevento():
    form = EventoForm()  
    if form.validate_on_submit():
        nombre = form.nombre.data
        fecha = form.fecha.data
        hora = form.hora.data
        ubicacion = form.ubicacion.data
        descripcion = form.descripcion.data

        # Insertar datos en la base de datos
        conn = DBConnection().get_connection()
        if conn:
            try:
                cursor = conn.cursor()
                query = "INSERT INTO festify (nombre, fecha, hora, ubicacion, descripcion) VALUES (?, ?, ?, ?, ?)"
                cursor.execute(query, (nombre, fecha, hora, ubicacion, descripcion))
                conn.commit()
                cursor.close()
                conn.close()
                flash('Evento agregado correctamente.', 'success')
                return redirect(url_for('home'))  
            except mariadb.Error as e:
                flash(f'Error al guardar el evento: {e}', 'danger')

    return render_template('agregarevento.html', title="Agregar Evento", form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        conn = DBConnection().get_connection()
        if conn:
            cursor = conn.cursor()
            query = "SELECT id, password FROM usuarios WHERE email = ?"
            cursor.execute(query, (email,))
            print(f"Query executed: {query}, with email: {email}")
            user = cursor.fetchone()
            print(f"User fetched: {user}")
            cursor.close()
            conn.close()
            if user is None:
                flash('Correo o contraseña incorrectos', 'danger')
                return redirect(url_for('login'))
            if user and check_password_hash(user[1], password):
                flash('Inicio de sesión exitoso.', 'success')
                return redirect(url_for('agregarevento'))
            else:
                flash('Correo o contraseña incorrectos', 'danger')
    return render_template('login.html', title="Login", form=form)

if __name__ == '__main__':
    app.run(debug=True)
