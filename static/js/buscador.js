const form = document.querySelector("form");
const buscador = document.getElementById("buscador");
const mensaje = document.getElementById("mensaje-busqueda");

// En Flask los archivos estáticos se sirven en /static/...
const jsonRuta = "/static/js/textos.json";

let textos = {};

// ----------------------------------
// Carga del JSON
// ----------------------------------
fetch(jsonRuta)
  .then((res) => res.json())
  .then((data) => (textos = data))
  .catch((err) => console.error("Error cargando JSON:", err));

// ----------------------------------
// Buscar palabra
// ----------------------------------
function buscarPalabra(palabra, paginaActual, esRedireccion = false) {
  palabra = palabra.toLowerCase();
  let encontrada = false;

  mensaje.textContent = "";

  // Normalizar nombre de página
  if (paginaActual === "" || paginaActual === "index.html") {
    paginaActual = "index.html";
  } else if (!paginaActual.endsWith(".html")) {
    paginaActual += ".html";
  }

  // --- 1️⃣ Buscar en la página actual ---
  if (textos[paginaActual]) {
    const bloques = document.querySelectorAll(".contenido, #contenido");

    bloques.forEach((b) => {
      // 🔹 Limpiar resaltados anteriores
      b.querySelectorAll(".resaltado").forEach((span) => {
        span.replaceWith(span.textContent);
      });

      const original = b.innerHTML;
      const textoPlano = b.textContent;
      const regex = new RegExp(`(${palabra})`, "gi");

      if (textoPlano.toLowerCase().includes(palabra)) {
        b.innerHTML = original.replace(
          regex,
          `<span class="resaltado">$1</span>`
        );

        encontrada = true;

        const primera = b.querySelector(".resaltado");
        if (primera) {
          primera.scrollIntoView({
            behavior: "smooth",
            block: "center",
          });
        }
      }
    });
  }

  // --- 2️⃣ Buscar en otras páginas ---
  if (!encontrada && !esRedireccion) {
    for (const [nombreArchivo, textosPagina] of Object.entries(textos)) {
      if (nombreArchivo === paginaActual) continue;

      const coincide = textosPagina.some((t) =>
        t.toLowerCase().includes(palabra)
      );

      if (coincide) {
        const rutaFinal =
          nombreArchivo === "index.html"
            ? "/"
            : "/" + nombreArchivo.replace(".html", "");

        window.location.href = `${rutaFinal}?buscar=${encodeURIComponent(
          palabra
        )}`;
        return;
      }
    }

    mensaje.textContent = `No se encontró: "${palabra}"`;
  }

  return encontrada;
}

// ----------------------------------
// Esperar a que el contenido esté estable
// ----------------------------------
function esperarContenidoEstableYBuscar(palabra, paginaActual) {
  const contenedores = document.querySelectorAll(".contenido, #contenido");
  if (!contenedores.length) return;

  let timeout;

  const observer = new MutationObserver(() => {
    clearTimeout(timeout);

    timeout = setTimeout(() => {
      observer.disconnect();
      buscarPalabra(palabra, paginaActual, true);
    }, 100);
  });

  contenedores.forEach((c) => {
    observer.observe(c, {
      childList: true,
      subtree: true,
      characterData: true,
    });
  });

  // fallback por si no hay mutaciones
  setTimeout(() => {
    observer.disconnect();
    buscarPalabra(palabra, paginaActual, true);
  }, 500);
}

// ----------------------------------
// Evento submit
// ----------------------------------
form.addEventListener("submit", (e) => {
  e.preventDefault();

  const palabra = buscador.value.trim();
  if (!palabra) {
    mensaje.textContent = "Escribe algo para buscar.";
    return;
  }

  const paginaActual = window.location.pathname.split("/").pop();
  buscarPalabra(palabra, paginaActual);
});

// ----------------------------------
// Carga con parámetros URL
// ----------------------------------
window.addEventListener("DOMContentLoaded", () => {
  const params = new URLSearchParams(window.location.search);
  const palabraABuscar = params.get("buscar");

  if (palabraABuscar) {
    buscador.value = palabraABuscar;
    const paginaActual = window.location.pathname.split("/").pop();
    esperarContenidoEstableYBuscar(palabraABuscar, paginaActual);
  }
});
