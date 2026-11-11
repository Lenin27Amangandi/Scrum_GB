import { STATES, createSchedule, initialSlots } from './schedule.js';

const schedule = createSchedule(initialSlots);
const list = document.querySelector('#schedule');
const announcement = document.querySelector('#announcement');
const rows = new Map();

for (const slot of schedule.getSlots()) {
  const row = document.createElement('li');
  row.className = 'slot';
  row.dataset.state = slot.state;
  const time = document.createElement('h3');
  time.textContent = slot.time;
  const badge = document.createElement('span');
  badge.className = 'badge';
  badge.textContent = STATES[slot.state].label;
  const label = document.createElement('label');
  label.htmlFor = `state-${slot.id}`;
  label.textContent = `Estado de ${slot.time}`;
  const select = document.createElement('select');
  select.id = label.htmlFor;
  for (const [value, state] of Object.entries(STATES)) {
    const option = document.createElement('option');
    option.value = value;
    option.textContent = state.label;
    select.append(option);
  }
  select.value = slot.state;
  select.addEventListener('change', () => schedule.setState(slot.id, select.value));
  row.append(time, badge, label, select);
  rows.set(slot.id, { row, badge, select });
  list.append(row);
}

schedule.subscribe(slot => {
  const { row, badge, select } = rows.get(slot.id);
  row.dataset.state = slot.state;
  badge.textContent = STATES[slot.state].label;
  select.value = slot.state;
  announcement.textContent = `${slot.time}: ${STATES[slot.state].label}`;
});
