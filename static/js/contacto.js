// Selección simple según preferencia del usuario
const form = document.getElementById("contact");
const submitBtn = document.querySelector(".enviar");
const spinnerOverlay = document.querySelector(".spinner-overlay");
const recaptchaError = document.getElementById("recaptcha-error");

// Escuchar el submit
form.addEventListener("submit", function (e) {
    e.preventDefault();

    // Limpiamos error previo del reCAPTCHA
    if (recaptchaError) recaptchaError.textContent = "";

    // Obtener token del reCAPTCHA
    const recaptchaResponse = grecaptcha.getResponse();

    // No bloqueamos con alert, el backend validará también
    // pero podemos mostrar el mensaje inmediatamente si no se completó
    if (!recaptchaResponse) {
        if (recaptchaError) {
            recaptchaError.textContent = "Por favor, completa el reCAPTCHA";
        }
        return; //  NO enviar el formulario
    }

    // Mostrar spinner
    if (spinnerOverlay) spinnerOverlay.classList.remove("hidden");
    if (submitBtn) submitBtn.disabled = true;

    // Crear objeto de datos (usar las claves que el backend espera)
    const data = {
        nombre: document.getElementById("nombre")
            ? document.getElementById("nombre").value.trim()
            : "",
        email: document.getElementById("email")
            ? document.getElementById("email").value.trim()
            : "",
        telefono: document.getElementById("telefono")
            ? document.getElementById("telefono").value.trim()
            : "",
        mensaje: document.getElementById("mensaje")
            ? document.getElementById("mensaje").value.trim()
            : "",
        recaptcha: recaptchaResponse, // enviamos el token al backend
    };

    enviarFormulario(data);
});

// Función para enviar datos al servidor
async function enviarFormulario(data) {
    try {
        const response = await fetch("/contacto", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(data),
        });

        // Mejor logging: status, statusText y cuerpo (JSON o texto)
        console.log("Response status:", response.status, response.statusText);
        let res = {};
        try {
            const text = await response.text();
            try {
                res = JSON.parse(text);
                console.log("Respuesta del servidor (JSON):", res);
            } catch (parseErr) {
                console.log("Respuesta del servidor (no-JSON):", text);
                res = { error: text };
            }
        } catch (err) {
            console.error("Error leyendo respuesta del servidor:", err);
        }

        // Ocultar spinner siempre que termine
        if (spinnerOverlay) spinnerOverlay.classList.add("hidden");
        if (submitBtn) submitBtn.disabled = false;

        // ------------------------------
        // Verificar éxito según Flask
        if (response.ok && res.success) {
            mostrarExito(); // Mostrar modal de éxito
            form.reset(); // Limpiar campos
            grecaptcha.reset(); // Resetear reCAPTCHA
            if (recaptchaError) recaptchaError.textContent = "";
        } else if (res.field) {
            // Mostrar burbuja de error para el campo correspondiente
            const inputConError = document.getElementById(res.field);
            if (inputConError) {
                inputConError.setCustomValidity(res.error);
                inputConError.reportValidity();
                inputConError.addEventListener("input", () =>
                    inputConError.setCustomValidity("")
                );
            }

            // Mostrar error del reCAPTCHA si corresponde
            if (res.field === "recaptcha" && recaptchaError) {
                recaptchaError.textContent = res.error;
            }
        } else {
            // Error genérico
            if (recaptchaError && res.error.includes("reCAPTCHA")) {
                recaptchaError.textContent = res.error;
            } else {
                alert(res.error || "Error al enviar el formulario");
            }
        }
    } catch (error) {
        // Error de conexión u otros
        if (spinnerOverlay) spinnerOverlay.classList.add("hidden");
        if (submitBtn) submitBtn.disabled = false;
        console.error("Fetch error:", error);
        alert("Error de conexión con el servidor");
    }
}

// Función para mostrar modal de éxito
function mostrarExito() {
    const modal = document.getElementById("modal-exito");
    if (!modal) return;

    modal.classList.remove("hidden");

    // Se cierra solo a los 3 segundos
    setTimeout(() => {
        modal.classList.add("hidden");
    }, 3000);
}
