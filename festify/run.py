from flask import Flask, render_template, request, redirect, url_for, flash
from festify.forms import MiFormulario, EventoForm, LoginForm  


app = Flask(__name__)
app.config['SECRET_KEY'] = '7110c8ae51a4b5af97be6534caef90e4bb9bdcb3380af008f90b23a5d1616bf319bc298105da20fe'


@app.route('/')
def home():
    return render_template('index.html', title="Inicio")

@app.route('/about')
def about():
    return render_template('about.html', title="Acerca de nosotros")

@app.route('/registro', methods=['GET', 'POST'])
def registro ():
    form = MiFormulario()
    if form.validate_on_submit():
        nombre = form.name.data
        email = form.email.data
        password = form.password.data
        return redirect(url_for('login')) 
    return render_template('registro.html', title="Registro", form=form)

@app.route('/agregarevento', methods=['GET', 'POST'])
def agregarevento():
    form = EventoForm()  
    if form.validate_on_submit():
        nombre = form.nombre.data
        fecha = form.fecha.data
        hora = form.hora.data
        ubicacion = form.ubicacion.data
        descripcion = form.descripcion.data
        return redirect(url_for('home'))  
    return render_template('agregarevento.html', title="Agregar Evento", form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        # Aquí deberías validar el usuario en la base de datos
        if email == "admin@example.com" and password == "1234":  # Ejemplo
            return redirect(url_for('agregarevento'))  
        else:
            flash('Correo o contraseña incorrectos', 'danger')
    return render_template('login.html', title="Login", form=form)


if __name__ == '__main__':
    app.run(debug=True)