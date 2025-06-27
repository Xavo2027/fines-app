from flask import Flask, render_template, redirect, url_for, request, session
import psycopg2
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Conexión a la base de datos
def get_db_connection():
    return psycopg2.connect(
        host="dpg-...",  # reemplazá esto con tu host
        database="fines",
        user="...",
        password="..."
    )

# Inicialización de la base de datos (solo una vez)
@app.before_request
def create_tables():
    if not hasattr(app, 'db_initialized'):
        with app.app_context():
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("""
                CREATE TABLE IF NOT EXISTS usuarios (
                    id SERIAL PRIMARY KEY,
                    nombre TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    rol TEXT NOT NULL
                );
            """)
            conn.commit()
            cur.close()
            conn.close()
            app.db_initialized = True

# Rutas
@app.route('/')
def index():
    rol = session.get('rol', 'desconocido')
    return render_template('index.html', rol=rol)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM usuarios WHERE email = %s AND password = %s", (email, password))
        usuario = cur.fetchone()
        cur.close()
        conn.close()

        if usuario:
            session['usuario_id'] = usuario[0]
            session['nombre'] = usuario[1]
            session['rol'] = usuario[4]
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error='Credenciales incorrectas')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/usuarios')
def usuarios():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM usuarios")
    usuarios = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('usuarios.html', usuarios=usuarios)

if __name__ == '__main__':
    app.run(debug=True)
