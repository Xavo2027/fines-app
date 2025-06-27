
from flask import Flask, render_template, request, redirect, url_for, session, flash
import psycopg2
import bcrypt
from db_connect import get_connection

app = Flask(__name__)
app.secret_key = 'clave_secreta'

@app.route('/')
def index():
    if 'usuario_id' not in session:
        return redirect(url_for('login'))
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario = request.form['usuario']
        contrasena = request.form['contrasena']

        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, contrasena_hash, rol FROM usuarios WHERE usuario = %s", (usuario,))
        result = cur.fetchone()
        cur.close()
        conn.close()

        if result:
            user_id, contrasena_hash, rol = result
            if bcrypt.checkpw(contrasena.encode('utf-8'), contrasena_hash.encode('utf-8')):
                session['usuario_id'] = user_id
                session['usuario'] = usuario
                session['rol'] = rol
                return redirect(url_for('index'))

        flash('Usuario o contraseña incorrectos.', 'danger')

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
