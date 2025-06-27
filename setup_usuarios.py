from db_connect import get_db_connection

def crear_tabla_y_usuario():
    conn = get_db_connection()
    cur = conn.cursor()

    # Crear tabla si no existe
    cur.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id SERIAL PRIMARY KEY,
            usuario VARCHAR(100) NOT NULL,
            contraseña VARCHAR(100) NOT NULL
        )
    """)

    # Verificar si el usuario ya existe
    cur.execute("SELECT * FROM usuarios WHERE usuario = %s", ('admin',))
    if cur.fetchone() is None:
        cur.execute("INSERT INTO usuarios (usuario, contraseña) VALUES (%s, %s)", ('admin', 'admin123'))
        print("Usuario 'admin' creado.")
    else:
        print("El usuario 'admin' ya existe. No se agregó nuevamente.")

    conn.commit()
    cur.close()
    conn.close()
    print("Proceso finalizado correctamente.")

if __name__ == '__main__':
    crear_tabla_y_usuario()
