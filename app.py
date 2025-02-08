import bcrypt
from flask import Flask, render_template, request, redirect, url_for, session
from config import get_db_connection

app = Flask(__name__)
app.secret_key = "clave_secreta"  # Cambiar por una clave segura

@app.route('/')
def login():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT correo FROM usuarios")
    correos = cursor.fetchall()
    cursor.close()
    connection.close()
    return render_template('login.html', correos=correos)


@app.route('/auth', methods=['POST'])
def auth():
    correo = request.form['correo']
    password = request.form['password']

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM usuarios WHERE correo = %s", (correo,))
    user = cursor.fetchone()
    cursor.close()
    connection.close()

    if user and bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
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
    connection = get_db_connection()

    if request.method == 'POST':
        # Datos del formulario
        codigo_capacitacion = request.form['codigo_capacitacion']
        nombre_capacitacion = request.form['nombre_capacitacion']
        id_unidad_organica = request.form['id_unidad_organica']

        # Guardar en la base de datos
        cursor = connection.cursor()
        sql = """
            INSERT INTO capacitaciones (codigo_capacitacion, nombre_capacitacion, id_unidad_organica, siglas_unidad_organica)
            VALUES (%s, %s, %s, 
                (SELECT siglas FROM unidades_organicas WHERE id_unidad_organica = %s))
        """
        cursor.execute(sql, (codigo_capacitacion, nombre_capacitacion, id_unidad_organica, id_unidad_organica))
        connection.commit()
        cursor.close()
        connection.close()

        return redirect(url_for('capacitaciones'))

    # Obtener las unidades orgánicas
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT id_unidad_organica, nombre_unidad_organica, siglas FROM unidades_organicas")
    unidades = cursor.fetchall()
    cursor.close()
    connection.close()

    return render_template('add_capacitacion.html', unidades=unidades)


@app.route('/actividades')
def actividades():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("""
        SELECT a.id_actividad, a.nombre_actividad, a.fecha_inicio, a.fecha_fin, c.nombre AS capacitacion,
               a.tipo_evaluacion, a.escala
        FROM actividades a
        JOIN capacitaciones c ON a.id_capacitacion = c.id_capacitacion
    """)
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
        fecha_inicio = request.form['fecha_inicio']
        fecha_fin = request.form['fecha_fin']
        tipo_evaluacion = request.form['tipo_evaluacion']
        escala = request.form['escala']

        connection = get_db_connection()
        cursor = connection.cursor()
        sql = """
            INSERT INTO actividades (id_capacitacion, nombre_actividad, fecha_inicio, fecha_fin, tipo_evaluacion, escala)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        cursor.execute(sql, (id_capacitacion, nombre_actividad, fecha_inicio, fecha_fin, tipo_evaluacion, escala))
        connection.commit()
        cursor.close()
        connection.close()

        return redirect(url_for('actividades'))

    return render_template('add_actividad.html', capacitaciones=capacitaciones, rol=session['rol'])


if __name__ == '__main__':
    app.run(debug=True)
