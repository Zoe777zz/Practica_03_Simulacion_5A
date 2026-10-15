const scenarioConfig = {
  scenario_1: { name: 'Escenario 1', lambda: 2.0, mu: 3.0, rho: 2 / 3 },
  scenario_2: { name: 'Escenario 2', lambda: 2.5, mu: 3.0, rho: 2.5 / 3 },
  scenario_3: { name: 'Escenario 3', lambda: 2.9, mu: 3.0, rho: 2.9 / 3 }
};

const personIcons = ['🧍', '👩', '👨', '🧑', '👩‍🦱', '👨‍🦱', '👩‍🦰', '👨‍🦰'];

let lastData = null;
let animationRunning = true;
let waitingQueue = [];
let currentService = null;
let nextPersonId = 1;
let arrivalTimeout = null;
let serviceTimeout = null;
let exitTimeout = null;

const queueSlots = [...document.querySelectorAll('.queue-slot')];
const queueCount = document.getElementById('animQueueCount');
const serviceLight = document.getElementById('serviceLight');
const serviceText = document.getElementById('serviceText');
const serviceBooth = document.getElementById('serviceBooth');
const serviceCustomer = document.getElementById('serviceCustomer');
const arrivalPerson = document.getElementById('arrivalPerson');
const exitPerson = document.getElementById('exitPerson');
const overflowQueue = document.getElementById('overflowQueue');

function toast(message) {
  const el = document.getElementById('toast');
  el.textContent = message;
  el.classList.add('show');
  setTimeout(() => el.classList.remove('show'), 2600);
}

function fmt(value) {
  return Number(value).toFixed(4);
}

function updateAnimationLabels(key) {
  const s = scenarioConfig[key];
  document.getElementById('animLambda').textContent = s.lambda.toFixed(1);
  document.getElementById('animMu').textContent = s.mu.toFixed(1);
  document.getElementById('animRho').textContent = s.rho.toFixed(3);
}

function personForId(id) {
  return personIcons[(id - 1) % personIcons.length];
}

function randomExponential(meanMs) {
  const u = Math.max(0.0001, Math.random());
  return -Math.log(u) * meanMs;
}

function clamp(value, min, max) {
  return Math.max(min, Math.min(max, value));
}

function pulseArrival(icon) {
  arrivalPerson.textContent = icon;
  arrivalPerson.classList.remove('show');
  void arrivalPerson.offsetWidth;
  arrivalPerson.classList.add('show');
}

function pulseExit(icon) {
  exitPerson.textContent = icon;
  exitPerson.classList.remove('show');
  void exitPerson.offsetWidth;
  exitPerson.classList.add('show');
}

function renderQueue() {
  // El cliente más antiguo va en la posición 1, junto al servidor.
  const visible = waitingQueue.slice(0, 6);

  queueSlots.forEach(slot => {
    slot.classList.remove('occupied');
    slot.querySelector('.slot-person').textContent = '';
  });

  visible.forEach((person, index) => {
    const slotNumber = index + 1;
    const slot = document.querySelector(`.queue-slot[data-slot="${slotNumber}"]`);
    if (!slot) return;
    slot.classList.add('occupied');
    slot.querySelector('.slot-person').textContent = person.icon;
  });

  const overflow = Math.max(0, waitingQueue.length - 6);
  if (overflow > 0) {
    overflowQueue.textContent = `+${overflow} esperando`;
    overflowQueue.classList.remove('hidden');
  } else {
    overflowQueue.classList.add('hidden');
  }

  queueCount.textContent = String(waitingQueue.length);
}

function renderService() {
  if (currentService) {
    serviceCustomer.textContent = currentService.icon;
    serviceCustomer.classList.remove('empty');
    serviceCustomer.classList.add('active');
    serviceLight.classList.add('busy');
    serviceBooth.classList.add('busy');
    serviceText.textContent = `Atendiendo cliente #${currentService.id}`;
  } else {
    serviceCustomer.textContent = '—';
    serviceCustomer.classList.add('empty');
    serviceCustomer.classList.remove('active');
    serviceLight.classList.remove('busy');
    serviceBooth.classList.remove('busy');
    serviceText.textContent = 'Servidor libre';
  }
}

function renderAnimation() {
  renderQueue();
  renderService();
}

function spawnPerson() {
  if (!animationRunning) return;

  const person = {
    id: nextPersonId++,
    icon: personForId(nextPersonId - 1)
  };

  pulseArrival(person.icon);
  waitingQueue.push(person);

  // Límite visual para que una racha larga no haga crecer memoria indefinidamente.
  if (waitingQueue.length > 30) waitingQueue = waitingQueue.slice(-30);

  renderAnimation();
}

