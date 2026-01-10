const form = document.querySelector("form");
const buscador = document.getElementById("buscador");
const mensaje = document.getElementById("mensaje-busqueda");

// En Flask los archivos estáticos se sirven en /static/... — usar ruta absoluta evita 404
const jsonRuta = "/static/js/textos.json";

let textos = {};

// Carga del JSON
fetch(jsonRuta)
  .then((res) => res.json())
  .then((data) => (textos = data))
  .catch((err) => console.error("Error cargando JSON:", err));

function buscarPalabra(palabra, paginaActual, esRedireccion = false) {
  palabra = palabra.toLowerCase();
  let encontrada = false;

  // Limpiamos el mensaje siempre que se inicia una búsqueda
  mensaje.textContent = "";

  // Normalizar nombre de la página (para Flask: '/consolas' -> 'consolas.html')
  if (paginaActual === "" || paginaActual === "index.html") {
    paginaActual = "index.html";
  } else if (!paginaActual.endsWith(".html")) {
    paginaActual = paginaActual + ".html";
  }

  // --- 1️⃣ Buscar en la página actual ---
  if (textos[paginaActual]) {
    const bloques = document.querySelectorAll(".contenido, #contenido");
    bloques.forEach((b) => {
      const original = b.textContent;
      const regex = new RegExp(`(${palabra})`, "gi");

      if (original.toLowerCase().includes(palabra)) {
        b.innerHTML = original.replace(
          regex,
          `<span class="resaltado">$1</span>`
        );
        encontrada = true;
        const primera = b.querySelector(".resaltado");
        if (primera)
          primera.scrollIntoView({ behavior: "smooth", block: "center" });
      } else {
        b.innerHTML = original;
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
        // Mapear nombreArchivo a ruta del servidor Flask: index.html -> '/', consolas.html -> '/consolas', etc.
        let rutaFinal;
        if (nombreArchivo === "index.html") {
          rutaFinal = "/";
        } else {
          rutaFinal = "/" + nombreArchivo.replace(".html", "");
        }

        window.location.href = `${rutaFinal}?buscar=${encodeURIComponent(
          palabra
        )}`;
        return;
      }
    }

    // Si llegamos aquí, no estaba en ninguna parte
    mensaje.textContent = `No se encontró: "${palabra}"`;
  }
  return encontrada;
}

// --- 3️⃣ Evento Submit ---
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

// --- 4️⃣ Carga con parámetros URL ---
window.addEventListener("DOMContentLoaded", () => {
  const params = new URLSearchParams(window.location.search);
  const palabraABuscar = params.get("buscar");

  if (palabraABuscar) {
    buscador.value = palabraABuscar;
    const paginaActual = window.location.pathname.split("/").pop();
    setTimeout(() => {
      buscarPalabra(palabraABuscar, paginaActual, true);
    }, 100);
  }
});
