from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "clave_secreta"

@app.before_first_request
def crear_usuario_demo():
    if not os.path.exists("fines.db"):
        conn = sqlite3.connect('fines.db')
        cursor = conn.cursor()
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS usuarios (id INTEGER PRIMARY KEY AUTOINCREMENT, usuario TEXT NOT NULL, password TEXT NOT NULL, rol TEXT NOT NULL)"
        )
        cursor.execute("SELECT * FROM usuarios WHERE usuario = ?", ('admin',))
        if not cursor.fetchone():
            cursor.execute("INSERT INTO usuarios (usuario, password, rol) VALUES (?, ?, ?)", ('admin', 'admin', 'admin'))
        conn.commit()
        conn.close()

@app.route("/")
def index():
    rol = session.get("rol", "desconocido")
    return render_template("index.html", rol=rol)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        usuario = request.form["usuario"]
        password = request.form["password"]

        conn = sqlite3.connect("fines.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE usuario=? AND password=?", (usuario, password))
        usuario_encontrado = cursor.fetchone()
        conn.close()

        if usuario_encontrado:
            session["usuario"] = usuario
            session["rol"] = usuario_encontrado[3]
            return redirect(url_for("index"))
        else:
            return render_template("login.html", error="Credenciales incorrectas")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)
