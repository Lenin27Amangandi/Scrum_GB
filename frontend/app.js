// HU-01: Catálogo de Laboratorios EPN
// Obtiene los laboratorios desde la API de Python y los muestra como tarjetas.

const catalogo = document.getElementById("catalogo");
const resumen = document.getElementById("resumen");

// Evita inyección de HTML con datos del CSV
function escapar(texto) {
    const div = document.createElement("div");
    div.textContent = texto;
    return div.innerHTML;
}

function crearTarjeta(lab) {
    const equipos = lab.equipos
        .map(e => `<li><span>${escapar(e.nombre)}</span><span class="cantidad">${e.cantidad}</span></li>`)
        .join("");

    return `
        <article class="tarjeta ${escapar(lab.tipo.toLowerCase())}">
            <div class="tarjeta-cabecera">
                <h3>${escapar(lab.nombre)}</h3>
                <span class="etiqueta">${escapar(lab.tipo)}</span>
            </div>
            <ul class="datos">
                <li><span class="clave">Edificio:</span><span>${escapar(lab.edificio)}</span></li>
                <li><span class="clave">Facultad:</span><span>${escapar(lab.facultad)}</span></li>
                <li><span class="clave">Capacidad:</span><span class="capacidad">${lab.capacidad} personas</span></li>
            </ul>
            <div class="equipos">
                <h4>Equipos disponibles</h4>
                <ul>${equipos || "<li>Sin equipos registrados</li>"}</ul>
            </div>
        </article>`;
}

async function cargarLaboratorios() {
    try {
        const respuesta = await fetch("/api/laboratorios");
        if (!respuesta.ok) throw new Error(`HTTP ${respuesta.status}`);
        const laboratorios = await respuesta.json();

        if (laboratorios.length === 0) {
            resumen.textContent = "";
            catalogo.innerHTML = `<p class="mensaje">No hay laboratorios registrados.</p>`;
            return;
        }

        resumen.textContent = `${laboratorios.length} laboratorios disponibles. Revisa su capacidad y equipamiento para elegir.`;
        catalogo.innerHTML = laboratorios.map(crearTarjeta).join("");
    } catch (error) {
        console.error("Error al cargar laboratorios:", error);
        resumen.textContent = "";
        catalogo.innerHTML = `<p class="mensaje error">No se pudo cargar el catálogo. Verifica que el servidor esté corriendo.</p>`;
    }
}

cargarLaboratorios();

