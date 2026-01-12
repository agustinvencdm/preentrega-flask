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
# Para Gmail con SSL usamos el puerto 465
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 465
SMTP_USER = os.environ.get("SMTP_USER", "")
SMTP_PASS = os.environ.get("SMTP_PASS", "")
MAIL_DESTINO = os.environ.get("MAIL_DESTINO", "")
RECAPTCHA_SECRET = os.environ.get("RECAPTCHA_SECRET_KEY", "")

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

    # Obtener JSON de forma segura
    data = request.get_json(silent=True)
    if not data:
        return jsonify(error="Datos inválidos o vacíos"), 400

    name = data.get("nombre", "").strip()
    email = data.get("email", "").strip()
    number = data.get("telefono", "").strip()
    message = data.get("mensaje", "").strip()
    recaptcha_token = data.get("recaptcha", "").strip()

    # -------- VALIDACIONES --------
    if not name or not re.match(r"^[A-Za-zÁÉÍÓÚáéíóúÑñ ]+$", name):
        return jsonify(error="Nombre inválido", field="nombre"), 400

    if not email or not re.match(r"^[^@]+@[^@]+\.[a-zA-Z]{2,}$", email):
        return jsonify(error="Email inválido", field="email"), 400

    if not number or not number.isdigit() or len(number) < 7:
        return jsonify(error="Teléfono inválido (mínimo 7 números)", field="telefono"), 400

    if not message:
        return jsonify(error="El mensaje es obligatorio", field="mensaje"), 400

    if not recaptcha_token:
        return jsonify(error="Por favor, completá el reCAPTCHA", field="recaptcha"), 400

    # -------- RECAPTCHA (Verificación con Google) --------
    try:
        if not RECAPTCHA_SECRET:
            print("ERROR: Falta RECAPTCHA_SECRET_KEY en las variables de entorno.")
            return jsonify(error="Error de configuración de seguridad"), 500

        r = requests.post(
            "https://www.google.com/recaptcha/api/siteverify",
            data={
                "secret": RECAPTCHA_SECRET,
                "response": recaptcha_token
            },
            timeout=10
        )
        recaptcha_verify = r.json()
        
        if not recaptcha_verify.get("success"):
            print(f"DEBUG: reCAPTCHA fallido: {recaptcha_verify}")
            return jsonify(error="Validación de reCAPTCHA fallida", field="recaptcha"), 400
            
    except Exception as e:
        print(f"Error conexión reCAPTCHA: {e}")
        return jsonify(error="Error al validar seguridad"), 500

    # -------- ENVÍO DE MAIL --------
    try:
        if not SMTP_USER or not SMTP_PASS or not MAIL_DESTINO:
            print("ERROR: Faltan variables de entorno para el correo.")
            return jsonify(error="Configuración de correo incompleta"), 500

        msg = EmailMessage()
        msg["Subject"] = f"Nueva consulta de {name}"
        msg["From"] = SMTP_USER
        msg["To"] = MAIL_DESTINO
        msg["Reply-To"] = email
        msg.set_content(f"Nombre: {name}\nEmail: {email}\nTeléfono: {number}\n\nMensaje:\n{message}")

        # Uso de SMTP_SSL para mayor compatibilidad con Render y Gmail
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, timeout=15) as server:
            server.login(SMTP_USER, SMTP_PASS)
            server.send_message(msg)

        return jsonify(success=True, message="Formulario enviado con éxito"), 200

    except smtplib.SMTPAuthenticationError:
        print("ERROR: Fallo de autenticación SMTP. Revisar App Password.")
        return jsonify(error="Error de acceso al correo (Autenticación)"), 500
    except Exception as e:
        # Imprime el error exacto en los logs de Render para debuguear
        print(f"ERROR SMTP DETALLADO: {e}")
        return jsonify(error="No se pudo enviar el correo"), 500

# --- Otras rutas ---
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