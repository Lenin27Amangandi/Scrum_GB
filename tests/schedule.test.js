import test from 'node:test';
import assert from 'node:assert/strict';
import { STATES, createSchedule, initialSlots } from '../src/schedule.js';

test('los datos iniciales incluyen los tres estados de la leyenda', () => {
  assert.deepEqual(new Set(initialSlots.map(slot => slot.state)), new Set(Object.keys(STATES)));
});

test('todas las transiciones notifican inmediatamente sin modificar otras franjas', () => {
  for (const from of Object.keys(STATES)) {
    for (const to of Object.keys(STATES)) {
      const schedule = createSchedule([{ id: 'a', state: from }, { id: 'b', state: 'ocupado' }]);
      const events = [];
      schedule.subscribe(slot => events.push(slot));
      schedule.setState('a', to);
      assert.equal(schedule.getSlots()[0].state, to);
      assert.equal(schedule.getSlots()[1].state, 'ocupado');
      assert.deepEqual(events, from === to ? [] : [{ id: 'a', state: to }]);
    }
  }
});

test('rechaza estados y franjas inválidos sin alterar el horario', () => {
  const schedule = createSchedule(initialSlots);
  assert.throws(() => schedule.setState('09', 'otro'), RangeError);
  assert.throws(() => schedule.setState('otro', 'disponible'), RangeError);
  assert.throws(() => createSchedule([{ id: 'a', state: 'otro' }]), RangeError);
  assert.deepEqual(schedule.getSlots(), initialSlots);
});

test('protege los datos contra modificaciones externas y permite cancelar suscripciones', () => {
  const schedule = createSchedule(initialSlots);
  schedule.getSlots()[0].state = 'ocupado';
  assert.equal(schedule.getSlots()[0].state, 'disponible');
  let count = 0;
  const unsubscribe = schedule.subscribe(slot => { count++; slot.state = 'mantenimiento'; });
  schedule.setState('09', 'ocupado');
  assert.equal(schedule.getSlots()[0].state, 'ocupado');
  unsubscribe();
  schedule.setState('09', 'disponible');
  assert.equal(count, 1);
});
