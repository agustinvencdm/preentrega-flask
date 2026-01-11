// Selección simple según preferencia del usuario
const form = document.getElementById("contact");
const submitBtn = document.querySelector(".enviar");
const spinnerOverlay = document.querySelector(".spinner-overlay");
const recaptchaError = document.getElementById("recaptcha-error");

// Escuchar el submit
form.addEventListener("submit", function (e) {
    e.preventDefault();

    if (recaptchaError) recaptchaError.textContent = "";

    const recaptchaResponse = grecaptcha.getResponse();

    if (!recaptchaResponse) {
        if (recaptchaError) {
            recaptchaError.textContent = "Por favor, completa el reCAPTCHA";
        }
        return;
    }

    if (spinnerOverlay) spinnerOverlay.classList.remove("hidden");
    if (submitBtn) submitBtn.disabled = true;

    const data = {
        nombre: document.getElementById("nombre")?.value.trim() || "",
        email: document.getElementById("email")?.value.trim() || "",
        telefono: document.getElementById("telefono")?.value.trim() || "",
        mensaje: document.getElementById("mensaje")?.value.trim() || "",
        recaptcha: recaptchaResponse,
    };

    enviarFormulario(data);
});

async function enviarFormulario(data) {
    try {
        const response = await fetch("/contacto", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(data),
        });

        console.log("Response status:", response.status);

        const text = await response.text();
        let res;

        try {
            res = JSON.parse(text);
        } catch {
            res = { error: text };
        }

        if (spinnerOverlay) spinnerOverlay.classList.add("hidden");
        if (submitBtn) submitBtn.disabled = false;

        if (response.ok && res.success) {
            mostrarExito();
            form.reset();
            grecaptcha.reset();
            if (recaptchaError) recaptchaError.textContent = "";
            return;
        }

        if (res.field) {
            const input = document.getElementById(res.field);
            if (input) {
                input.setCustomValidity(res.error);
                input.reportValidity();
                input.addEventListener("input", () =>
                    input.setCustomValidity("")
                );
            }
            if (res.field === "recaptcha" && recaptchaError) {
                recaptchaError.textContent = res.error;
            }
            return;
        }

        alert(res.error || "Error al enviar el formulario");

    } catch (error) {
        if (spinnerOverlay) spinnerOverlay.classList.add("hidden");
        if (submitBtn) submitBtn.disabled = false;
        console.error(error);
        alert("Error de conexión con el servidor");
    }
}

// Función para mostrar modal de éxito
function mostrarExito() {
    const modal = document.getElementById("modal-exito");
    if (!modal) return;

    modal.classList.remove("hidden");
    setTimeout(() => modal.classList.add("hidden"), 3000);
}
