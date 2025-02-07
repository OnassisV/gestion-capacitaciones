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

if __name__ == '__main__':
    app.run(debug=True)
