from flask import Flask, render_template, request, redirect, url_for, send_file
import psycopg2
import pandas as pd
import io
import os

app = Flask(__name__)

DATABASE_URL = os.environ.get("DATABASE_URL")

def get_db_connection():
    return psycopg2.connect(DATABASE_URL)

@app.before_first_request
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
    conn.commit()
    conn.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/alumnos')
def alumnos():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM alumno")
    alumnos = cur.fetchall()
    conn.close()
    return render_template('alumnos.html', alumnos=alumnos)

@app.route('/agregar_alumno', methods=['POST'])
def agregar_alumno():
    dni = request.form['dni']
    nombre = request.form['nombre']
    comision = request.form['comision']
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO alumno (dni, nombre, comision) VALUES (%s, %s, %s)", (dni, nombre, comision))
    conn.commit()
    conn.close()
    return redirect(url_for('alumnos'))

@app.route('/comisiones')
def comisiones():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT DISTINCT comision FROM alumno")
    comisiones = cur.fetchall()
    conn.close()
    return render_template('comisiones.html', comisiones=comisiones)

@app.route('/pases')
def pases():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM pase")
    pases = cur.fetchall()
    conn.close()
    return render_template('pases.html', pases=pases)

@app.route('/realizar_pase', methods=['POST'])
def realizar_pase():
    dni = request.form['dni']
    comision_origen = request.form['comision_origen']
    comision_destino = request.form['comision_destino']
    fecha = request.form['fecha']
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO pase (dni, comision_origen, comision_destino, fecha) VALUES (%s, %s, %s, %s)",
                (dni, comision_origen, comision_destino, fecha))
    cur.execute("UPDATE alumno SET comision = %s WHERE dni = %s", (comision_destino, dni))
    conn.commit()
    conn.close()
    return redirect(url_for('pases'))

@app.route('/descargar_excel')
def descargar_excel():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT dni, nombre, comision FROM alumno ORDER BY comision")
    alumnos = cur.fetchall()
    conn.close()

    df = pd.DataFrame(alumnos, columns=["DNI", "Nombre", "Comisión"])

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Alumnos')

    output.seek(0)
    return send_file(
        output,
        as_attachment=True,
        download_name='alumnos_por_comision.xlsx',
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

@app.route('/vista_excel')
def vista_excel():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT dni, nombre, comision FROM alumno ORDER BY comision")
    alumnos = cur.fetchall()
    conn.close()
    return render_template('vista_excel.html', alumnos=alumnos)

@app.route('/debug_db')
def debug_db():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM alumno")
        count = cur.fetchone()[0]
        conn.close()
        return f"✔ Conexión OK. Alumnos en la base: {count}"
    except Exception as e:
        return f"❌ Error de conexión: {e}"

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=10000)
