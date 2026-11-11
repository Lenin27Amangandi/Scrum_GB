const fecha = document.querySelector('#fecha');
const laboratorio = document.querySelector('#laboratorio');
const lista = document.querySelector('#franjas');
const mensaje = document.querySelector('#estado-carga');
const labels = { disponible: 'Disponible', ocupado: 'Ocupado', mantenimiento: 'Mantenimiento' };
let version = 0;
async function actualizar() {
  const actual = ++version;
  if (!fecha.value) { lista.replaceChildren(); mensaje.textContent = 'Selecciona una fecha para consultar disponibilidad.'; return; }
  try {
    const response = await fetch('/api/franjas?' + new URLSearchParams({fecha: fecha.value, laboratorio: laboratorio.value}), {cache: 'no-store'});
    if (!response.ok) throw new Error();
    const franjas = await response.json();
    if (actual !== version) return;
    lista.replaceChildren(...franjas.map(franja => {
      const item = document.createElement('li');
      item.dataset.state = franja.state;
      item.textContent = `${franja.time}: ${labels[franja.state]}`;
      return item;
    }));
    mensaje.textContent = 'Disponibilidad actualizada. Se consulta cada 5 segundos.';
  } catch { if (actual === version) { lista.replaceChildren(); mensaje.textContent = 'No se pudo consultar la disponibilidad. Se reintentará.'; } }
}
fecha.addEventListener('change', actualizar);
laboratorio.addEventListener('change', actualizar);
setInterval(actualizar, 5000);
actualizar();
