const fecha = document.querySelector('#fecha');
const laboratorio = document.querySelector('#laboratorio');
const facultad = document.querySelector('#facultad');
const horario = document.querySelector('#filtro-horario');
const lista = document.querySelector('#franjas');
const mensaje = document.querySelector('#estado-carga');
const resumen = document.querySelector('#resumen-filtro');
const tarjetas = [...document.querySelectorAll('details[data-laboratorio]')];
const opciones = [...laboratorio.options].map(option => option.cloneNode(true));
const labels = { disponible: 'Disponible', ocupado: 'Ocupado', mantenimiento: 'Mantenimiento' };
let version = 0;
function pintar(destino, franjas) {
  destino.replaceChildren(...franjas.filter(franja => !horario.value || franja.time === horario.value).map(franja => {
    const item = document.createElement('li');
    item.dataset.state = franja.state;
    item.textContent = `${franja.time}: ${labels[franja.state]}`;
    return item;
  }));
}
function filtrarFacultad() {
  const anterior = laboratorio.value;
  laboratorio.replaceChildren(...opciones.filter(option => !facultad.value || option.dataset.facultad === facultad.value).map(option => option.cloneNode(true)));
  if ([...laboratorio.options].some(option => option.value === anterior)) laboratorio.value = anterior;
  for (const tarjeta of tarjetas) tarjeta.hidden = Boolean(facultad.value && tarjeta.dataset.facultad !== facultad.value);
  resumen.textContent = `${tarjetas.filter(tarjeta => !tarjeta.hidden).length} laboratorios encontrados.`;
  actualizar();
}
async function actualizar() {
  const actual = ++version;
  lista.replaceChildren();
  for (const tarjeta of tarjetas) tarjeta.querySelector('.disponibilidad-lab').replaceChildren();
  if (!fecha.value) { mensaje.textContent = 'Selecciona una fecha para consultar disponibilidad.'; return; }
  mensaje.textContent = 'Consultando disponibilidad…';
  const visibles = tarjetas.filter(tarjeta => !tarjeta.hidden);
  try {
    const resultados = await Promise.all(visibles.map(async tarjeta => {
      const response = await fetch('/api/franjas?' + new URLSearchParams({fecha: fecha.value, laboratorio: tarjeta.dataset.laboratorio}), {cache: 'no-store'});
      if (!response.ok) throw new Error();
      return { tarjeta, franjas: await response.json() };
    }));
    if (actual !== version) return;
    for (const {tarjeta, franjas} of resultados) {
      pintar(tarjeta.querySelector('.disponibilidad-lab'), franjas);
      if (tarjeta.dataset.laboratorio === laboratorio.value) pintar(lista, franjas);
    }
    mensaje.textContent = 'Disponibilidad actualizada. Se consulta cada 5 segundos.';
  } catch { if (actual === version) mensaje.textContent = 'No se pudo consultar la disponibilidad. Se reintentará.'; }
}
facultad.addEventListener('change', filtrarFacultad);
horario.addEventListener('change', () => {
  if (horario.value) {
    const [inicio, fin] = horario.value.split(' – ');
    document.querySelector('#hora_inicio').value = inicio;
    document.querySelector('#hora_fin').value = fin;
  }
  actualizar();
});
fecha.addEventListener('change', actualizar);
laboratorio.addEventListener('change', actualizar);
setInterval(actualizar, 5000);
filtrarFacultad();
