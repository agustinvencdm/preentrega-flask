from flask import Flask, request, jsonify, render_template
import re
import smtplib
import requests
from email.message import EmailMessage

app = Flask(__name__)


# Mostrar el formulario
@app.route("/")
def index():
    return render_template("index.html")

# ======================
# CONFIGURACIÓN MAIL
# ======================
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USER = "vitadev03@gmail.com"        # correo que envía
SMTP_PASS = "smfd rgab valf hncy"       # contraseña de app
MAIL_DESTINO = "vitadev03@gmail.com" # correo que recibe

# ======================
# ENDPOINT
# ======================
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
        return jsonify(error="El nombre es obligatorio" , field= "nombre"), 400

    # Validación: nombre solo letras y espacios
    if not re.match(r"^[A-Za-zÁÉÍÓÚáéíóúÑñ ]+$", name):
        return jsonify(error="El nombre solo puede contener letras y espacios", field="name"), 400


    if not email:
        return jsonify(error="El email es obligatorio", field = "email"), 400

    if not number:
        return jsonify(error="El numero es obligatorio", field = "telefono"), 400
    
    if not number.isdigit():
        return jsonify(error="El teléfono solo puede contener números", field="telefono"), 400
    
    if not message:
        return jsonify(error="El mensaje es obligatorio", field = "mensaje"), 400

    if len(number) < 7:
        return jsonify(error="El numero es demasiado corto", field = "telefono"), 400

    if not recaptcha:
        return jsonify(error="Por favor, completá el reCAPTCHA", field="recaptcha"), 400


    # Si tiene @ pero no tiene punto después del @ (ej: fdobal@gmail)
    if "@" in email:
        parte_dominio = email.split("@")[-1]
        if "." not in parte_dominio:
            return jsonify(error="Falta el dominio (ejemplo: .com, .net)", field="email"), 400

    if not re.match(r"^[^@]+@[^@]+\.[a-zA-Z]{2,}$", email):
        return jsonify(error="Email inválido", field = "email"), 400


    if len(name) > 50:
        return jsonify(error="El nombre es demasiado largo", field = "nombre"), 400


    if len(name) < 3:
        return jsonify(error="El nombre es demasiado corto", field = "nombre"), 400



    if len(message) < 4:
        return jsonify(error="El mensaje es demasiado corto", field="mensaje"), 400
    if len(message) > 2000:
        return jsonify(error="El mensaje es demasiado largo", field="mensaje"), 400




    recaptcha_token = data.get("recaptcha", "")
    recaptcha_secret = "6LfqVjwsAAAAAJ44ZEIsQBZHQyAAuEbsuXQ8kOQO"

    # Verificación reCAPTCHA
    recaptcha_verify = requests.post(
        "https://www.google.com/recaptcha/api/siteverify",
        data={"secret": recaptcha_secret, "response": recaptcha_token}
    ).json()

    if not recaptcha_verify.get("success", False):
        return jsonify(error="reCAPTCHA inválido, por favor verifica.", field = "recaptcha"), 400

    # -------- ARMAR MAIL --------
    msg = EmailMessage()
    msg["Subject"] = "Nueva consulta desde la web"
    msg["From"] = SMTP_USER
    msg["To"] = MAIL_DESTINO
    msg["Reply-To"] = email  # para responder directo al cliente

    msg.set_content(f"""
Nueva consulta desde la web

Nombre: {name}
Email: {email}
Número: {number}

Mensaje:
{message}
""")

    # -------- ENVIAR MAIL --------
    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            server.send_message(msg)

    except Exception as e:
        print(e)  # log interno
        return jsonify(error="No se pudo enviar el correo"), 500

    return jsonify(success=True, message="Formulario enviado"), 200


@app.route('/consolas')
def consolas():
    return render_template('consolas.html')


@app.route('/juegos')
def juegos():
    return render_template('juegos.html')


@app.route('/suscripciones')
def suscripciones():
    return render_template('suscripciones.html')

@app.route('/.well-known/appspecific/com.chrome.devtools.json')
def chrome_devtools_config():
    return jsonify({}), 200


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000, debug=True)