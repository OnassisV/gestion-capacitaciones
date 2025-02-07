from flask import Flask, render_template, request, redirect, url_for, session
from config import get_db_connection

app = Flask(__name__)
app.secret_key = "clave_secreta"  # Cambiar por una clave segura

@app.route('/')
def login():
    return render_template('login.html')

@app.route('/auth', methods=['POST'])
def auth():
    usuario = request.form['usuario']
    password = request.form['password']

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM usuarios WHERE nombre_usuario = %s AND password = %s", (usuario, password))
    user = cursor.fetchone()
    cursor.close()
    connection.close()

    if user:
        session['usuario'] = user['nombre_usuario']
        session['rol'] = user['rol']
        return redirect(url_for('dashboard'))
    else:
        return render_template('login.html', error="Credenciales incorrectas")

@app.route('/dashboard')
def dashboard():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html', usuario=session['usuario'], rol=session['rol'])

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/capacitaciones')
def capacitaciones():
    if 'usuario' not in session:
        return redirect(url_for('login'))

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM capacitaciones")
    capacitaciones = cursor.fetchall()
    cursor.close()
    connection.close()

    return render_template('capacitaciones.html', capacitaciones=capacitaciones, rol=session['rol'])

@app.route('/capacitaciones/add', methods=['GET', 'POST'])
def add_capacitacion():
    if 'usuario' not in session or session['rol'] not in ['Especialista', 'Administrador']:
        return redirect(url_for('login'))

    if request.method == 'POST':
        codigo = request.form['codigo']
        nombre = request.form['nombre']
        tipo = request.form['tipo']
        fecha_inicio = request.form['fecha_inicio']
        fecha_fin = request.form['fecha_fin']
        modalidad = request.form['modalidad']

        connection = get_db_connection()
        cursor = connection.cursor()
        sql = "INSERT INTO capacitaciones (codigo, nombre, tipo, fecha_inicio, fecha_fin, modalidad) VALUES (%s, %s, %s, %s, %s, %s)"
        cursor.execute(sql, (codigo, nombre, tipo, fecha_inicio, fecha_fin, modalidad))
        connection.commit()
        cursor.close()
        connection.close()

        return redirect(url_for('capacitaciones'))

    return render_template('add_capacitacion.html', rol=session['rol'])

@app.route('/actividades')
def actividades():
    if 'usuario' not in session:
        return redirect(url_for('login'))

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT a.id_actividad, a.nombre_actividad, a.fecha, a.hora, c.nombre AS capacitacion FROM actividades a JOIN capacitaciones c ON a.id_capacitacion = c.id_capacitacion")
    actividades = cursor.fetchall()
    cursor.close()
    connection.close()

    return render_template('actividades.html', actividades=actividades, rol=session['rol'])

@app.route('/actividades/add', methods=['GET', 'POST'])
def add_actividad():
    if 'usuario' not in session or session['rol'] not in ['Especialista', 'Administrador']:
        return redirect(url_for('login'))

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT id_capacitacion, nombre FROM capacitaciones")
    capacitaciones = cursor.fetchall()
    cursor.close()
    connection.close()

    if request.method == 'POST':
        id_capacitacion = request.form['id_capacitacion']
        nombre_actividad = request.form['nombre_actividad']
        fecha = request.form['fecha']
        hora = request.form['hora']
        tipo_evaluacion = request.form['tipo_evaluacion']
        escala = request.form['escala']

        connection = get_db_connection()
        cursor = connection.cursor()
        sql = "INSERT INTO actividades (id_capacitacion, nombre_actividad, fecha, hora, tipo_evaluacion, escala) VALUES (%s, %s, %s, %s, %s, %s)"
        cursor.execute(sql, (id_capacitacion, nombre_actividad, fecha, hora, tipo_evaluacion, escala))
        connection.commit()
        cursor.close()
        connection.close()

        return redirect(url_for('actividades'))

    return render_template('add_actividad.html', capacitaciones=capacitaciones, rol=session['rol'])


if __name__ == '__main__':
    app.run(debug=True)
