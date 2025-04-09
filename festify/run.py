
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
import mariadb
from festify.forms import MiFormulario, EventoForm, LoginForm , RegistroClienteForm
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mail import Mail, Message
from flask import Flask

app = Flask(__name__)
app.config['SECRET_KEY'] = '7110c8ae51a4b5af97be6534caef90e4bb9bdcb3380af008f90b23a5d1616bf319bc298105da20fe'

# Configuración de la base de datos

class DBConnection:
    _instance = None
    _conn = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DBConnection, cls).__new__(cls)
            cls._connect()
        return cls._instance

    @classmethod
    def _connect(cls):
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
            cls._conn = None

    def get_connection(self):
        try:
            self._conn.ping()  # Verifica si sigue activa
        except mariadb.Error:
            print("Conexión cerrada. Reconectando...")
            self._connect()
        return self._conn

#--------------------Configuración de correo----------------------------------
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'festifysoporte@gmail.com'
app.config['MAIL_PASSWORD'] = 'vipw fzjs jxwe txru'  # Contraseña de aplicación
app.config['MAIL_DEFAULT_SENDER'] = 'festifysoporte@gmail.com'


mail = Mail(app)

#--------------------rutas empresarios----------------------------------
@app.route('/')
def home():
    return render_template('index.html', title="Inicio")

@app.route('/about')
def about():
    return render_template('about.html', title="Acerca de nosotros")



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

                # Enviar correo de bienvenida
                enviar_correo(
                    destinatario=email,
                    asunto='🎉 ¡Bienvenido a Festify!',
                    cuerpo=f"Hola {nombre},\n\nGracias por registrarte en Festify.\n¡Explora eventos y disfruta la música!\n\nEl equipo de Festify."
                )

                flash('Registro exitoso. Se ha enviado un correo de bienvenida.', 'success')
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
        tiquetes = form.tiquetes.data
        precio = form.precio.data

        conn = DBConnection().get_connection()
        if conn:
            try:
                cursor = conn.cursor()
                query = """
                    INSERT INTO festify (nombre, fecha, hora, ubicacion, descripcion, tiquetes, precio)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """
                cursor.execute(query, (nombre, fecha, hora, ubicacion, descripcion, tiquetes, precio))
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


#-------------------rutas cliente----------------------------------------------------

@app.route('/cliente/login', methods=['GET', 'POST'])
def login_cliente():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        conn = DBConnection().get_connection()
        if conn:
            cursor = conn.cursor()
            query = "SELECT cliente_id, clave_cliente FROM clientesb WHERE correo_cliente = ?"
            cursor.execute(query, (email,))
            cliente = cursor.fetchone()
            cursor.close()
            conn.close()

            if cliente and check_password_hash(cliente[1], password):
                session['cliente_id'] = cliente[0]  # 👈 Guardar ID en sesión
                flash('Inicio de sesión de cliente exitoso.', 'success')
                return redirect(url_for('eventos_cliente'))
            else:
                flash('Correo o contraseña incorrectos (cliente)', 'danger')

    return render_template('cliente/logincliente.html', title="Login Cliente", form=form)

@app.route('/cliente/registro', methods=['GET', 'POST'])
def registro_cliente():
    form = RegistroClienteForm()
    if form.validate_on_submit():
        nombre = form.nombre.data
        correo = form.correo.data
        password = form.password.data

        conn = DBConnection().get_connection()
        if conn:
            cursor = conn.cursor()

            # Verificar si el correo ya existe
            cursor.execute("SELECT * FROM clientesb WHERE correo_cliente = ?", (correo,))
            existente = cursor.fetchone()
            if existente:
                flash('El correo ya está registrado como cliente.', 'warning')
                cursor.close()
                conn.close()
                return redirect(url_for('registro_cliente'))

            # Insertar nuevo cliente
            hashed_password = generate_password_hash(password)
            cursor.execute(
                "INSERT INTO clientesb (nombre, correo_cliente, clave_cliente) VALUES (?, ?, ?)",
                (nombre, correo, hashed_password)
            )
            conn.commit()
            cursor.close()
            conn.close()

            # Enviar correo de bienvenida al cliente
            enviar_correo(
                destinatario=correo,
                asunto='🎟️ ¡Bienvenido a Festify, Cliente!',
                cuerpo=f"Hola {nombre},\n\nGracias por registrarte como cliente en Festify.\nYa puedes iniciar sesión y comprar tus boletas favoritas.\n\n¡Nos alegra tenerte con nosotros!\n\n- Equipo Festify"
            )

            flash('Cliente registrado exitosamente. Revisa tu correo. Ahora puedes iniciar sesión.', 'success')
            return redirect(url_for('login_cliente'))

    return render_template('cliente/registrocliente.html', form=form, title="Registro Cliente")

@app.route('/cliente/eventos')
def eventos_cliente():
    if 'cliente_id' not in session:
        flash('Debes iniciar sesión como cliente para ver los eventos.', 'warning')
        return redirect(url_for('login_cliente'))  # redirige a login si no hay sesión

    conn = DBConnection().get_connection()
    eventos = []
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM festify")
        eventos = cursor.fetchall()

        cursor.close()
        conn.close()

    return render_template('cliente/eventosclientes.html', eventos=eventos, title="Eventos Disponibles")

@app.route('/comprar/<int:evento_id>', methods=['GET', 'POST'])
def comprar_tiquetes(evento_id):
    db = DBConnection().get_connection()
    cursor = db.cursor()

    cursor.execute("SELECT * FROM festify WHERE id = ?", (evento_id,))
    resultado = cursor.fetchone()

    if not resultado:
        flash('Evento no encontrado.', 'error')
        return redirect(url_for('eventos_cliente'))

    # Convertir a diccionario manualmente
    columnas = [col[0] for col in cursor.description]
    evento = dict(zip(columnas, resultado))

    if request.method == 'POST':
        cantidad = int(request.form['cantidad'])

        if cantidad <= 0:
            flash('La cantidad debe ser mayor a 0.', 'error')
        elif cantidad > evento['tiquetes']:
            flash('No hay suficientes tiquetes disponibles.', 'error')
        else:
            nuevos_tiquetes = evento['tiquetes'] - cantidad
            cursor.execute("UPDATE festify SET tiquetes = ? WHERE id = ?", (nuevos_tiquetes, evento_id))
            db.commit()
            flash(f'Compra realizada con éxito. Compraste {cantidad} tiquete(s).', 'success')
            return redirect(url_for('eventos_cliente'))

    return render_template('cliente/comprar.html', evento=evento, title="Comprar Tiquetes")

#------------------- funciones para gmail----------------------------------------------------
def enviar_correo(destinatario, asunto, cuerpo):
    try:
        msg = Message(asunto, recipients=[destinatario])
        msg.body = cuerpo
        mail.send(msg)
    except Exception as e:
        print(f"Error al enviar correo: {e}")



if __name__ == '__main__':
    app.run(debug=True)
