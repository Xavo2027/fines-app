from flask import Flask, render_template, request, redirect, session, url_for
import psycopg2

app = Flask(__name__)
app.secret_key = 'supersecreto123'  # podés cambiarlo por seguridad

# Conexión a base de datos (Render)
def get_db_connection():
    return psycopg2.connect(
        host="dpg-d1blfm0dl3ps73eqif70-a",
        port="5432",
        database="finesdb_sng6",
        user="finesdb_sng6_user",
        password="IxPys2jK7nwhNx12d1sch49EILGOHwS0"
    )

# Crear tablas si no existen
@app.before_request
def create_tables():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('''
            CREATE TABLE IF NOT EXISTS usuarios (
                id SERIAL PRIMARY KEY,
                nombre TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                contraseña TEXT NOT NULL,
                rol TEXT NOT NULL
            );
        ''')
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print("Error creando tablas:", e)

# Página principal
@app.route('/')
def index():
    usuario = session.get('usuario')
    rol = session.get('rol')
    return render_template('index.html', usuario=usuario, rol=rol)

# Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        email = request.form['email']
        contraseña = request.form['contraseña']
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT nombre, rol FROM usuarios WHERE email = %s AND contraseña = %s", (email, contraseña))
        user = cur.fetchone()
        conn.close()
        if user:
            session['usuario'] = user[0]
            session['rol'] = user[1]
            return redirect(url_for('index'))
        else:
            error = 'Email o contraseña incorrectos.'
    return render_template('login.html', error=error)

# Usuarios (solo muestra lista por ahora)
@app.route('/usuarios')
def usuarios():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, nombre, email, rol FROM usuarios")
    usuarios = cur.fetchall()
    conn.close()
    return render_template('usuarios.html', usuarios=usuarios)

# Logout
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

# Run localmente
if __name__ == '__main__':
    app.run(debug=True)
