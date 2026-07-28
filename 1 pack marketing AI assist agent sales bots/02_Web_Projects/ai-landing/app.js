// NeuralPack.ai — логика: навигация, табы, ROI (часы), квиз, Telegram

const TG_BOT_TOKEN = '6240637727:AAGZsu3ZOAinWoAJwTP11eJJv2M4qzCtx_g';
const TG_CHAT_ID   = '888005446';

// ── Навигация ──────────────────────────────────────────────
const navbar = document.getElementById('navbar');
window.addEventListener('scroll', () => {
  if (navbar) navbar.classList.toggle('scrolled', window.scrollY > 40);
});

const burger = document.getElementById('burger');
if (burger) {
  burger.addEventListener('click', () => {
    const navLinks = document.querySelector('.nav-links');
    const open = navLinks.style.display === 'flex';
    navLinks.style.cssText = open ? '' : `
      display:flex; flex-direction:column; position:fixed;
      top:64px; left:0; right:0; z-index:999;
      background:rgba(3,7,18,.97); padding:16px 24px;
      backdrop-filter:blur(20px); border-bottom:1px solid rgba(255,255,255,.08);
    `;
  });
}

// ── Табы услуг ─────────────────────────────────────────────
document.querySelectorAll('.tab-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
    document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));
    btn.classList.add('active');
    document.getElementById('tab-' + btn.dataset.tab)?.classList.add('active');
  });
});

// ── ROI Калькулятор (на основе часов) ─────────────────────
const roiHours = document.getElementById('roi-hours');
const roiRate  = document.getElementById('roi-rate');
let selectedEff   = 0.75;

function fmt(n) { return n.toLocaleString('ru-RU') + ' ₸'; }

function calcRoi() {
  if (!roiHours || !roiRate) return;
  const hours = parseInt(roiHours.value);      // часов/неделю
  const rate  = parseInt(roiRate.value);        // ₸/час
  const eff   = selectedEff;

  const hoursFreed  = Math.round(hours * eff);             // ч/нед освобождается
  const monthlySave = Math.round(hours * 4.3 * rate * eff); // ₸/мес
  const annualSave  = monthlySave * 12;
  const equiv       = (hoursFreed / 40).toFixed(1);        // эквивалент FTE

  document.getElementById('roi-hours-val').textContent  = hours + ' ч';
  document.getElementById('roi-rate-val').textContent   = rate.toLocaleString('ru-RU') + ' ₸';
  document.getElementById('roi-monthly').textContent    = fmt(monthlySave);
  document.getElementById('roi-annual').textContent     = fmt(annualSave);
  document.getElementById('roi-hours-freed').textContent = hoursFreed + ' ч/нед';
  document.getElementById('roi-equiv').textContent      = equiv + ' шт. ед.';

  // Формула в шапке
  document.getElementById('rf-hours').textContent  = hours + 'ч';
  document.getElementById('rf-rate').textContent   = rate.toLocaleString('ru-RU') + '₸';
  document.getElementById('rf-eff').textContent    = Math.round(eff * 100) + '%';
  document.getElementById('rf-result').textContent = fmt(monthlySave);
}

if (roiHours) roiHours.addEventListener('input', calcRoi);
if (roiRate) roiRate.addEventListener('input', calcRoi);

document.querySelectorAll('.roi-type-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    document.querySelectorAll('.roi-type-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    selectedEff = parseFloat(btn.dataset.eff);
    calcRoi();
  });
});

calcRoi();

// ── SaaS счётчики ──────────────────────────────────────────
function animateCounter(el) {
  const target = parseInt(el.dataset.target);
  const start  = performance.now();
  const dur    = 1500;
  const step   = now => {
    const p = Math.min((now - start) / dur, 1);
    el.textContent = Math.round(target * (1 - Math.pow(1 - p, 3))).toLocaleString('ru-RU');
    if (p < 1) requestAnimationFrame(step);
  };
  requestAnimationFrame(step);
}

new IntersectionObserver((entries) => {
  entries.forEach(e => {
    if (e.isIntersecting) {
      e.target.querySelectorAll('.sm-num').forEach(animateCounter);
      // Убираем обсервер чтобы не анимировать повторно
      e.target.classList.add('animated');
    }
  });
}, { threshold: 0.3 }).observe(document.querySelector('.saas-metrics') || document.body);

// ── Анимация карточек при скролле ─────────────────────────
const styleEl = document.createElement('style');
styleEl.textContent = '.anim-card.visible { opacity: 1 !important; transform: translateY(0) !important; }';
document.head.appendChild(styleEl);

const cardObserver = new IntersectionObserver(entries => {
  entries.forEach(e => { if (e.isIntersecting) e.target.classList.add('visible'); });
}, { threshold: 0.1 });

