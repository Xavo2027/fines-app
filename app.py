
from flask import Flask, render_template, request, redirect, url_for, send_file, session
import psycopg2
import pandas as pd
import io
import os
from functools import wraps

app = Flask(__name__)
app.secret_key = 'clave-super-secreta'
DATABASE_URL = os.environ.get("DATABASE_URL")

def get_db_connection():
    return psycopg2.connect(DATABASE_URL)

def init_db():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS alumno (
        dni INTEGER PRIMARY KEY,
        nombre TEXT NOT NULL,
        comision TEXT NOT NULL)""")
    c.execute("""CREATE TABLE IF NOT EXISTS pase (
        id SERIAL PRIMARY KEY,
        dni INTEGER,
        comision_origen TEXT,
        comision_destino TEXT,
        fecha TEXT)""")
    c.execute("""CREATE TABLE IF NOT EXISTS usuario (
        id SERIAL PRIMARY KEY,
        nombre TEXT NOT NULL,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        rol TEXT NOT NULL)""")
    c.execute("SELECT COUNT(*) FROM usuario")
    if c.fetchone()[0] == 0:
        c.execute("""
            INSERT INTO usuario (nombre, username, password, rol) VALUES
            ('Coordinador Admin', 'coordinador', '1234', 'coordinador'),
            ('Analista General', 'analista', '1234', 'analista'),
            ('Directora Ejecutiva', 'ceo', '1234', 'ceo')
        """)
    conn.commit()
    conn.close()

def requiere_rol(*roles):
    def wrapper(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'rol' not in session or session['rol'] not in roles:
                return "Acceso denegado", 403
            return f(*args, **kwargs)
        return decorated_function
    return wrapper

@app.before_request
def requerir_login():
    if 'usuario' not in session and request.endpoint not in ('login', 'static'):
        return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = request.form['username']
        pwd = request.form['password']
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT username, rol FROM usuario WHERE username = %s AND password = %s", (user, pwd))
        result = cur.fetchone()
        conn.close()
        if result:
            session['usuario'] = result[0]
            session['rol'] = result[1]
            return redirect(url_for('index'))
        else:
            return "Credenciales inválidas", 401
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/')
@requiere_rol('coordinador', 'analista', 'ceo')
def index():
    return render_template('index.html', usuario=session.get('usuario'), rol=session.get('rol'))

@app.route('/alumnos')
@requiere_rol('coordinador', 'analista', 'ceo')
def alumnos():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM alumno")
    alumnos = cur.fetchall()
    conn.close()
    return render_template('alumnos.html', alumnos=alumnos, rol=session.get("rol"))

@app.route('/agregar_alumno', methods=['POST'])
@requiere_rol('coordinador', 'analista', 'ceo')
def agregar_alumno():
    usuario = request.form.get("usuario")
    nombre = request.form['nombre']
    comision = request.form['comision']
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO alumno (dni, nombre, comision) VALUES (%s, %s, %s) ON CONFLICT (dni) DO NOTHING", (dni, nombre, comision))
    conn.commit()
    conn.close()
    return redirect(url_for('alumnos'))

@app.route('/comisiones')
@requiere_rol('coordinador', 'analista', 'ceo')
def comisiones():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT DISTINCT comision FROM alumno")
    comisiones = cur.fetchall()
    conn.close()
    return render_template('comisiones.html', comisiones=comisiones, rol=session.get("rol"))

@app.route('/pases')
@requiere_rol('analista', 'ceo')
def pases():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM pase")
    pases = cur.fetchall()
    conn.close()
    return render_template('pases.html', pases=pases, rol=session.get("rol"))

@app.route('/realizar_pase', methods=['POST'])
@requiere_rol('analista', 'ceo')
def realizar_pase():
    usuario = request.form.get("usuario")
    comision_origen = request.form['comision_origen']
    comision_destino = request.form['comision_destino']
    fecha = request.form['fecha']
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO pase (dni, comision_origen, comision_destino, fecha) VALUES (%s, %s, %s, %s)", (dni, comision_origen, comision_destino, fecha))
    cur.execute("UPDATE alumno SET comision = %s WHERE dni = %s", (comision_destino, dni))
    conn.commit()
    conn.close()
    return redirect(url_for('pases'))

@app.route('/descargar_excel')
@requiere_rol('analista', 'ceo')
def descargar_excel():
    conn = get_db_connection()
    df = pd.read_sql("SELECT * FROM alumno", conn)
    conn.close()
    output = io.BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, index=False, sheet_name='Alumnos')
    writer.close()
    output.seek(0)
    return send_file(output, download_name="alumnos.xlsx", as_attachment=True)

@app.route('/vista_excel')
@requiere_rol('analista', 'ceo')
def vista_excel():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM alumno")
    alumnos = cur.fetchall()
    conn.close()
    return render_template('vista_excel.html', alumnos=alumnos, rol=session.get("rol"))

@app.route('/admin/usuarios')
@requiere_rol('ceo')
def ver_usuarios():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, nombre, username, rol FROM usuario ORDER BY id")
    usuarios = cur.fetchall()
    conn.close()
    return render_template('usuarios.html', usuarios=usuarios, rol=session.get("rol"), usuario=session.get("usuario"))

@app.route('/admin/usuarios/nuevo', methods=['GET', 'POST'])
@requiere_rol('ceo')
def nuevo_usuario():
    if request.method == 'POST':
        nombre = request.form['nombre']
        username = request.form['username']
        password = request.form.get("password")
        rol = request.form['rol']
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO usuario (nombre, username, password, rol) VALUES (%s, %s, %s, %s)", (nombre, username, password, rol))
        conn.commit()
        conn.close()
        return redirect(url_for('ver_usuarios'))
    return render_template('nuevo_usuario.html', rol=session.get("rol"), usuario=session.get("usuario"))

if __name__ == '__main__':
    init_db()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
