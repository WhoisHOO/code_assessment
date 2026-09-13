'use strict';

/* Code Assessment Study UI — vanilla JS, talks to the local quiz.server API. */

let DATA = null;            // /api/bootstrap payload
const qById = new Map();    // question id -> question
const cById = new Map();    // card id -> card
const $view = document.getElementById('view');

/* ---------- helpers ---------- */

async function api(path, opts) {
  const res = await fetch(path, opts);
  const body = await res.json();
  if (!res.ok) throw new Error(body.error || res.statusText);
  return body;
}

function post(path, payload) {
  return api(path, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
}

function el(tag, attrs = {}, ...children) {
  const node = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs)) {
    if (k === 'class') node.className = v;
    else if (k === 'html') node.innerHTML = v;
    else if (k.startsWith('on')) node.addEventListener(k.slice(2), v);
    else node.setAttribute(k, v);
  }
  for (const c of children) if (c !== null && c !== undefined) node.append(c);
  return node;
}

function escapeHtml(s) {
  return s.replace(/&/g, '&amp;').replace(/</g, '&lt;')
          .replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}

function shuffle(arr) {
  const a = arr.slice();
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [a[i], a[j]] = [a[j], a[i]];
  }
  return a;
}

function todayIso() {
  const d = new Date();
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-` +
         `${String(d.getDate()).padStart(2, '0')}`;
}

/* Tiny renderer for the controlled markdown used in problems/*.md. */
function renderMd(md) {
  const parts = md.split('```');
  let html = '';
  for (let i = 0; i < parts.length; i++) {
    if (i % 2 === 1) {
      let code = parts[i];
      const nl = code.indexOf('\n');
      if (nl >= 0) code = code.slice(nl + 1); // drop the language tag line
      html += `<pre class="code"><code>${escapeHtml(code.replace(/\n$/, ''))}</code></pre>`;
    } else {
      html += renderMdBlocks(parts[i]);
    }
  }
  return html;
}

