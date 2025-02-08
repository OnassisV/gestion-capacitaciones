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
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    # Consulta completa para obtener todas las columnas
    cursor.execute("""
        SELECT 
            c.id_capacitacion, 
            c.codigo_capacitacion, 
            c.nombre_capacitacion, 
            c.tipo_capacitacion, 
            c.modalidad_capacitacion, 
            c.condicion, 
            c.capacitacion_replica, 
            c.capacitacion_acompanamiento, 
            c.capacitacion_sesiones_sincronicas, 
            c.tipo_proceso_fortalecido, 
            c.recursos_virtuales, 
            c.monitores, 
            c.retroalimentacion, 
            c.proceso_principal_fortalecido, 
            c.competencia_especifica, 
            c.capacitacion_aplicacion_inmediata, 
            c.sub_proceso_fortalecido, 
            c.rubro_tematico, 
            u.nombre_unidad_organica AS unidad_organica, 
            u.siglas AS siglas_unidad_organica, 
            c.oficio_requerimiento, 
            c.publico_objetivo, 
            c.etapa_desarrollo, 
            c.objetivo_capacitacion, 
            c.genera_evidencia_comparativa, 
            c.nivel_capacidad_fortalecida, 
            c.evaluacion_eficacia_grupo_control, 
            c.tipo_inscripcion, 
            c.documento_convocatoria, 
            c.horas_cronologicas, 
            c.convocatoria_fecha_inicio, 
            c.implementacion_fecha_inicio, 
            c.implementacion_fecha_fin, 
            c.oficio_dre_ugel_listado, 
            c.aplica_encuesta_satisfaccion, 
            c.incluido_reporte_cneb, 
            c.evidencia_resultado_impacto, 
            c.oficio_dre_ugel_situacion, 
            c.carpeta_formatos_enlace, 
            c.informe_cierre
        FROM capacitaciones c
        JOIN unidades_organicas u ON c.id_unidad_organica = u.id_unidad_organica
    """)
    
    capacitaciones = cursor.fetchall()
    cursor.close()
    connection.close()
    
    return render_template('capacitaciones.html', capacitaciones=capacitaciones)


@app.route('/capacitaciones/add', methods=['GET', 'POST'])
def add_capacitacion():
    connection = get_db_connection()

    if request.method == 'POST':
        # Recibir datos del formulario
        codigo_capacitacion = request.form['codigo_capacitacion']
        nombre_capacitacion = request.form['nombre_capacitacion']
        tipo_capacitacion = request.form['tipo_capacitacion']
        modalidad_capacitacion = request.form['modalidad_capacitacion']
        condicion = request.form['condicion']
        capacitacion_replica = request.form['capacitacion_replica']
        capacitacion_acompanamiento = request.form['capacitacion_acompanamiento']
        capacitacion_sesiones_sincronicas = request.form['capacitacion_sesiones_sincronicas']
        tipo_proceso_fortalecido = request.form['tipo_proceso_fortalecido']
        proceso_principal_fortalecido = request.form['proceso_principal_fortalecido']
        id_unidad_organica = request.form['id_unidad_organica']
        horas_cronologicas = request.form['horas_cronologicas']
        convocatoria_fecha_inicio = request.form['convocatoria_fecha_inicio']
        implementacion_fecha_inicio = request.form['implementacion_fecha_inicio']
        implementacion_fecha_fin = request.form['implementacion_fecha_fin']
        oficio_requerimiento = request.form['oficio_requerimiento']
        carpeta_formatos_enlace = request.form['carpeta_formatos_enlace']
        informe_cierre = request.form['informe_cierre']

        # Guardar en la base de datos
        cursor = connection.cursor()
        sql = """
            INSERT INTO capacitaciones (codigo_capacitacion, nombre_capacitacion, tipo_capacitacion, modalidad_capacitacion,
            condicion, capacitacion_replica, capacitacion_acompanamiento, capacitacion_sesiones_sincronicas, tipo_proceso_fortalecido,
            proceso_principal_fortalecido, id_unidad_organica, horas_cronologicas, convocatoria_fecha_inicio, implementacion_fecha_inicio,
            implementacion_fecha_fin, oficio_requerimiento, carpeta_formatos_enlace, informe_cierre)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(sql, (
            codigo_capacitacion, nombre_capacitacion, tipo_capacitacion, modalidad_capacitacion,
            condicion, capacitacion_replica, capacitacion_acompanamiento, capacitacion_sesiones_sincronicas,
            tipo_proceso_fortalecido, proceso_principal_fortalecido, id_unidad_organica, horas_cronologicas,
            convocatoria_fecha_inicio, implementacion_fecha_inicio, implementacion_fecha_fin,
            oficio_requerimiento, carpeta_formatos_enlace, informe_cierre
        ))
        connection.commit()
        cursor.close()
        connection.close()

        return redirect(url_for('capacitaciones'))

    # Obtener unidades orgánicas
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