function finishService(person) {
  if (!person) return;
  pulseExit(person.icon);
  currentService = null;
  renderAnimation();

  // Si hay alguien esperando, el servidor puede iniciar la siguiente atención.
  if (animationRunning && waitingQueue.length > 0) {
    window.setTimeout(startServiceIfPossible, 180);
  }
}

function startServiceIfPossible() {
  if (!animationRunning || currentService || waitingQueue.length === 0) return;

  currentService = waitingQueue.shift();
  renderAnimation();

  const key = document.getElementById('animationScenario').value;
  const s = scenarioConfig[key];
  const meanServiceMs = 4500 / s.mu;
  const duration = clamp(randomExponential(meanServiceMs), 650, 2900);

  clearTimeout(serviceTimeout);
  serviceTimeout = window.setTimeout(() => finishService(currentService), duration);
}

function scheduleNextArrival() {
  clearTimeout(arrivalTimeout);
  if (!animationRunning) return;

  const key = document.getElementById('animationScenario').value;
  const s = scenarioConfig[key];
  const meanArrivalMs = 4500 / s.lambda;
  const delay = clamp(randomExponential(meanArrivalMs), 650, 3400);

  arrivalTimeout = window.setTimeout(() => {
    spawnPerson();
    startServiceIfPossible();
    scheduleNextArrival();
  }, delay);
}

function restartAnimation() {
  clearTimeout(arrivalTimeout);
  clearTimeout(serviceTimeout);
  clearTimeout(exitTimeout);

  waitingQueue = [];
  currentService = null;
  nextPersonId = 1;

  arrivalPerson.classList.remove('show');
  exitPerson.classList.remove('show');

  const key = document.getElementById('animationScenario').value;
  updateAnimationLabels(key);
  renderAnimation();

  if (!animationRunning) return;

  // Estado inicial didáctico: se muestran varios clientes para que el
  // flujo FIFO se entienda desde el primer instante. Después la dinámica
  // continúa con llegadas y servicios aleatorios.
  for (let i = 0; i < 4; i += 1) {
    const person = { id: nextPersonId++, icon: personForId(nextPersonId - 1) };
    waitingQueue.push(person);
    if (i === 3) pulseArrival(person.icon);
  }
  renderAnimation();

  window.setTimeout(startServiceIfPossible, 420);
  scheduleNextArrival();
}

function updateChart() {
  if (!lastData) return;
  const key = document.getElementById('chartScenario').value;
  const item = lastData.details[key];
  if (!item) return;
  const image = document.getElementById('chartImage');
  image.src = item.chart_image;
  image.classList.remove('hidden');
  document.getElementById('chartPlaceholder').classList.add('hidden');
}

function renderResults(data) {
  const body = document.getElementById('resultsBody');
  body.innerHTML = data.summaries.map(row => `
    <tr>
      <td><strong>${row.scenario}</strong><br><small>${row.condition}</small></td>
      <td>${fmt(row.rho)}</td>
      <td>${fmt(row.L)}</td>
      <td>${fmt(row.Lq)}</td>
      <td>${fmt(row.W)}</td>
      <td>${fmt(row.Wq)}</td>
      <td>${fmt(row.average_wait_sim)}</td>
      <td>${fmt(row.average_queue_sim)}</td>
    </tr>`).join('');
  document.getElementById('resultBadge').textContent = `${data.repetitions} repetición(es)`;
  document.getElementById('seedInfo').textContent = data.seed_message;
}

async function runSimulation() {
  const button = document.getElementById('runBtn');
  const repetitions = Number(document.getElementById('repetitions').value);
  if (!Number.isInteger(repetitions) || repetitions < 1 || repetitions > 50) {
    toast('N debe estar entre 1 y 50.');
    return;
  }

  button.disabled = true;
  button.textContent = 'Simulando…';
  try {
    const response = await fetch('/api/simulate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ repetitions })
    });
    const payload = await response.json();
    if (!payload.ok) throw new Error(payload.error || 'No se pudo ejecutar la simulación.');
    lastData = payload.data;
    renderResults(lastData);
    updateChart();
    toast('Simulación completada correctamente.');
  } catch (error) {
    toast(error.message);
  } finally {
    button.disabled = false;
    button.textContent = 'Ejecutar simulación';
  }
}

document.getElementById('runBtn').addEventListener('click', runSimulation);
document.getElementById('chartScenario').addEventListener('change', updateChart);
document.getElementById('animationScenario').addEventListener('change', restartAnimation);
document.getElementById('toggleAnimation').addEventListener('click', event => {
  animationRunning = !animationRunning;
  event.currentTarget.textContent = animationRunning ? 'Pausar' : 'Reanudar';

  if (!animationRunning) {
    clearTimeout(arrivalTimeout);
    clearTimeout(serviceTimeout);
    serviceText.textContent = 'Animación pausada';
    return;
  }

  restartAnimation();
});

restartAnimation();