function renderMdBlocks(text) {
  let html = '';
  let para = [];
  let list = null;
  const inline = (s) => escapeHtml(s)
    .replace(/`([^`]+)`/g, '<code>$1</code>')
    .replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
  const flushPara = () => {
    if (para.length) { html += `<p>${inline(para.join(' '))}</p>`; para = []; }
  };
  const flushList = () => {
    if (list) {
      html += `<ul>${list.map((li) => `<li>${inline(li)}</li>`).join('')}</ul>`;
      list = null;
    }
  };
  for (const line of text.split('\n')) {
    const t = line.trim();
    if (!t) { flushPara(); flushList(); continue; }
    const heading = t.match(/^(#{2,4})\s+(.*)/);
    if (heading) {
      flushPara(); flushList();
      const level = heading[1].length;
      html += `<h${level}>${inline(heading[2])}</h${level}>`;
    } else if (t.startsWith('- ')) {
      flushPara();
      (list = list || []).push(t.slice(2));
    } else {
      flushList();
      para.push(t);
    }
  }
  flushPara(); flushList();
  return html;
}

async function recordReview(key, correct) {
  const res = await post('/api/review', { key, correct });
  DATA.state.items[key] = res.entry;
}

function itemCategory(key) {
  if (key.startsWith('q:')) {
    const q = qById.get(key.slice(2));
    return q ? `${q.language}/${q.topic}` : key;
  }
  const c = cById.get(key.slice(2));
  return c ? `card:${c.category}` : key;
}

/* ---------- reusable widgets ---------- */

function mcqPanel(question, done) {
  const panel = el('div', { class: 'panel' });
  panel.append(el('div', { class: 'meta-line' },
    `${question.language} | ${question.topic} | ${question.difficulty}`));
  panel.append(el('p', {}, question.question));
  if (question.code) panel.append(el('pre', { class: 'qcode' }, question.code));

  const order = shuffle([...question.choices.keys()]);
  const correctText = question.choices[question.answer_index];
  const box = el('div', { class: 'choices' });
  const buttons = order.map((origIdx, pos) => {
    const label = String.fromCharCode(97 + pos);
    const btn = el('button', {
      onclick: async () => {
        const correct = question.choices[origIdx] === correctText;
        buttons.forEach((b) => { b.disabled = true; });
        buttons.forEach((b) => {
          if (b.dataset.text === correctText) b.classList.add('correct');
        });
        if (!correct) btn.classList.add('wrong');
        const fb = el('div', { class: `feedback ${correct ? 'good' : 'bad'}` },
          el('strong', {}, correct ? 'Correct!' : 'Incorrect.'),
          el('div', { class: 'explain' }, question.explanation));
        panel.append(fb);
        try { await recordReview(`q:${question.id}`, correct); } catch (e) { /* offline edit races */ }
        panel.append(el('div', { class: 'btn-row' },
          el('button', { class: 'btn primary', onclick: () => done(correct) }, 'Next')));
      },
    }, `${label}) ${question.choices[origIdx]}`);
    btn.dataset.text = question.choices[origIdx];
    return btn;
  });
  buttons.forEach((b) => box.append(b));
  panel.append(box);
  return panel;
}

function flashcardPanel(card, done) {
  const panel = el('div', { class: 'panel' });
  panel.append(el('div', { class: 'meta-line' }, `flashcard | ${card.category}`));
  const front = el('div', { class: 'card-face' },
    el('div', {},
      el('div', {}, card.trigger),
      el('div', { class: 'muted small' }, '(click to reveal the pattern)')));
  front.addEventListener('click', () => {
    front.remove();
    const back = el('div', { class: 'card-face card-back' },
      el('div', {},
        el('div', {}, el('strong', {}, card.pattern)),
        card.notes ? el('div', { class: 'notes' }, card.notes) : null));
    const grade = async (correct) => {
      try { await recordReview(`c:${card.id}`, correct); } catch (e) { /* ignore */ }
      done(correct);
    };
    panel.append(back, el('div', { class: 'btn-row' },
      el('button', { class: 'btn bad', onclick: () => grade(false) }, 'Again'),
      el('button', { class: 'btn good', onclick: () => grade(true) }, 'Got it')));
  });
  panel.append(front);
  return panel;
}

/* Runs a mixed session over item keys (q:*, c:*). */
function runSession(keys, { title, onFinish }) {
  let index = 0;
  let correctCount = 0;
  const total = keys.length;

  const step = () => {
    $view.replaceChildren();
    if (index >= total) {
      $view.append(el('div', { class: 'panel' },
        el('h2', {}, 'Session complete'),
        el('p', {}, `Score: ${correctCount}/${total}. `,
          el('span', { class: 'muted' },
            'Missed items stay due and will come back.')),
        el('div', { class: 'btn-row' },
          el('button', { class: 'btn primary', onclick: onFinish }, 'Done'))));
      return;
    }
    const key = keys[index];
    $view.append(el('h2', {}, title),
      el('div', { class: 'progress' }, `${index + 1} / ${total}`));
    const done = (correct) => { if (correct) correctCount += 1; index += 1; step(); };
    if (key.startsWith('q:')) {
      $view.append(mcqPanel(qById.get(key.slice(2)), done));
    } else {
      $view.append(flashcardPanel(cById.get(key.slice(2)), done));
    }
  };
  step();
}

/* ---------- tabs ---------- */

function renderDaily() {
  const { due, new: fresh } = DATA.daily;
  const keys = [...due, ...fresh].filter((k) =>
    (k.startsWith('q:') && qById.has(k.slice(2))) ||
    (k.startsWith('c:') && cById.has(k.slice(2))));
  $view.replaceChildren(el('h2', {}, 'Daily review'));
  if (!keys.length) {
    $view.append(el('div', { class: 'panel' },
      el('p', {}, 'All caught up - nothing due today.'),
      el('p', { class: 'muted small' },
        'New items are capped per day so the backlog stays manageable. ' +
        'Come back tomorrow, or practice a timed problem instead.')));
    return;
  }
  $view.append(el('div', { class: 'panel' },
    el('p', {}, `${due.length} due review(s) and ${fresh.length} new item(s) today.`),
    el('div', { class: 'btn-row' },
      el('button', {
        class: 'btn primary',
        onclick: () => runSession(shuffle(keys), {
          title: 'Daily review',
          onFinish: () => location.reload(),
        }),
      }, `Start (${keys.length} items)`))));
}

function renderFlashcards() {
  const categories = ['all', ...new Set(DATA.cards.map((c) => c.category))];
  let active = 'all';

  const draw = () => {
    const cards = DATA.cards.filter((c) => active === 'all' || c.category === active);
    $view.replaceChildren(el('h2', {}, 'Flashcards'));
    const chips = el('div', { class: 'chips' });
    categories.forEach((cat) => chips.append(el('button', {
      class: cat === active ? 'active' : '',
      onclick: () => { active = cat; draw(); },
    }, cat)));
    $view.append(chips);

    const list = el('div', { class: 'panel' });
    cards.forEach((card) => {
      const entry = DATA.state.items[`c:${card.id}`];
      list.append(el('div', { class: 'item-row', onclick: () => {
        runSession([`c:${card.id}`], { title: 'Flashcard', onFinish: renderFlashcards });
      } },
        el('span', { class: 'title' }, card.trigger),
        el('span', { class: 'tag' }, card.category),
        el('span', { class: 'right' }, entry ? `box ${entry.box}` : 'new')));
    });
    $view.append(list, el('div', { class: 'btn-row' },
      el('button', {
        class: 'btn primary',
        onclick: () => runSession(shuffle(cards.map((c) => `c:${c.id}`)), {
          title: 'Flashcards',
          onFinish: renderFlashcards,
        }),
      }, `Study these ${cards.length} card(s)`)));
  };
  draw();
}

function renderQuiz() {
  $view.replaceChildren(el('h2', {}, 'Quiz'));
  const langSel = el('select', { class: 'select' },
    el('option', { value: 'all' }, 'all languages'),
    el('option', { value: 'python' }, 'python'),
    el('option', { value: 'java' }, 'java'));
  const countInput = el('input', { type: 'number', value: '10', min: '1', max: '50' });
  $view.append(el('div', { class: 'panel' },
    el('p', {}, 'Multiple-choice concept questions. Results feed the same ',
      'spaced-repetition boxes as the daily review.'),
    el('div', { class: 'btn-row' }, langSel, countInput,
      el('button', {
        class: 'btn primary',
        onclick: () => {
          const pool = DATA.questions.filter(
            (q) => langSel.value === 'all' || q.language === langSel.value);
          const picked = shuffle(pool).slice(0, Number(countInput.value) || 10);
          runSession(picked.map((q) => `q:${q.id}`),
            { title: 'Quiz', onFinish: renderQuiz });
        },
      }, 'Start'))));
}

function lastPostmortem(problemId) {
  const list = DATA.state.postmortems.filter((p) => p.problem_id === problemId);
  return list.length ? list[list.length - 1] : null;
}

function renderProblems() {
  $view.replaceChildren(el('h2', {}, 'Timed problems'));
  if (!DATA.problems.length) {
    $view.append(el('div', { class: 'panel' },
      el('p', {}, 'No problems yet - add markdown files under problems/<category>/.')));
    return;
  }
  const byCat = new Map();
  DATA.problems.forEach((p) => {
    if (!byCat.has(p.category)) byCat.set(p.category, []);
    byCat.get(p.category).push(p);
  });
  [...byCat.keys()].sort().forEach((cat) => {
    const panel = el('div', { class: 'panel' }, el('h3', {}, cat));
    byCat.get(cat).forEach((p) => {
      const pm = lastPostmortem(p.id);
      panel.append(el('div', { class: 'item-row', onclick: () => renderProblemDetail(p.id) },
        el('span', { class: 'title' }, p.title),
        el('span', { class: 'tag' }, `${p.difficulty} - target ${p.time_target_min} min`),
        el('span', { class: 'right' }, pm ? `last: ${pm.outcome} (${pm.date})` : 'not attempted')));
    });
    $view.append(panel);
  });
}

async function renderProblemDetail(id) {
  $view.replaceChildren(el('p', { class: 'muted' }, 'Loading…'));
  const { meta, statement, solution } = await api(`/api/problem?id=${encodeURIComponent(id)}`);

  $view.replaceChildren();
  $view.append(
    el('div', { class: 'btn-row' },
      el('button', { class: 'btn', onclick: renderProblems }, '< Back')),
    el('h2', {}, meta.title),
    el('div', { class: 'meta-line' },
      `${meta.category} | ${meta.difficulty} | target ${meta.time_target_min} min`),
    el('div', { class: 'panel', html: renderMd(statement) }));

  // Timer + reveal. The trigger/pattern line is a spoiler, so it only shows
  // after the reveal.
  let seconds = 0;
  let intervalId = null;
  const timerLabel = el('span', { class: 'timer' }, '00:00');
  const tick = () => {
    seconds += 1;
    const mm = String(Math.floor(seconds / 60)).padStart(2, '0');
    const ss = String(seconds % 60).padStart(2, '0');
    timerLabel.textContent = `${mm}:${ss}`;
    if (seconds > meta.time_target_min * 60) timerLabel.classList.add('over');
  };
  const startBtn = el('button', {
    class: 'btn primary',
    onclick: () => {
      if (intervalId) { clearInterval(intervalId); intervalId = null; startBtn.textContent = 'Resume'; }
      else { intervalId = setInterval(tick, 1000); startBtn.textContent = 'Pause'; }
    },
  }, 'Start timer');

  const timerPanel = el('div', { class: 'panel' },
    el('div', { class: 'btn-row' }, timerLabel, startBtn,
      el('button', { class: 'btn', onclick: reveal }, 'Reveal solution & log')));
  $view.append(timerPanel);

  function reveal() {
    if (intervalId) clearInterval(intervalId);
    timerPanel.remove();

    $view.append(
      el('div', { class: 'panel' },
        el('p', {}, el('strong', {}, 'Trigger: '), meta.trigger),
        el('p', {}, el('strong', {}, 'Pattern: '), meta.pattern)),
      el('div', { class: 'panel', html: renderMd(solution) }));

    const radios = (name, options) => {
      const row = el('div', { class: 'radio-row' });
      options.forEach(([value, label], i) => row.append(el('label', {},
        el('input', { type: 'radio', name, value, ...(i === 0 ? { checked: '' } : {}) }),
        label)));
      return row;
    };
    const outcomeRow = radios('outcome', [
      ['solved', 'Solved'], ['partial', 'Partial'], ['failed', 'Failed']]);
    const causeRow = radios('cause', [
      ['none', 'No issue'],
      ['misread', 'Misread the statement'],
      ['unknown_pattern', "Didn't know the pattern"],
      ['slow_recall', 'Knew it, recalled slowly'],
      ['implementation_bug', 'Implementation bug']]);
    const minutesInput = el('input', {
      type: 'number', min: '0', step: '0.5',
      value: (seconds / 60).toFixed(1),
    });

    const form = el('div', { class: 'panel' },
      el('h3', {}, 'Post-mortem'),
      el('div', { class: 'form-group' }, el('div', { class: 'label' }, 'Outcome'), outcomeRow),
      el('div', { class: 'form-group' }, el('div', { class: 'label' }, 'Main cause'), causeRow),
      el('div', { class: 'form-group' },
        el('div', { class: 'label' }, 'Minutes spent'), minutesInput),
      el('div', { class: 'btn-row' },
        el('button', {
          class: 'btn primary',
          onclick: async () => {
            const pick = (name) =>
              form.querySelector(`input[name=${name}]:checked`).value;
            const res = await post('/api/postmortem', {
              problem_id: id,
              outcome: pick('outcome'),
              cause: pick('cause'),
              minutes: Number(minutesInput.value) || 0,
            });
            DATA.state.postmortems.push(res.entry);
            renderProblems();
          },
        }, 'Save & back')));
    $view.append(form);
  }
}

function renderStats() {
  const items = DATA.state.items;
  const keys = Object.keys(items);
  const today = todayIso();
  const dueNow = keys.filter((k) => items[k].due <= today).length;
  const totalCatalog = DATA.questions.length + DATA.cards.length;

  $view.replaceChildren(el('h2', {}, 'Stats'));

  // Box distribution
  const boxCounts = [0, 0, 0, 0, 0, 0];
  keys.forEach((k) => { boxCounts[items[k].box] += 1; });
  const bars = el('div', { class: 'bars' });
  const maxCount = Math.max(1, ...boxCounts, totalCatalog - keys.length);
  const addBar = (label, count) => {
    bars.append(el('span', { class: 'small' }, label),
      el('div', { class: 'bar' },
        el('i', { style: `width:${(100 * count) / maxCount}%` })),
      el('span', { class: 'small muted' }, String(count)));
  };
  addBar('unseen', totalCatalog - keys.length);
  for (let box = 1; box <= 5; box++) addBar(`box ${box}`, boxCounts[box]);
  $view.append(el('div', { class: 'panel' },
    el('h3', {}, 'Spaced repetition'),
    el('p', { class: 'muted small' },
      `${keys.length}/${totalCatalog} items in rotation - ${dueNow} due today. ` +
      'Higher boxes = longer review intervals (1/2/4/8/16 days).'),
    bars));

  // Accuracy by category
  const agg = new Map();
  keys.forEach((k) => {
    const cat = itemCategory(k);
    const a = agg.get(cat) || { seen: 0, correct: 0 };
    a.seen += items[k].seen;
    a.correct += items[k].correct;
    agg.set(cat, a);
  });
  const accTable = el('table', { class: 'plain' },
    el('tr', {}, el('th', {}, 'category'), el('th', {}, 'answered'),
      el('th', {}, 'correct'), el('th', {}, 'accuracy')));
  [...agg.keys()].sort().forEach((cat) => {
    const a = agg.get(cat);
    accTable.append(el('tr', {},
      el('td', {}, cat), el('td', {}, String(a.seen)),
      el('td', {}, String(a.correct)),
      el('td', {}, a.seen ? `${Math.round((100 * a.correct) / a.seen)}%` : '-')));
  });
  $view.append(el('div', { class: 'panel' },
    el('h3', {}, 'Accuracy by category'),
    agg.size ? accTable : el('p', { class: 'muted' }, 'No reviews yet.')));

  // Post-mortems
  const pms = DATA.state.postmortems;
  const causeCounts = new Map();
  pms.forEach((p) => causeCounts.set(p.cause, (causeCounts.get(p.cause) || 0) + 1));
  const causePanel = el('div', { class: 'panel' }, el('h3', {}, 'Problem post-mortems'));
  if (!pms.length) {
    causePanel.append(el('p', { class: 'muted' },
      'No timed sessions logged yet. The cause column is the important one: ' +
      'it tells you WHAT to train.'));
  } else {
    const causeTable = el('table', { class: 'plain' },
      el('tr', {}, el('th', {}, 'cause'), el('th', {}, 'count')));
    [...causeCounts.entries()].sort((a, b) => b[1] - a[1]).forEach(([cause, n]) =>
      causeTable.append(el('tr', {}, el('td', {}, cause), el('td', {}, String(n)))));
    const recent = el('table', { class: 'plain' },
      el('tr', {}, el('th', {}, 'date'), el('th', {}, 'problem'),
        el('th', {}, 'outcome'), el('th', {}, 'cause'), el('th', {}, 'min')));
    pms.slice(-10).reverse().forEach((p) => {
      const meta = DATA.problems.find((x) => x.id === p.problem_id);
      recent.append(el('tr', {},
        el('td', {}, p.date), el('td', {}, meta ? meta.title : p.problem_id),
        el('td', {}, p.outcome), el('td', {}, p.cause),
        el('td', {}, String(p.minutes))));
    });
    causePanel.append(causeTable, el('h3', {}, 'Recent sessions'), recent);
  }
  $view.append(causePanel);
}

/* ---------- boot ---------- */

const TABS = {
  daily: renderDaily,
  flashcards: renderFlashcards,
  quiz: renderQuiz,
  problems: renderProblems,
  stats: renderStats,
};

document.getElementById('tabs').addEventListener('click', (ev) => {
  const btn = ev.target.closest('button');
  if (!btn) return;
  document.querySelectorAll('#tabs button').forEach((b) =>
    b.classList.toggle('active', b === btn));
  TABS[btn.dataset.tab]();
});

(async function init() {
  try {
    DATA = await api('/api/bootstrap');
  } catch (err) {
    $view.replaceChildren(el('div', { class: 'panel' },
      el('p', {}, `Failed to load data: ${err.message}`)));
    return;
  }
  DATA.questions.forEach((q) => qById.set(q.id, q));
  DATA.cards.forEach((c) => cById.set(c.id, c));
  const { due, new: fresh } = DATA.daily;
  document.getElementById('due-badge').textContent =
    `${due.length} due | ${fresh.length} new today`;
  renderDaily();
})();
