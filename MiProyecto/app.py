from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_mysqldb import MySQL
import MySQLdb

app = Flask(__name__)
app.secret_key = 'mysecretkey'

# Configuración de MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '12345678'
app.config['MYSQL_DB'] = 'ProyectoIntegrador'

mysql = MySQL(app)

# RUTA HOME
@app.route('/')
def home():
    return render_template('index.html')

# LOGIN
@app.route('/login', methods=['GET', 'POST'])
def login():
    errores = {}
    if request.method == 'POST':
        correo = request.form.get('correo', '').strip()
        contrasena = request.form.get('contrasena', '').strip()

        if not correo:
            errores['correo'] = 'El correo es obligatorio'
        if not contrasena:
            errores['contrasena'] = 'La contraseña es obligatoria'

        if not errores:
            try:
                cursor = mysql.connection.cursor()
                cursor.execute('SELECT * FROM Tutores WHERE Correo = %s AND Contrasena = %s', (correo, contrasena))
                tutor = cursor.fetchone()
                cursor.close()
                if tutor:
                    session['tutor_id'] = tutor[0]
                    flash('Inicio de sesión exitoso')
                    return redirect(url_for('home'))
                else:
                    errores['login'] = 'Correo o contraseña incorrectos'
            except Exception as e:
                print(str(e))
                flash('Error al iniciar sesión')

    return render_template('index.html', errores=errores)

# REGISTRO TUTOR
@app.route('/registro_tutor', methods=['GET', 'POST'])
def registro_tutor():
    errores = {}
    if request.method == 'POST':
        nombre = request.form.get('nombre', '').strip()
        apellido = request.form.get('apellido', '').strip()
        usuario = request.form.get('usuario', '').strip()
        correo = request.form.get('correo', '').strip()
        contrasena = request.form.get('contrasena', '').strip()
        fecha = request.form.get('fecha', '').strip()

        if not nombre:
            errores['nombre'] = 'Nombre obligatorio'
        if not apellido:
            errores['apellido'] = 'Apellido obligatorio'
        if not usuario:
            errores['usuario'] = 'Usuario obligatorio'
        if not correo:
            errores['correo'] = 'Correo obligatorio'
        if not contrasena or len(contrasena) < 4:
            errores['contrasena'] = 'Contraseña mínima de 4 caracteres'
        if not fecha:
            errores['fecha'] = 'Fecha de nacimiento obligatoria'

        if not errores:
            try:
                cursor = mysql.connection.cursor()
                cursor.execute('''
                    INSERT INTO Tutores (Nombre, Apellido, Usuario, Correo, Contrasena, FechaNacimiento)
                    VALUES (%s, %s, %s, %s, %s, %s)
                ''', (nombre, apellido, usuario, correo, contrasena, fecha))
                mysql.connection.commit()
                tutor_id = cursor.lastrowid
                cursor.close()
                session['tutor_id'] = tutor_id
                flash('Tutor registrado correctamente')
                return redirect(url_for('registrar_ninos'))
            except Exception as e:
                mysql.connection.rollback()
                print(str(e))
                flash('Error al registrar tutor: ' + str(e))

    return render_template('RegistroTutor.html', errores=errores)

# REGISTRO NIÑO
@app.route('/registrar_nino', methods=['GET', 'POST'])
def registrar_nino():
    errores = {}

    tutor_id = session.get('tutor_id')
    if not tutor_id:
        flash('Debes iniciar sesión o registrar un tutor primero.')
        return redirect(url_for('registro_tutor'))

    if request.method == 'POST':
        nombre = request.form.get('nombre_nino', '').strip()
        apellido = request.form.get('apellido_nino', '').strip()
        fecha_nacimiento = request.form.get('fecha_nacimiento', '').strip()

        if not nombre or any(char.isdigit() for char in nombre):
            errores['nombre_nino'] = 'Nombre obligatorio y sin números.'
        if not apellido or any(char.isdigit() for char in apellido):
            errores['apellido_nino'] = 'Apellido obligatorio y sin números.'
        if not fecha_nacimiento:
            errores['fecha_nacimiento'] = 'Fecha de nacimiento obligatoria.'

        if not errores:
            try:
                cursor = mysql.connection.cursor()
                cursor.execute('''
                    INSERT INTO Ninos (Tutor_id, Nombre, Apellido, FechaNacimiento)
                    VALUES (%s, %s, %s, %s)
                ''', (tutor_id, nombre, apellido, fecha_nacimiento))
                mysql.connection.commit()
                cursor.close()
                flash('Niño registrado exitosamente.')
                return redirect(url_for('home'))
            except Exception as e:
                mysql.connection.rollback()
                flash(f'Error al registrar al niño: {str(e)}')

    return render_template('registro_nino.html', errores=errores)

# Inicia la aplicación
if __name__ == '__main__':
    app.run(port=3000, debug=True)