from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "clave_secreta"

DB_NAME = "usuarios.db"

# 📌 Crear tabla si no existe
def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# 📌 Página principal
@app.route("/")
def index():
    if "username" in session:
        return redirect(url_for("home"))
    return render_template("login.html")

# 📌 Login
@app.route("/login", methods=["POST"])
def login():
    username = request.form["username"]
    password = request.form["password"]

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT * FROM usuarios WHERE username=? AND password=?", (username, password))
    user = c.fetchone()
    conn.close()

    if user:
        session["username"] = username
        return redirect(url_for("home"))
    else:
        return "Usuario o contraseña incorrectos"

# 📌 Registro
@app.route("/register", methods=["POST"])
def register():
    username = request.form["username"]
    password = request.form["password"]

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    try:
        c.execute("INSERT INTO usuarios (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
    except sqlite3.IntegrityError:
        return "El usuario ya existe"
    finally:
        conn.close()

    return redirect(url_for("index"))

# 📌 Página de inicio
@app.route("/home")
def home():
    if "username" in session:
        return f"Bienvenido {session['username']}! <br><a href='/logout'>Cerrar sesión</a>"
    return redirect(url_for("index"))

# 📌 Logout
@app.route("/logout")
def logout():
    session.pop("username", None)
    return redirect(url_for("index"))

# 📌 Ejecutar
if __name__ == "__main__":
    init_db()  # ✅ Crea la base de datos y la tabla si no existen
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
