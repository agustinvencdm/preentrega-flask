from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import re
import smtplib
import requests
import os
from email.message import EmailMessage

app = Flask(__name__)
CORS(app)

# ======================
# CONFIGURACIÓN MAIL (ENV)
# ======================
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USER = os.environ.get("SMTP_USER")
SMTP_PASS = os.environ.get("SMTP_PASS")
MAIL_DESTINO = os.environ.get("MAIL_DESTINO")

RECAPTCHA_SECRET = os.environ.get("RECAPTCHA_SECRET")

# ======================
# RUTAS FRONTEND
# ======================
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/contacto", methods=["GET", "POST"])
def contacto():
    if request.method == "GET":
        return render_template("contacto.html")

    data = request.get_json(silent=True)
    if not data:
        return jsonify(error="Datos inválidos"), 400

    name = data.get("nombre", "").strip()
    email = data.get("email", "").strip()
    number = data.get("telefono", "").strip()
    message = data.get("mensaje", "").strip()
    recaptcha = data.get("recaptcha", "").strip()

    # -------- VALIDACIONES --------
    if not name:
        return jsonify(error="El nombre es obligatorio", field="nombre"), 400

    if not re.match(r"^[A-Za-zÁÉÍÓÚáéíóúÑñ ]+$", name):
        return jsonify(error="El nombre solo puede contener letras y espacios", field="nombre"), 400

    if not email:
        return jsonify(error="El email es obligatorio", field="email"), 400

    if not number or not number.isdigit():
        return jsonify(error="El teléfono solo puede contener números", field="telefono"), 400

    if len(number) < 7:
        return jsonify(error="El número es demasiado corto", field="telefono"), 400

    if not message:
        return jsonify(error="El mensaje es obligatorio", field="mensaje"), 400

    if not recaptcha:
        return jsonify(error="Por favor, completá el reCAPTCHA", field="recaptcha"), 400

    if not re.match(r"^[^@]+@[^@]+\.[a-zA-Z]{2,}$", email):
        return jsonify(error="Email inválido", field="email"), 400

    # -------- RECAPTCHA --------
    recaptcha_verify = requests.post(
        "https://www.google.com/recaptcha/api/siteverify",
        data={
            "secret": RECAPTCHA_SECRET,
            "response": recaptcha
        }
    ).json()

    if not recaptcha_verify.get("success"):
        return jsonify(error="reCAPTCHA inválido", field="recaptcha"), 400

    # -------- MAIL --------
    msg = EmailMessage()
    msg["Subject"] = "Nueva consulta desde la web"
    msg["From"] = SMTP_USER
    msg["To"] = MAIL_DESTINO
    msg["Reply-To"] = email

    msg.set_content(f"""
Nombre: {name}
Email: {email}
Teléfono: {number}

Mensaje:
{message}
""")

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            server.send_message(msg)
    except Exception as e:
        print(e)
        return jsonify(error="No se pudo enviar el correo"), 500

    return jsonify(success=True, message="Formulario enviado"), 200


@app.route("/consolas")
def consolas():
    return render_template("consolas.html")

@app.route("/juegos")
def juegos():
    return render_template("juegos.html")

@app.route("/suscripciones")
def suscripciones():
    return render_template("suscripciones.html")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)