from flask import Flask, render_template, request, redirect, url_for
from festify.forms import MiFormulario


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
        return redirect(url_for('home'))
    return render_template('registro.html', title="Registro", form=form)

if __name__ == '__main__':
    app.run(debug=True)