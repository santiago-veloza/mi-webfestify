from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
import mariadb
from datetime import datetime, timedelta
from .forms import MiFormulario, EventoForm, LoginForm, RegistroClienteForm
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mail import Mail, Message
from functools import wraps

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
            self._conn.ping()
        except mariadb.Error:
            print("Conexión cerrada. Reconectando...")
            self._connect()
        return self._conn

# Configuración de correo
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'festifysoporte@gmail.com'
app.config['MAIL_PASSWORD'] = 'vipw fzjs jxwe txru'  # Contraseña de aplicación
app.config['MAIL_DEFAULT_SENDER'] = 'festifysoporte@gmail.com'

mail = Mail(app)

# Función para enviar correo
def enviar_correo(destinatario, asunto, cuerpo):
    try:
        msg = Message(asunto, recipients=[destinatario])
        msg.body = cuerpo
        mail.send(msg)
    except Exception as e:
        print(f"Error al enviar correo: {e}")



# Decoradores para verificar si el usuario está logueado como microempresario o cliente

def login_required_cliente(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'cliente_id' not in session:
            flash('Debes iniciar sesión como cliente para acceder.', 'warning')
            return redirect(url_for('login_cliente'))
        return f(*args, **kwargs)
    return decorated_function

def login_required_usuario(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario_id' not in session:
            flash('Debes iniciar sesión para acceder a esta página.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function



# Rutas empresarios
@app.route('/')
def home():
    conn = DBConnection().get_connection()
    eventos = []
    evento_reciente = None
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM festify ORDER BY fecha DESC")
        eventos = cursor.fetchall()

        # Buscar evento reciente (últimas 24 horas)
        ahora = datetime.now()
        for evento in eventos:
            if 'fecha_creacion' in evento and evento['fecha_creacion']:
                if evento['fecha_creacion'] >= ahora - timedelta(hours=24):
                    evento_reciente = evento
                    break

        cursor.close()
    
    return render_template('index.html', title="Inicio", eventos=eventos, evento_reciente=evento_reciente)
@app.route('/about')
def about():
    return render_template('about.html', title="Acerca de nosotros")

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    form = MiFormulario()
    if form.validate_on_submit():
        print("Formulario validado correctamente.")

        nombre = form.name.data
        email = form.email.data
        password = form.password.data

        conn = DBConnection().get_connection()
        if conn:
            try:
                cursor = conn.cursor()

                # Verificar si ya existe el correo
                cursor.execute("SELECT id FROM usuarios WHERE email = %s", (email,))
                existente = cursor.fetchone()
                if existente:
                    flash('Este correo ya está registrado. Intenta con otro.', 'warning')
                    return render_template('registro.html', form=form)

                # Insertar usuario
                query = "INSERT INTO usuarios (nombre, email, password) VALUES (%s, %s, %s)"
                cursor.execute(query, (nombre, email, generate_password_hash(password)))
                conn.commit()

                print("Usuario registrado en base de datos.")

                # Intentar enviar correo
                try:
                    enviar_correo(
                        destinatario=email,
                        asunto='🎉 ¡Bienvenido a Festify!',
                        cuerpo=f"Hola {nombre},\n\nGracias por registrarte en Festify.\n¡Explora eventos y disfruta la música!\n\nEl equipo de Festify."
                    )
                    print("Correo enviado correctamente.")
                except Exception as e:
                    print(f"Error enviando correo: {e}")
                    flash('Usuario registrado, pero no se pudo enviar el correo.', 'warning')

                flash('Registro exitoso. Se ha enviado un correo de bienvenida.', 'success')
                return redirect(url_for('login'))

            except Exception as e:
                flash(f'Error al registrar: {e}', 'danger')
                print(f"Error al registrar usuario: {e}")
            finally:
                cursor.close()
    else:
        if request.method == 'POST':
            print("Formulario inválido. Errores:", form.errors)

    return render_template('registro.html', form=form)
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        conn = DBConnection().get_connection()
        if conn:
            cursor = conn.cursor()
            query = "SELECT id, password FROM usuarios WHERE email = %s"
            cursor.execute(query, (email,))
            user = cursor.fetchone()
            cursor.close()

            if user and check_password_hash(user[1], password):
                session['usuario_id'] = user[0]  # Guarda id usuario en sesión
                flash('Inicio de sesión exitoso.', 'success')
                return redirect(url_for('agregarevento'))  # O a donde quieras enviar
            else:
                flash('Correo o contraseña incorrectos', 'danger')
                return redirect(url_for('login'))
    return render_template('login.html', title="Login", form=form)

@app.route('/agregarevento', methods=['GET', 'POST'])
@login_required_usuario
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

        # 🔥 Aquí capturas el usuario actual desde la sesión
        usuario_id = session.get('usuario_id')
        if not usuario_id:
            flash('Debes iniciar sesión para agregar un evento.', 'warning')
            return redirect(url_for('login'))

        conn = DBConnection().get_connection()
        if conn:
            try:
                cursor = conn.cursor()
                # 🔥 Agrega el campo usuario_id en la consulta
                query = """
                    INSERT INTO festify (nombre, fecha, hora, ubicacion, descripcion, tiquetes, precio, usuario_id)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """
                cursor.execute(query, (nombre, fecha, hora, ubicacion, descripcion, tiquetes, precio, usuario_id))
                conn.commit()
                flash('Evento agregado correctamente.', 'success')
                return redirect(url_for('home'))
            except mariadb.Error as e:
                flash(f'Error al guardar el evento: {e}', 'danger')
            finally:
                cursor.close()
    return render_template('agregarevento.html', title="Agregar Evento", form=form)

@app.route('/info')
@login_required_usuario
def info_eventos():
    print("ID en sesión:", session.get('usuario_id'))
    if 'usuario_id' not in session:
        return redirect(url_for('login'))  # Redirige si el usuario no está logueado

    usuario_id = session['usuario_id']
    conn = DBConnection().get_connection()
    eventos = []
    total_boletos = 0
    total_ingresos = 0
    eventos_disponibles = []

    if conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, nombre, fecha, hora, ubicacion, descripcion, tiquetes, precio
            FROM festify
            WHERE usuario_id = %s
        """, (usuario_id,))
        resultados = cursor.fetchall()
        columnas = [col[0] for col in cursor.description]

        for fila in resultados:
            evento = dict(zip(columnas, fila))

            # Obtener tiquetes vendidos desde la tabla 'compras'
            cursor.execute("SELECT SUM(cantidad) FROM compras WHERE evento_id = %s", (evento['id'],))
            vendidos = cursor.fetchone()[0] or 0

            evento['tiquetes_vendidos'] = vendidos
            evento['tiquetes_disponibles'] = evento['tiquetes'] - vendidos
            evento['total_recaudado'] = float(vendidos) * float(evento['precio'])

            total_boletos += vendidos
            total_ingresos += evento['total_recaudado']

            if evento['tiquetes_disponibles'] > 0:
                eventos_disponibles.append(evento)

            eventos.append(evento)

        cursor.close()

    return render_template(
        'info_eventos.html',
        eventos=eventos,
        total_boletos=total_boletos,
        total_ingresos=total_ingresos,
        eventos_disponibles=eventos_disponibles
    )






# Rutas para cliente

@app.route('/cliente/login', methods=['GET', 'POST'])
def login_cliente():
    form = LoginForm()

    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        conn = DBConnection().get_connection()
        if not conn:
            flash('Error al conectar con la base de datos.', 'danger')
            return render_template('cliente/logincliente.html', title="Login Cliente", form=form)

        cursor = conn.cursor()
        try:
            query = "SELECT cliente_id, clave_cliente FROM clientesb WHERE correo_cliente = %s"
            cursor.execute(query, (email,))
            cliente = cursor.fetchone()
        except Exception as e:
            flash('Error al consultar la base de datos.', 'danger')
            cliente = None
        finally:
            cursor.close()

        if cliente and check_password_hash(cliente[1], password):
            session.clear()  # Limpiar cualquier sesión previa
            session['cliente_id'] = cliente[0]  # Guardar cliente_id en sesión
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

            cursor.execute("SELECT * FROM clientesb WHERE correo_cliente = %s", (correo,))
            existente = cursor.fetchone()
            if existente:
                flash('El correo ya está registrado como cliente.', 'warning')
                cursor.close()
                return redirect(url_for('registro_cliente'))

            hashed_password = generate_password_hash(password)
            cursor.execute(
                "INSERT INTO clientesb (nombre, correo_cliente, clave_cliente) VALUES (%s, %s, %s)",
                (nombre, correo, hashed_password)
            )
            conn.commit()
            cursor.close()

            enviar_correo(
                destinatario=correo,
                asunto='🎟️ ¡Bienvenido a Festify, Cliente!',
                cuerpo=f"Hola {nombre},\n\nGracias por registrarte como cliente en Festify.\nYa puedes iniciar sesión y comprar tus boletas favoritas.\n\n¡Nos alegra tenerte con nosotros!\n\n- Equipo Festify"
            )

            flash('Cliente registrado exitosamente. Revisa tu correo. Ahora puedes iniciar sesión.', 'success')
            return redirect(url_for('login_cliente'))

    return render_template('cliente/registrocliente.html', form=form, title="Registro Cliente")

@app.route('/cliente/eventos')
@login_required_cliente
def eventos_cliente():
    if 'cliente_id' not in session:
        flash('Debes iniciar sesión como cliente para ver los eventos.', 'warning')
        return redirect(url_for('login_cliente'))

    conn = DBConnection().get_connection()
    eventos = []

    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, nombre, fecha, hora, ubicacion, descripcion, tiquetes, precio FROM festify")
        resultados = cursor.fetchall()
        columnas = [col[0] for col in cursor.description]

        for fila in resultados:
            evento = dict(zip(columnas, fila))
            eventos.append(evento)

        cursor.close()
        

    return render_template('cliente/eventosclientes.html', eventos=eventos, title="Eventos Disponibles")


@app.route('/comprar/<int:evento_id>', methods=['GET', 'POST'])
def comprar_tiquetes(evento_id):
    if 'cliente_id' not in session:
        flash('Debes iniciar sesión como cliente para comprar.', 'warning')
        return redirect(url_for('login_cliente'))

    db = DBConnection().get_connection()
    cursor = db.cursor()

    cursor.execute("SELECT * FROM festify WHERE id = ?", (evento_id,))
    resultado = cursor.fetchone()

    if not resultado:
        flash('Evento no encontrado.', 'error')
        return redirect(url_for('eventos_cliente'))

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

            # Registrar la compra en la tabla 'compras'
            cliente_id = session['cliente_id']
            cursor.execute(
                "INSERT INTO compras (cliente_id, evento_id, cantidad) VALUES (%s, %s, %s)",
                (cliente_id, evento_id, cantidad)
            )
            db.commit()

            flash(f'Compra realizada con éxito. Compraste {cantidad} tiquete(s).', 'success')
            return redirect(url_for('eventos_cliente'))

    return render_template('cliente/comprar.html', evento=evento, title="Comprar Tiquetes")

# Run
if __name__ == '__main__':


    app.run(debug=True)
