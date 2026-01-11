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
# CONFIGURACIÓN (VARIABLES DE ENTORNO)
# ======================
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
# Es vital que estas variables estén configuradas en el panel de Onrender
SMTP_USER = os.environ.get("SMTP_USER")
SMTP_PASS = os.environ.get("SMTP_PASS")
MAIL_DESTINO = os.environ.get("MAIL_DESTINO")
RECAPTCHA_SECRET = os.environ.get("RECAPTCHA_SECRET_KEY")

# ======================
# RUTAS DE PÁGINAS E ESTÁTICAS
# ======================
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/consolas")
def consolas():
    return render_template("consolas.html")

@app.route("/juegos")
def juegos():
    return render_template("juegos.html")

@app.route("/suscripciones")
def suscripciones():
    return render_template("suscripciones.html")

@app.route("/contacto", methods=["GET"])
def contacto_get():
    return render_template("contacto.html")

# ======================
# PROCESAMIENTO DEL FORMULARIO
# ======================
@app.route("/contacto", methods=["POST"])
def contacto_post():
    data = request.get_json(silent=True)
    if not data:
        return jsonify(error="No se recibieron datos válidos"), 400

    # Limpieza de datos
    name = data.get("nombre", "").strip()
    email = data.get("email", "").strip()
    number = data.get("telefono", "").strip()
    message = data.get("mensaje", "").strip()
    recaptcha = data.get("recaptcha", "").strip()

    # -------- VALIDACIONES LÓGICAS --------
    if not name or not re.match(r"^[A-Za-zÁÉÍÓÚáéíóúÑñ ]+$", name):
        return jsonify(error="Nombre inválido (solo letras)", field="nombre"), 400

    if not email or not re.match(r"^[^@]+@[^@]+\.[a-zA-Z]{2,}$", email):
        return jsonify(error="Email inválido", field="email"), 400

    if not number or not number.isdigit() or len(number) < 7:
        return jsonify(error="Teléfono inválido (mínimo 7 números)", field="telefono"), 400

    if not message:
        return jsonify(error="El mensaje no puede estar vacío", field="mensaje"), 400

    if not recaptcha:
        return jsonify(error="Por favor, completa el reCAPTCHA", field="recaptcha"), 400

    # -------- VERIFICACIÓN RECAPTCHA --------
    try:
        r = requests.post(
            "https://www.google.com/recaptcha/api/siteverify",
            data={
                "secret": RECAPTCHA_SECRET,
                "response": recaptcha
            },
            timeout=7
        )
        recaptcha_verify = r.json()
        
        if not recaptcha_verify.get("success"):
            print(f"DEBUG: reCAPTCHA fallido: {recaptcha_verify}")
            return jsonify(error="Validación de seguridad fallida", field="recaptcha"), 400
            
    except Exception as e:
        print(f"ERROR reCAPTCHA: {e}")
        return jsonify(error="Error al conectar con el servicio de seguridad"), 500

    # -------- ENVÍO DE EMAIL --------
    try:
        # Verificación preventiva de credenciales
        if not all([SMTP_USER, SMTP_PASS, MAIL_DESTINO]):
            print("ERROR: Variables de entorno de correo no configuradas en el servidor.")
            return jsonify(error="El servicio de correo no está configurado."), 500

        msg = EmailMessage()
        msg["Subject"] = f"Nueva consulta web: {name}"
        msg["From"] = SMTP_USER
        msg["To"] = MAIL_DESTINO
        msg["Reply-To"] = email
        
        cuerpo_mensaje = (
            f"Has recibido un nuevo mensaje de contacto:\n\n"
            f"Nombre: {name}\n"
            f"Email: {email}\n"
            f"Teléfono: {number}\n\n"
            f"Mensaje:\n{message}"
        )
        msg.set_content(cuerpo_mensaje)

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=10) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            server.send_message(msg)

        return jsonify(success=True, message="Mensaje enviado con éxito"), 200

    except smtplib.SMTPAuthenticationError:
        print("ERROR: Autenticación SMTP fallida. Verifica la App Password.")
        return jsonify(error="Error de autenticación en el servidor de correo"), 500
    except Exception as e:
        print(f"ERROR INESPERADO SMTP: {e}")
        return jsonify(error="No se pudo enviar el correo en este momento"), 500

if __name__ == "__main__":
    # Onrender asigna el puerto automáticamente
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)