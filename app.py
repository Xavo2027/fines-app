import os
from flask import Flask, render_template, request, redirect, url_for, session, send_file
from flask import flash
from db_connect import get_db_connection
import pandas as pd
import xlsxwriter

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "default_secret_key")

@app.route('/')
def index():
    return render_template('index.html')

# ... Agregar más rutas según la lógica original
# Ejemplo:
@app.route('/login')
def login():
    return render_template('login.html')

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)