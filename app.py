
from flask import Flask, render_template, request
import psycopg2
import os

app = Flask(__name__)

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

        conn = psycopg2.connect(
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASS"),
            host=os.getenv("DB_HOST"),
            port="5432"
        )
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
    conn = psycopg2.connect(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASS"),
        host=os.getenv("DB_HOST"),
        port="5432"
    )
    cur = conn.cursor()
    cur.execute("SELECT nombre_completo, dni, email, turno_preferencia, materias_a_rendir FROM inscripciones ORDER BY fecha_envio DESC")
    inscriptos = cur.fetchall()
    cur.close()
    conn.close()
    return render_template("inscriptos.html", inscriptos=inscriptos)

@app.route("/")
def index():
    return "", 302, {"Location": "/alumnos"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