document.querySelectorAll('.value-card, .problem-card, .ai-emp-card').forEach(el => {
  el.classList.add('anim-card');
  el.style.cssText += 'opacity:0; transform:translateY(20px); transition:opacity .5s ease, transform .5s ease;';
  cardObserver.observe(el);
});

// ── КВИЗ ──────────────────────────────────────────────────
const TOTAL_STEPS = 4;
let currentStep = 1;

function goToStep(n) {
  document.querySelectorAll('.quiz-step').forEach(s => s.classList.remove('active'));
  const target = document.querySelector(`.quiz-step[data-step="${n}"]`);
  if (target) {
    target.classList.add('active');
    currentStep = n;
  }
  const pct = (n / TOTAL_STEPS) * 100;
  document.getElementById('quiz-fill').style.width = pct + '%';
  document.getElementById('quiz-step-label').textContent = `Шаг ${n} из ${TOTAL_STEPS}`;
}

// Кнопки «Далее»
document.querySelectorAll('.quiz-next').forEach(btn => {
  btn.addEventListener('click', () => {
    const next = parseInt(btn.dataset.next);
    // Для шагов с радио-кнопками — проверяем выбор
    const step = btn.closest('.quiz-step');
    const radios = step.querySelectorAll('input[type="radio"]');
    if (radios.length) {
      const chosen = [...radios].some(r => r.checked);
      if (!chosen) {
        step.querySelector('.quiz-options').style.outline = '2px solid var(--accent-blue)';
        step.querySelector('.quiz-options').style.borderRadius = '8px';
        setTimeout(() => { step.querySelector('.quiz-options').style.outline = ''; }, 800);
        return;
      }
    }
    // Для шагов с чекбоксами (шаг 1)
    const checkboxes = step.querySelectorAll('input[type="checkbox"][name="pain"]');
    if (checkboxes.length) {
      const chosen = [...checkboxes].some(c => c.checked);
      if (!chosen) {
        step.querySelector('.quiz-options').style.outline = '2px solid var(--accent-blue)';
        step.querySelector('.quiz-options').style.borderRadius = '8px';
        setTimeout(() => { step.querySelector('.quiz-options').style.outline = ''; }, 800);
        return;
      }
    }
    goToStep(next);
  });
});

// Кнопки «Назад»
document.querySelectorAll('.quiz-back').forEach(btn => {
  btn.addEventListener('click', () => goToStep(parseInt(btn.dataset.back)));
});

// ── Отправка формы в Telegram ─────────────────────────────
async function sendToTelegram(data) {
  const text = [
    '🎯 <b>Новая заявка — NeuralPack.ai</b>',
    '',
    `👤 <b>Имя:</b> ${data.name}`,
    `📞 <b>Контакт:</b> ${data.phone}`,
    data.company ? `📝 <b>Задача:</b> ${data.company}` : '',
    '',
    `🛠 <b>Что делегируем:</b>\n${data.pains || '—'}`,
    `🏢 <b>Ниша:</b> ${data.niche || '—'}`,
    `👥 <b>Заявки/день:</b> ${data.leads_vol || '—'}`,
    '',
    `⏰ ${new Date().toLocaleString('ru-RU', { timeZone: 'Asia/Almaty' })}`,
  ].filter(Boolean).join('\n');

  const res = await fetch(`https://api.telegram.org/bot${TG_BOT_TOKEN}/sendMessage`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ chat_id: TG_CHAT_ID, text, parse_mode: 'HTML' }),
  });
  if (!res.ok) throw new Error('TG error ' + res.status);
}

const form       = document.getElementById('lead-form');
const submitBtn  = document.getElementById('submit-btn');
const btnText    = document.getElementById('btn-text');
const btnLoader  = document.getElementById('btn-loader');
const quizBody   = document.getElementById('quiz-body');
const formSuccess = document.getElementById('form-success');
const formError  = document.getElementById('form-error');

if (form) {
  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    formError.classList.add('hidden');
    btnText.classList.add('hidden');
    btnLoader.classList.remove('hidden');
    submitBtn.disabled = true;

    // Собираем ответы квиза
    const pains = [...document.querySelectorAll('input[name="pain"]:checked')]
      .map(i => '• ' + i.value).join('\n');
    const niche = document.querySelector('input[name="team_size"]:checked')?.value || '';
    const leadsVol   = document.querySelector('input[name="budget"]:checked')?.value || '';

    const data = {
      name:      form.name.value.trim(),
      phone:     form.phone.value.trim(),
      company:   form.company.value.trim(), // Используем поле company как описание задачи
      pains,
      niche,
      leads_vol: leadsVol,
    };

    try {
      await sendToTelegram(data);
      quizBody.classList.add('hidden');
      formSuccess.classList.remove('hidden');
    } catch (err) {
      console.error(err);
      formError.classList.remove('hidden');
      btnText.classList.remove('hidden');
      btnLoader.classList.add('hidden');
      submitBtn.disabled = false;
    }
  });
}
