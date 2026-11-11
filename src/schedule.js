export const STATES = Object.freeze({
  disponible: Object.freeze({ label: 'Disponible' }),
  ocupado: Object.freeze({ label: 'Ocupado' }),
  mantenimiento: Object.freeze({ label: 'Mantenimiento' }),
});

export function validateState(state) {
  if (!Object.hasOwn(STATES, state)) throw new RangeError(`Estado desconocido: ${state}`);
  return state;
}

export function createSchedule(initialSlots) {
  const slots = new Map();
  for (const slot of initialSlots) {
    validateState(slot.state);
    if (slots.has(slot.id)) throw new Error(`Franja duplicada: ${slot.id}`);
    slots.set(slot.id, { ...slot });
  }
  const listeners = new Set();
  return {
    getSlots: () => [...slots.values()].map(slot => ({ ...slot })),
    setState(id, state) {
      validateState(state);
      const slot = slots.get(id);
      if (!slot) throw new RangeError(`Franja desconocida: ${id}`);
      if (slot.state === state) return;
      const updated = { ...slot, state };
      slots.set(id, updated);
      for (const listener of listeners) listener({ ...updated });
    },
    subscribe(listener) {
      listeners.add(listener);
      return () => listeners.delete(listener);
    },
  };
}

// Datos de demostración hasta que el proyecto disponga de una fuente de horarios.
export const initialSlots = [
  { id: '09', time: '09:00 – 10:00', state: 'disponible' },
  { id: '10', time: '10:00 – 11:00', state: 'ocupado' },
  { id: '11', time: '11:00 – 12:00', state: 'mantenimiento' },
  { id: '12', time: '12:00 – 13:00', state: 'disponible' },
];
