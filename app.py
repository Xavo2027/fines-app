
from flask import Flask, render_template, request, redirect, url_for, session
import psycopg2
import os
from psycopg2.extras import RealDictCursor
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = os.urandom(24)

def get_db_connection():
    conn = psycopg2.connect(os.getenv("DATABASE_URL"))
    return conn

@app.route("/")
def index():
    return redirect("/alumnos")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        dni = request.form["dni"]
        password = request.form["password"]
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM usuarios WHERE dni = %s", (dni,))
        usuario = cur.fetchone()
        cur.close()
        conn.close()
        if usuario and check_password_hash(usuario[2], password):
            session["dni"] = dni
            return redirect("/alumnos")
        else:
            return render_template("login.html", error="Credenciales inválidas")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("dni", None)
    return redirect("/login")

@app.route("/nuevo_usuario", methods=["GET", "POST"])
def nuevo_usuario():
    if request.method == "POST":
        dni = request.form["dni"]
        password = request.form["password"]
        rol = request.form["rol"]
        hashed_password = generate_password_hash(password)
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO usuarios (dni, password, rol) VALUES (%s, %s, %s)", (dni, hashed_password, rol))
        conn.commit()
        cur.close()
        conn.close()
        return redirect("/login")
    return render_template("nuevo_usuario.html")

@app.route("/alumnos", methods=["GET", "POST"])
def inscripcion():
    if request.method == "POST":
        datos = (
            request.form.get("email"),
            request.form.get("dni"),
            request.form.get("apellido"),
            request.form.get("nombre_completo"),
            request.form.get("celular"),
            request.form.get("celular_alternativo"),
            request.form.get("fecha_nacimiento"),
            request.form.get("curso_anterior"),
            request.form.get("turno_preferencia"),
            request.form.get("cursando_fines"),
            request.form.get("ubicacion_ultima_escuela"),
            request.form.get("nombre_ultima_escuela"),
            request.form.get("localidad_institucion"),
            request.form.get("materias_totales"),
            request.form.get("materias_a_rendir"),
            request.form.get("materias_exactas"),
            request.form.get("materias_preferidas"),
            request.form.get("observaciones"),
            request.form.get("genero"),
            request.form.get("situacion_actual"),
            request.form.get("cursada_1etapa_2023")
        )
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS inscripciones (
              id SERIAL PRIMARY KEY,
              email TEXT,
              dni TEXT,
              apellido TEXT,
              nombre_completo TEXT,
              celular TEXT,
              celular_alternativo TEXT,
              fecha_nacimiento TEXT,
              curso_anterior TEXT,
              turno_preferencia TEXT,
              cursando_fines TEXT,
              ubicacion_ultima_escuela TEXT,
              nombre_ultima_escuela TEXT,
              localidad_institucion TEXT,
              materias_totales INTEGER,
              materias_a_rendir INTEGER,
              materias_exactas TEXT,
              materias_preferidas TEXT,
              observaciones TEXT,
              genero TEXT,
              situacion_actual TEXT,
              cursada_1etapa_2023 TEXT,
              fecha_envio TIMESTAMP DEFAULT NOW()
            )
        """)
        cur.execute("""
            INSERT INTO inscripciones (
              email, dni, apellido, nombre_completo, celular, celular_alternativo, fecha_nacimiento,
              curso_anterior, turno_preferencia, cursando_fines, ubicacion_ultima_escuela,
              nombre_ultima_escuela, localidad_institucion, materias_totales, materias_a_rendir,
              materias_exactas, materias_preferidas, observaciones, genero, situacion_actual, cursada_1etapa_2023
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, datos)
        conn.commit()
        cur.close()
        conn.close()
        return render_template("alumnos.html", mensaje="✅ Inscripción enviada con éxito.")
    return render_template("alumnos.html")

@app.route("/inscriptos")
def ver_inscriptos():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT nombre_completo, dni, email, turno_preferencia, materias_a_rendir FROM inscripciones ORDER BY fecha_envio DESC")
    inscriptos = cur.fetchall()
    cur.close()
    conn.close()
    return render_template("inscriptos.html", inscriptos=inscriptos)

@app.route("/comisiones")
def comisiones():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT nombre FROM comisiones")
    comisiones = cur.fetchall()
    cur.close()
    conn.close()
    return render_template("comisiones.html", comisiones=comisiones)

@app.route("/pases", methods=["GET", "POST"])
def pases():
    conn = get_db_connection()
    cur = conn.cursor()
    if request.method == "POST":
        dni = request.form["dni"]
        nueva_comision = request.form["nueva_comision"]
        cur.execute("UPDATE alumnos SET comision = %s WHERE dni = %s", (nueva_comision, dni))
        cur.execute("INSERT INTO pases (dni, nueva_comision) VALUES (%s, %s)", (dni, nueva_comision))
        conn.commit()
    cur.execute("SELECT * FROM pases")
    pases = cur.fetchall()
    cur.close()
    conn.close()
    return render_template("pases.html", pases=pases)

@app.route("/vista_excel")
def vista_excel():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * FROM alumnos")
    alumnos = cur.fetchall()
    cur.close()
    conn.close()
    return render_template("vista_excel.html", alumnos=alumnos)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
