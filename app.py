
from flask import Flask, render_template, request, redirect, url_for, session
import psycopg2
import psycopg2.extras
import hashlib

app = Flask(__name__)
app.secret_key = "clave_secreta"  # Cambiar por una clave segura

def get_connection():
    return psycopg2.connect(
        host="dpg-d1blfm0dl3ps73eqif70-a",
        database="finesdb_sng6",
        user="finesdb_sng6_user",
        password="IxPys2jK7nwhNxl2dlsch49EILGOHwSO"
    )

def verificar_usuario(usuario, contrasena):
    conn = get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("SELECT * FROM usuarios WHERE usuario = %s", (usuario,))
    user = cur.fetchone()
    cur.close()
    conn.close()

    if user:
        hash_contrasena = hashlib.sha256(contrasena.encode()).hexdigest()
        return hash_contrasena == user["contrasena_hash"], user["rol"]
    return False, None

@app.route("/")
def index():
    if "usuario" in session:
        return f"Bienvenido, {session['usuario']}! Rol: {session['rol']}"
    return redirect(url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        usuario = request.form.get("usuario", "")
        password = request.form.get("password", "")

        if not usuario or not password:
            error = "Por favor, completá todos los campos."
        else:
            valido, rol = verificar_usuario(usuario, password)
            if valido:
                session["usuario"] = usuario
                session["rol"] = rol
                return redirect(url_for("index"))
            else:
                error = "Usuario o contraseña incorrectos."

    return render_template("login.html", error=error)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)
