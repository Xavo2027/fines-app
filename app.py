
# app.py
from flask import Flask, render_template, request, redirect, url_for, send_file
import sqlite3
import pandas as pd
import io

app = Flask(__name__)

# DB INIT
def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS alumno (
                    dni INTEGER PRIMARY KEY,
                    nombre TEXT NOT NULL,
                    comision TEXT NOT NULL)''')
    c.execute('''CREATE TABLE IF NOT EXISTS pase (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    dni INTEGER,
                    comision_origen TEXT,
                    comision_destino TEXT,
                    fecha TEXT)''')
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/alumnos')
def alumnos():
    conn = sqlite3.connect('database.db')
    alumnos = conn.execute("SELECT * FROM alumno").fetchall()
    conn.close()
    return render_template('alumnos.html', alumnos=alumnos)

@app.route('/agregar_alumno', methods=['POST'])
def agregar_alumno():
    dni = request.form['dni']
    nombre = request.form['nombre']
    comision = request.form['comision']
    conn = sqlite3.connect('database.db')
    conn.execute("INSERT INTO alumno (dni, nombre, comision) VALUES (?, ?, ?)", (dni, nombre, comision))
    conn.commit()
    conn.close()
    return redirect(url_for('alumnos'))

@app.route('/comisiones')
def comisiones():
    conn = sqlite3.connect('database.db')
    comisiones = conn.execute("SELECT DISTINCT comision FROM alumno").fetchall()
    conn.close()
    return render_template('comisiones.html', comisiones=comisiones)

@app.route('/pases')
def pases():
    conn = sqlite3.connect('database.db')
    pases = conn.execute("SELECT * FROM pase").fetchall()
    conn.close()
    return render_template('pases.html', pases=pases)

@app.route('/realizar_pase', methods=['POST'])
def realizar_pase():
    dni = request.form['dni']
    comision_origen = request.form['comision_origen']
    comision_destino = request.form['comision_destino']
    fecha = request.form['fecha']
    conn = sqlite3.connect('database.db')
    conn.execute("INSERT INTO pase (dni, comision_origen, comision_destino, fecha) VALUES (?, ?, ?, ?)",
                 (dni, comision_origen, comision_destino, fecha))
    conn.execute("UPDATE alumno SET comision = ? WHERE dni = ?", (comision_destino, dni))
    conn.commit()
    conn.close()
    return redirect(url_for('pases'))

@app.route('/descargar_excel')
def descargar_excel():
    conn = sqlite3.connect('database.db')
    alumnos = conn.execute("SELECT dni, nombre, comision FROM alumno ORDER BY comision").fetchall()
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
    conn = sqlite3.connect('database.db')
    alumnos = conn.execute("SELECT dni, nombre, comision FROM alumno ORDER BY comision").fetchall()
    conn.close()
    return render_template('vista_excel.html', alumnos=alumnos)

@app.route('/debug_db')
def debug_db():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM alumno")
        total = cur.fetchone()[0]
        conn.close()
        return f"✔ Conexión OK. Alumnos en la base: {total}"
    except Exception as e:
        return f"❌ Error de conexión: {e}"





if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=10000)
