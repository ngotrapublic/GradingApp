const Q = { cls: '', classInfo: null, me: null, paper: null, result: null, explain: null, preread: null };

function quizMath(s) {
  let t = String(s ?? '');
  t = t.replace(/(^|[^A-Za-z0-9.])(\d+(?:\.\d+)?)[eE]([+-]?\d+)(?![A-Za-z0-9])/g, (_, p, a, b) => `${p}${a} * 10^${b}`);
  // Older banks use compact symbols, while newer entries can use explicit underscores.
  t = t.replace(/\bn(?=VT\b)/g, 'n ')
    .replace(/\b(VDS|ID),(sat)\b/g, (_, base, qualifier) => `${base[0]}_${base.slice(1)},${qualifier}`)
    .replace(/\b(ID|IS|IF|IR|IB|IC|IE|NA|ND|VGS|VDS|VBS|VSB|VBE|VCE|VCB|VCC|VDD|VT|VA|VR|VF|VOV|Vbi|ni|Cj|Cox|CG|rd|ro|gm|tox|fT|Emax|RL|RDS)\b/g,
      (_, symbol) => `${symbol[0]}_${symbol.slice(1)}`)
    .replace(/ΦBn\b/g, 'Φ_Bn');
  t = esc(t);
  t = t.replace(/(^|[^A-Za-z0-9_])([A-Za-zμσαβθφψΦεΩ∂]{1,6})_([A-Za-z0-9α-ω]+(?:,[A-Za-z0-9α-ω]+)*)(?![A-Za-z0-9_])/g,
    (_, p, base, sub) => `${p}${base}<sub>${sub}</sub>`);
  t = t.replace(/\^\{([^}]+)\}/g, '<sup>$1</sup>');
  t = t.replace(/\^(-?\d+)/g, '<sup>$1</sup>');
  t = t.replace(/[²]/g, '<sup>2</sup>').replace(/[³]/g, '<sup>3</sup>');
  return t;
}

function qsCls() {
  try { return new URLSearchParams(location.search).get('cls') || ''; } catch (e) { return ''; }
}
Q.cls = qsCls();

function isPhoneOrTablet() {
  const ua = navigator.userAgent || '';
  if (/Android|webOS|iPhone|iPod|iPad|Tablet|Kindle|Silk|BlackBerry|IEMobile|Opera Mini|Mobile|CriOS|FxiOS/i.test(ua)) return true;
  if (/Macintosh/i.test(ua) && navigator.maxTouchPoints > 1) return true;
  if (/Windows NT/i.test(ua) && navigator.maxTouchPoints > 1 && /Touch/i.test(ua)) return true;
  return false;
}

function renderDeviceBlock(app) {
  app.innerHTML = headBar() + `<main><div class="card" style="padding:14px">
    <h2>${T('Phone or tablet only', 'Chỉ điện thoại / máy tính bảng')}</h2>
    <p class="muted">${T('This review quiz cannot be opened on a computer. Open the link on your phone or tablet.', 'Quiz ôn tập không mở trên máy tính. Hãy mở link bằng điện thoại hoặc máy tính bảng.')}</p>
  </div></main>`;
  bindLangToggle(app);
}

function quizHeaders(extra) {
  const h = Object.assign({ 'X-Quiz-Client': isPhoneOrTablet() ? 'tablet' : 'desktop' }, extra || {});
  return h;
}

async function post(path, body) {
  const r = await fetch(path, {
    method: 'POST',
    headers: quizHeaders({ 'Content-Type': 'application/json' }),
    body: JSON.stringify(body),
  });
  const j = await r.json().catch(() => ({}));
  if (!r.ok) {
    toast((LANG === 'vi' && j.error_vi) || j.error || T('Error', 'Lỗi'));
    if (r.status === 401) { Q.me = null; render(); }
    return null;
  }
  return j;
}
async function get(path) {
  const r = await fetch(path, { headers: quizHeaders() });
  if (r.status === 401) return null;
  const j = await r.json().catch(() => ({}));
  if (!r.ok) { toast((LANG === 'vi' && j.error_vi) || j.error || T('Error', 'Lỗi')); return null; }
  return j;
}

function formatExplainBody(body) {
  const items = Array.isArray(body)
    ? body.map(x => String(x || '').trim()).filter(Boolean)
    : String(body || '').split(/\n+/).map(x => x.replace(/^[-•*]\s*/, '').trim()).filter(Boolean);
  if (!items.length) return '';
  if (items.length === 1 && !Array.isArray(body) && !/\n/.test(String(body || ''))) {
    return `<div class="explain">${quizMath(items[0])}</div>`;
  }
  return `<ul class="explain-bullets">${items.map(t => `<li>${quizMath(t)}</li>`).join('')}</ul>`;
}

async function reload() {
  Q.paper = null;
  Q.result = null;
  Q.explain = null;
  Q.preread = null;
  Q.cls = qsCls() || Q.cls;
  Q.classInfo = Q.cls ? await get('/api/public/quiz/class?cls=' + encodeURIComponent(Q.cls)) : null;
  Q.me = await get('/api/public/quiz/me');
  if (Q.me && Q.cls && String(Q.me.cls) !== String(Q.cls)) {
    await post('/api/public/quiz/logout', {});
    Q.me = null;
  }
  if (Q.me) {
    const left = await flushAbandonedAttempt();
    if (left) {
      Q.result = left;
      render();
      return;
    }
  } else {
    clearActiveAttempt();
  }
  render();
}

async function signOut() {
  disarmLeaveGuard();
  await post('/api/public/quiz/logout', {});
  Q.me = null; Q.paper = null; Q.result = null; Q.explain = null; Q.preread = null;
  render();
}

function headBar() {
  const outBtn = Q.me ? `<button class="qrbtn" id="out">${T('Sign out', 'Thoát')}</button>` : '';
  const title = (Q.me && Q.me.courseName) || (Q.classInfo && Q.classInfo.courseName) || T('Review Quiz', 'Quiz ôn tập');
  return `<header><div class="row"><h1>${esc(title)}</h1>${langToggle()}${outBtn}</div></header>`;
}

function blockCopy(root) {
  const stop = e => {
    if (e.target && (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA')) return;
    e.preventDefault();
    return false;
  };
  ['copy', 'cut', 'contextmenu', 'selectstart', 'dragstart'].forEach(ev => root.addEventListener(ev, stop));
  root.addEventListener('keydown', e => {
    if (e.target && (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA')) return;
    if ((e.ctrlKey || e.metaKey) && ['c', 'C', 'x', 'X', 'a', 'A'].includes(e.key)) e.preventDefault();
  });
}

let leaveArmed = false;
let leaveDone = false;
const ACTIVE_ATTEMPT_KEY = 'quiz_active_attempt';

function saveActiveAttempt(P) {
  if (!P || !P.attempt_id) return;
  try {
    sessionStorage.setItem(ACTIVE_ATTEMPT_KEY, JSON.stringify({
      attempt_id: P.attempt_id,
      slug: P.slug,
      total: P.total,
      pass_score: P.pass_score,
    }));
  } catch (e) {}
}

function clearActiveAttempt() {
  try { sessionStorage.removeItem(ACTIVE_ATTEMPT_KEY); } catch (e) {}
}

function readActiveAttempt() {
  try {
    const raw = sessionStorage.getItem(ACTIVE_ATTEMPT_KEY);
    return raw ? JSON.parse(raw) : null;
  } catch (e) { return null; }
}

function postLeaveAttempt(attemptId) {
  const body = JSON.stringify({ attempt_id: attemptId, answers: {}, left_app: true });
  const headers = quizHeaders({ 'Content-Type': 'application/json' });
  try {
    if (navigator.sendBeacon) {
      const ok = navigator.sendBeacon(
        '/api/public/quiz/submit',
        new Blob([body], { type: 'application/json' })
      );
      if (ok) return Promise.resolve({ ok: true, beacon: true });
    }
  } catch (e) {}
  return fetch('/api/public/quiz/submit', {
    method: 'POST',
    headers,
    body,
    keepalive: true,
    credentials: 'same-origin',
  }).then(r => r.json().catch(() => ({}))).catch(() => null);
}

async function flushAbandonedAttempt() {
  const saved = readActiveAttempt();
  if (!saved || !saved.attempt_id) return null;
  clearActiveAttempt();
  try {
    const r = await fetch('/api/public/quiz/submit', {
      method: 'POST',
      headers: quizHeaders({ 'Content-Type': 'application/json' }),
      body: JSON.stringify({ attempt_id: saved.attempt_id, answers: {}, left_app: true }),
      credentials: 'same-origin',
    });
    const j = await r.json().catch(() => ({}));
    return j && j.left_app ? j : null;
  } catch (e) {
    return null;
  }
}

function disarmLeaveGuard() {
  leaveArmed = false;
  document.removeEventListener('visibilitychange', onLeaveApp);
  window.removeEventListener('pagehide', onLeaveApp);
  window.removeEventListener('beforeunload', onLeaveApp);
}

function armLeaveGuard() {
  disarmLeaveGuard();
  leaveDone = false;
  leaveArmed = true;
  document.addEventListener('visibilitychange', onLeaveApp);
  window.addEventListener('pagehide', onLeaveApp);
  window.addEventListener('beforeunload', onLeaveApp);
}

function onLeaveApp(ev) {
  if (!leaveArmed || leaveDone || !Q.paper) return;
  if (ev && ev.type === 'visibilitychange' && !document.hidden) return;
  leaveDone = true;
  const P = Q.paper;
  if (P && P._hintTimer) clearInterval(P._hintTimer);
  closeHintPopup();
  disarmLeaveGuard();
  postLeaveAttempt(P.attempt_id).then(j => {
    clearActiveAttempt();
    if (!j || j.beacon || !Q.result || !Q.result.left_app) return;
    Q.result.leave_count = j.leave_count;
    Q.result.cooldown_sec = j.cooldown_sec || 0;
    Q.result.penalty_note = (LANG === 'vi' && j.penalty_note_vi) || j.penalty_note || '';
    render();
  });
  Q.paper = null;
  Q.result = {
    passed: false,
    score: 0,
    total: P.total,
    pass_score: P.pass_score,
    slug: P.slug,
    left_app: true,
    leave_count: null,
    cooldown_sec: 0,
    penalty_note: T('Attempt ended because you left / reloaded this page.', 'Bài bị hủy vì bạn thoát app hoặc reload trang.'),
  };
  if (ev && ev.type !== 'beforeunload' && ev.type !== 'pagehide') render();
}

function renderIdentify(app) {
  if (!Q.cls || !Q.classInfo) {
    app.innerHTML = headBar() + `<main><div class="card" style="padding:14px">
      <h2>${T('Missing class link', 'Thiếu link lớp')}</h2>
      <p class="muted">${T('Open the QR / link from your lecturer (…/quiz/?cls=…).', 'Mở QR hoặc link giảng viên phát (…/quiz/?cls=…).')}</p>
    </div></main>`;
    bindLangToggle(app);
    return;
  }
  const C = Q.classInfo;
  app.innerHTML = headBar() + `<main><div class="login card">
    <h2>${T('Enter your details', 'Nhập thông tin')}</h2>
    <p class="muted"><b>${esc(C.name)}</b> · ${esc(C.term)}</p>
    <p class="muted">${T('First time: fill both. Returning after exit: name OR student ID is enough.', 'Lần đầu: nhập cả hai. Thoát rồi vào lại: chỉ cần đúng tên hoặc MSSV.')}</p>
    <label class="fl">${T('Full name', 'Họ và tên')}<input id="name" autocomplete="name" autocapitalize="words"></label>
    <label class="fl">${T('Student ID', 'MSSV')}<input id="sid" autocomplete="username" autocapitalize="characters"></label>
    <button class="big on" id="go">${T('Continue', 'Tiếp tục')}</button>
  </div></main>`;
  bindLangToggle(app);
  const go = async () => {
    const name = $('#name').value.trim();
    const sid = $('#sid').value.trim();
    if (!name && !sid) return toast(T('Enter name or student ID.', 'Nhập họ tên hoặc MSSV.'));
    if (!await post('/api/public/quiz/identify', { cls: +Q.cls, name, sid })) return;
    reload();
  };
  $('#go').onclick = go;
  app.querySelectorAll('input').forEach(i => { i.onkeydown = e => { if (e.key === 'Enter') go(); }; });
  $('#name').focus();
}

function renderHome(app) {
  const I = Q.me;
  let h = headBar() + `<main><div class="card who"><div class="nm">${esc(I.name)}</div>
    <div class="sub">${esc(I.sid)} · ${esc(I.className)}</div></div>
    <p class="muted">${T('Read all theory pages once for each day. Then take the quiz and review the explanations before attendance.', 'Đọc hết lý thuyết một lần cho mỗi ngày. Sau đó làm quiz và xem giải thích trước khi điểm danh.')}</p>`;
  if (!I.sets.length) h += `<p class="muted">${T('No open quiz right now.', 'Hiện chưa có quiz nào mở.')}</p>`;
  I.sets.forEach(s => {
    let badge, btn;
    if (s.attendance_done) {
      badge = `<span class="badge ok">${T('Attendance done', 'Đã điểm danh')} ${s.best}/${s.n_pick}</span>`;
      btn = `<p class="muted">${T('You may leave.', 'Bạn có thể ra về.')}</p>`;
    } else if (s.expired) {
      badge = `<span class="badge warn">${T('Session ended', 'Phiên đã kết thúc')}</span>`;
      btn = '';
    } else if (s.needs_explanations) {
      badge = `<span class="badge warn">${T('Finish answer review', 'Cần xem lại đáp án')}</span>`;
      btn = `<p class="muted">${T('Read every question’s answer before attendance is recorded. Result is shown only at the end.', 'Phải xem hết đáp án từng câu mới điểm danh. Kết quả chỉ hiện ở cuối.')}</p>
        <button class="big on" data-explain="${esc(s.slug)}">${T('Continue answer review', 'Tiếp tục xem đáp án')}</button>`;
    } else if (s.passed) {
      badge = `<span class="badge ok">${T('Passed', 'Đạt')} ${s.best}/${s.n_pick}</span>`;
      btn = `<p class="muted">${T('Done.', 'Đã xong.')}</p>`;
    } else {
      badge = s.tries
        ? `<span class="badge warn">${T('Best', 'Cao nhất')} ${s.best}/${s.n_pick}</span>`
        : `<span class="badge">${T('Not tried', 'Chưa làm')}</span>`;
      const cool = Number(s.cooldown_sec) || 0;
      if (cool > 0) {
        const mins = Math.max(1, Math.ceil(cool / 60));
        btn = `<p class="muted" data-cool="${esc(s.slug)}"><b>${T(
          `Wait ${mins} min — leave penalty (${s.leave_count || ''}×; 1st = 1 min, then ×2).`,
          `Chờ ${mins} phút — phạt thoát app (${s.leave_count || ''} lần; lần 1 = 1 phút, sau ×2).`
        )}</b></p>
        <button class="big" disabled>${T(`Wait ${mins} min`, `Chờ ${mins} phút`)}</button>`;
      } else {
        btn = `<button class="big on" data-read="${esc(s.slug)}">${s.theory_done ? T('Start quiz', 'Vào quiz') : T('Read theory, then quiz', 'Đọc lý thuyết rồi làm quiz')}</button>`;
      }
    }
    h += `<div class="card qcard"><div class="stem">${esc(s.title)}</div>
      <div class="muted">${badge} · ${T('tries', 'lần')}: ${s.tries} · pass ${s.pass_score}/${s.n_pick} · ${T('bank', 'ngân hàng')} ${s.n}</div>
      ${s.session_minutes ? `<p class="muted">${T(
        `Submit when ready. The session closes at minute ${s.session_minutes.max}.`,
        `Nộp quiz khi làm xong. Phiên đóng ở phút ${s.session_minutes.max}.`)}</p>` : ''}
      ${btn}</div>`;
  });
  h += `<div class="btns"><button class="on" id="ref">${T('Refresh', 'Tải lại')}</button></div></main>`;
  app.innerHTML = h;
  bindLangToggle(app);
  const out = $('#out'); if (out) out.onclick = signOut;
  $('#ref').onclick = () => reload();
  app.querySelectorAll('[data-read]').forEach(b => b.onclick = () => beginPreRead(b.dataset.read));
  app.querySelectorAll('[data-explain]').forEach(b => b.onclick = () => resumeExplain(b.dataset.explain));
  const coolNeed = (I.sets || []).some(s => (Number(s.cooldown_sec) || 0) > 0);
  if (Q._coolTimer) clearInterval(Q._coolTimer);
  if (coolNeed) {
    Q._coolTimer = setInterval(() => {
      if (!Q.me) { clearInterval(Q._coolTimer); return; }
      reload();
    }, 15000);
  }
}

async function beginPreRead(slug) {
  const j = await post('/api/public/quiz/read_start', { slug });
  if (!j) return;
  if (j.skip || !(j.pages || []).length) {
    return startQuiz(slug);
  }
  Q.preread = {
    slug: j.slug,
    title: j.title,
    pages: j.pages,
    localTheoryTest: j.local_theory_test === true,
    sec: Number(j.sec_per_page) || 15,
    i: 0,
    unlockAt: Date.now() + (Number(j.sec_per_page) || 15) * 1000,
  };
  Q.paper = null;
  Q.result = null;
  Q.explain = null;
  render();
}

async function startQuiz(slug) {
  const j = await post('/api/public/quiz/start', { slug });
  if (!j) return false;
  j.startedAt = Date.now();
  j.deadline = j.seconds_remaining == null ? null : j.startedAt + j.seconds_remaining * 1000;
  j.hints_unlocked = !!j.hints_ready;
  j.hint_after_sec = Number(j.hint_after_sec) || 20 * 60;
  Q.preread = null;
  Q.paper = j;
  Q.result = null;
  Q.explain = null;
  saveActiveAttempt(j);
  render();
  return true;
}

function renderPreRead(app) {
  const R = Q.preread;
  if (!R) return renderHome(app);
  const n = R.pages.length;
  const page = R.pages[R.i];
  const last = R.i + 1 >= n;
  const img = page.image
    ? `<button type="button" class="theory-figure" id="openTheoryFigure" aria-label="${T('Enlarge figure', 'Phóng to hình')}">
        <img class="theory-img" src="${esc(page.image)}" alt="${esc(page.title || 'Theory figure')}">
      </button>
      <dialog class="theory-dialog" aria-label="${T('Theory figure', 'Hình lý thuyết')}">
        <form method="dialog"><button type="submit" class="big">${T('Close figure', 'Đóng hình')}</button></form>
        <img src="${esc(page.image)}" alt="${esc(page.title || 'Theory figure')}">
      </dialog>`
    : '';
  let h = headBar() + `<main class="no-copy">
    <p class="muted"><b>${T('Theory first', 'Đọc lý thuyết trước')}</b> — ${esc(R.title)}</p>
    <p class="muted">${T('Page', 'Trang')} ${R.i + 1} / ${n}. ${T('Read carefully (English). Next unlocks after the timer.', 'Đọc kỹ (tiếng Anh). Hết giờ mới bấm Tiếp.')}</p>
    <div class="card qcard">
      <div class="stem">${quizMath(page.title || '')}</div>
      <div class="theory-body">${formatExplainBody(page.body)}</div>
      ${img}
    </div>
    <p class="muted" id="readWait"></p>
    <button class="big on" id="readNext">${last ? T('Finish reading — start quiz', 'Xong đọc — bắt đầu quiz') : T('Next', 'Tiếp')}</button>
  </main>`;
  app.innerHTML = h;
  bindLangToggle(app);
  blockCopy(app.querySelector('main.no-copy') || app);
  const out = $('#out'); if (out) out.onclick = signOut;
  const figure = $('#openTheoryFigure');
  if (figure) figure.onclick = () => app.querySelector('.theory-dialog').showModal();
  const next = $('#readNext');
  const waitEl = $('#readWait');
  const label = last ? T('Finish reading — start quiz', 'Xong đọc — bắt đầu quiz') : T('Next', 'Tiếp');
  if (R._timer) clearInterval(R._timer);
  const tick = () => {
    if (!Q.preread || Q.preread !== R) { clearInterval(R._timer); return; }
    const left = Math.max(0, R.unlockAt - Date.now());
    const sec = Math.ceil(left / 1000);
    if (left <= 0) {
      clearInterval(R._timer);
      R._timer = null;
      waitEl.textContent = '';
      next.classList.remove('wait');
      next.textContent = label;
      return;
    }
    next.classList.add('wait');
    waitEl.textContent = T(`Next unlocks in ${sec}s — keep reading. Early tap adds +10s.`, `Còn ${sec}s mới bấm tiếp — hãy đọc. Bấm sớm +10s.`);
    next.textContent = T(`Wait ${sec}s`, `Chờ ${sec}s`);
  };
  R._timer = setInterval(tick, 200);
  tick();
  next.onclick = async () => {
    if (Date.now() < R.unlockAt) {
      R.unlockAt += 10000;
      if (!R._timer) R._timer = setInterval(tick, 200);
      tick();
      return;
    }
    if (R._timer) clearInterval(R._timer);
    if (!last) {
      R.i += 1;
      R.unlockAt = Date.now() + R.sec * 1000;
      render();
      return;
    }
    await finishPreRead(R);
  };
}

async function finishPreRead(R, skipForTest = false) {
  if (Q.preread !== R || R.finishing) return;
  R.finishing = true;
  const next = $('#readNext');
  if (next) next.disabled = true;
  try {
    const ok = await post('/api/public/quiz/read_done', {
      slug: R.slug, local_skip_theory: skipForTest,
    });
    if (!ok) return;
    if (R._timer) clearInterval(R._timer);
    if (!(await startQuiz(R.slug))) {
      Q.preread = null;
      await reload();
    }
  } finally {
    R.finishing = false;
    if (next) next.disabled = false;
  }
}

$('#app-ver').addEventListener('click', () => {
  const reading = Q.preread;
  if (!reading?.localTheoryTest || reading.finishing) return;
  reading.versionTaps = (reading.versionTaps || 0) + 1;
  if (reading.versionTaps !== 5) return;
  reading.versionTaps = 0;
  finishPreRead(reading, true);
});

function paperHintsOn() {
  const P = Q.paper;
  if (!P) return false;
  if (P.hints_unlocked) return true;
  const need = (Number(P.hint_after_sec) || 1200) * 1000;
  return Date.now() - (P.startedAt || Date.now()) >= need;
}

function unlockPaperHints(app) {
  const P = Q.paper;
  if (!P || P.hints_unlocked) return;
  P.hints_unlocked = true;
  app.querySelectorAll('.hintbulb').forEach(btn => {
    btn.disabled = false;
    btn.classList.add('on');
    btn.setAttribute('aria-disabled', 'false');
  });
  const banner = app.querySelector('#hintBanner');
  if (banner) banner.innerHTML = `<b>${T('Hints unlocked — tap the lightbulb on each question.', 'Đã mở gợi ý — bấm bóng đèn ở từng câu.')}</b>`;
}

function closeHintPopup() {
  const pop = document.getElementById('hintPop');
  if (pop) pop.remove();
}

function openHintPopup(text, qn) {
  closeHintPopup();
  const wrap = document.createElement('div');
  wrap.id = 'hintPop';
  wrap.className = 'hintpop';
  wrap.innerHTML = `<div class="hintpop-card" role="dialog" aria-modal="true">
    <div class="hintpop-hd"><span>💡 ${T('Hint', 'Gợi ý')} ${qn || ''}</span>
      <button type="button" class="hintpop-x" id="hintPopClose">×</button></div>
    <div class="hintpop-bd">${quizMath(text)}</div>
    <button type="button" class="big on" id="hintPopOk">${T('OK', 'OK')}</button>
  </div>`;
  document.body.appendChild(wrap);
  const close = () => closeHintPopup();
  wrap.onclick = e => { if (e.target === wrap) close(); };
  $('#hintPopClose').onclick = close;
  $('#hintPopOk').onclick = close;
}

async function resumeExplain(slug) {
  const j = await post('/api/public/quiz/review', { slug });
  if (!j) return;
  if (j.attendance_done) { toast(T('Attendance already recorded.', 'Đã điểm danh rồi.')); return reload(); }
  beginExplain(j);
}

function beginExplain(payload) {
  Q.result = null;
  Q.paper = null;
  Q.explain = {
    slug: payload.slug,
    score: payload.score,
    total: payload.total,
    pass_score: payload.pass_score,
    review: payload.review || [],
    followUp: payload.follow_up || [],
    followAnswers: {},
    finishAt: Date.now() + (payload.finish_wait_sec || 0) * 1000,
    deadline: payload.seconds_remaining == null ? null : Date.now() + payload.seconds_remaining * 1000,
    i: 0,
    unlockAt: Date.now() + 10000,
  };
  render();
}

function renderPaper(app) {
  const P = Q.paper;
  const hintsOn = paperHintsOn();
  P.hints_unlocked = hintsOn;
  const mins = Math.round((Number(P.hint_after_sec) || 1200) / 60);
  let h = headBar() + `<main class="no-copy"><h2>${esc(P.title)}</h2>
    <p class="muted">${T('Pass from', 'Đạt từ')} ${P.pass_score}/${P.total}. ${T('Your question order and choices are unique. Copying is disabled.', 'Thứ tự câu và đáp án của bạn là riêng. Không cho copy.')}</p>
    <p class="muted"><b>${T('Stay in this app. Switching away ends your attempt immediately.', 'Ở lại trong app này. Đổi sang app khác là hủy bài ngay.')}</b></p>
    ${P.deadline ? '<p class="muted" id="sessionClock"></p>' : ''}
    ${P.deadline ? '' : `<p class="muted" id="hintBanner">${hintsOn
      ? `<b>${T('Hints unlocked — tap the lightbulb on each question.', 'Đã mở gợi ý — bấm bóng đèn ở từng câu.')}</b>`
      : T(`Lightbulb unlocks after ${mins} min, after 5+ tries, or from attempt 4 if scores stay between 10 and 14.`, `Bóng đèn mở sau ${mins} phút, sau trên 5 lần thử, hoặc từ lần 4 nếu điểm cứ trong khoảng 10–14.`)}</p>`}`;
  P.questions.forEach((q, qi) => {
    const bulb = q.hint
      ? `<button type="button" class="hintbulb ${hintsOn ? 'on' : ''}" data-qid="${esc(q.id)}" data-qn="${qi + 1}"
          ${hintsOn ? '' : 'disabled'} aria-label="${T('Hint', 'Gợi ý')}">💡</button>`
      : '';
    h += `<div class="card qcard" data-qid="${esc(q.id)}" data-type="${esc(q.type || 'mcq')}">
      <div class="stemrow"><div class="stem">${qi + 1}. ${quizMath(q.stem)}</div>${bulb}</div>`;
    if ((q.type || 'mcq') === 'numeric') {
      h += `<label class="fl numans">${T('Your answer', 'Nhập đáp án')}
        <span class="numrow">
          <input inputmode="numeric" autocomplete="off" name="qm_${esc(q.id)}" placeholder="${T('integer', 'số nguyên')}">
          <span class="scale">* 10</span>
          <input class="exp" inputmode="text" autocomplete="off" name="qe_${esc(q.id)}" placeholder="${T('power', 'mũ')}">
          ${q.unit ? `<span class="unit">${quizMath(q.unit)}</span>` : ''}
        </span></label>
        <p class="muted">${T('Any integers OK — we check coeff × 10^power. Example for 2.59: 259 and −2 (or 2590 and −3).', 'Nhập số nguyên tự do — chấm theo hệ số × 10^mũ. Vd 2.59: 259 và −2 (hoặc 2590 và −3).')}</p>`;
    } else {
      (q.choices || []).forEach((c, ci) => {
        h += `<label><input type="radio" name="q_${esc(q.id)}" value="${ci}"> ${quizMath(c)}</label>`;
      });
    }
    h += `</div>`;
  });
  h += `<button class="big on" id="submit">${T('Submit', 'Nộp bài')}</button>
    <button class="big" id="cancel">${T('Cancel', 'Hủy')}</button></main>`;
  app.innerHTML = h;
  bindLangToggle(app);
  blockCopy(app.querySelector('main.no-copy') || app);
  const out = $('#out'); if (out) out.onclick = signOut;
  app.querySelectorAll('.qcard[data-type="mcq"] label').forEach(lab => {
    lab.onclick = () => {
      lab.parentElement.querySelectorAll('label').forEach(x => x.classList.remove('on'));
      lab.classList.add('on');
    };
  });
  const hintById = {};
  P.questions.forEach(q => { if (q.hint) hintById[q.id] = q.hint; });
  app.querySelectorAll('.hintbulb').forEach(btn => {
    btn.onclick = e => {
      e.preventDefault();
      e.stopPropagation();
      if (!paperHintsOn()) {
        toast(T('Hint still locked.', 'Gợi ý chưa mở.'));
        return;
      }
      openHintPopup(hintById[btn.dataset.qid] || '', btn.dataset.qn || '');
    };
  });
  if (P._hintTimer) clearInterval(P._hintTimer);
  if (!P.deadline && !hintsOn) {
    P._hintTimer = setInterval(() => {
      if (!Q.paper || Q.paper.attempt_id !== P.attempt_id) { clearInterval(P._hintTimer); return; }
      if (paperHintsOn()) {
        clearInterval(P._hintTimer);
        unlockPaperHints(app);
      }
    }, 5000);
  }
  armLeaveGuard();
  saveActiveAttempt(P);
  $('#cancel').onclick = () => {
    if (P._hintTimer) clearInterval(P._hintTimer);
    closeHintPopup();
    disarmLeaveGuard();
    leaveDone = true;
    clearActiveAttempt();
    Q.paper = null;
    render();
  };
  if (P.deadline) {
    watchReviewClock(P.deadline, (seconds) => {
      const clock = $('#sessionClock');
      if (!clock || Q.paper !== P) return false;
      clock.textContent = reviewTimeLabel(seconds);
      if (!seconds) {
        $('#submit').disabled = true;
        disarmLeaveGuard();
        clearActiveAttempt();
      }
      return true;
    });
  }
  $('#submit').onclick = async () => {
    const answers = {};
    let missing = 0;
    P.questions.forEach(q => {
      if ((q.type || 'mcq') === 'numeric') {
        const mInp = app.querySelector(`input[name="qm_${q.id}"]`);
        const eInp = app.querySelector(`input[name="qe_${q.id}"]`);
        const m = mInp ? mInp.value.trim() : '';
        const e = eInp ? eInp.value.trim() : '';
        if (!m || e === '') missing += 1;
        answers[q.id] = { m, e: e === '' ? '0' : e };
      } else {
        const sel = app.querySelector(`input[name="q_${q.id}"]:checked`);
        if (!sel) missing += 1;
        else answers[q.id] = +sel.value;
      }
    });
    if (missing && !confirm(T(`You left ${missing} unanswered. Submit anyway?`, `Còn ${missing} câu chưa trả lời. Vẫn nộp?`))) return;
    const btn = $('#submit'); btn.disabled = true;
    if (P._hintTimer) clearInterval(P._hintTimer);
    disarmLeaveGuard();
    leaveDone = true;
    const j = await post('/api/public/quiz/submit', { attempt_id: P.attempt_id, answers });
    btn.disabled = false;
    if (!j) {
      leaveDone = false;
      armLeaveGuard();
      return;
    }
    closeHintPopup();
    clearActiveAttempt();
    Q.paper = null;
    if (j.expired) {
      toast(T('The 60-minute review session has ended.', 'Phiên ôn tập 60 phút đã kết thúc.'));
      return reload();
    }
    if (j.needs_explanations && j.review) beginExplain(j);
    else { Q.result = j; render(); }
  };
}

function renderResult(app) {
  const R = Q.result;
  const pass = R.passed;
  let h = headBar() + `<main><div class="card result ${pass ? 'pass' : 'fail'}">
    <div>${pass ? T('Passed', 'Đạt') : T('Not passed — no attendance', 'Chưa đạt — chưa điểm danh')}</div>
    <div class="score">${R.score} / ${R.total}</div>
    <div class="muted">${T('Pass mark', 'Mốc đạt')}: ${R.pass_score}/${R.total}</div>`;
  if (R.left_app) {
    const note = R.penalty_note || T('Attempt ended because you left this app.', 'Bài bị hủy vì bạn đã thoát khỏi app.');
    const cool = Number(R.cooldown_sec) || 0;
    h += `<p class="muted"><b>${esc(note)}</b></p>`;
    if (cool > 0) {
      h += `<p class="muted" id="coolLeft">${T(`Wait ${Math.ceil(cool / 60)} min before the next try.`, `Chờ ${Math.ceil(cool / 60)} phút mới làm lại.`)}</p>`;
    } else {
      h += `<p class="muted">${T('Wait ends before you can retry (1st leave = 1 min, then doubles).', 'Hết chờ mới làm lại được (lần 1 = 1 phút, sau nhân đôi).')}</p>`;
    }
  } else if (!pass) {
    h += `<p class="muted"><b>${T('Attendance not recorded yet.', 'Chưa được điểm danh.')}</b>
      ${T('Please retry.', 'Hãy làm lại.')}</p>`;
  } else if (R.attendance_done) {
    h += `<p class="muted">${T('Attendance already recorded. You may leave.', 'Đã điểm danh. Bạn có thể ra về.')}</p>`;
  }
  h += `</div>
    <button class="big on" id="done">${T('Done', 'Xong')}</button>
    ${!pass ? `<button class="big" id="retry">${T('Try again', 'Làm lại')}</button>` : ''}
    </main>`;
  app.innerHTML = h;
  bindLangToggle(app);
  const out = $('#out'); if (out) out.onclick = signOut;
  $('#done').onclick = () => { Q.result = null; reload(); };
  const retry = $('#retry');
  if (retry) retry.onclick = () => { const slug = R.slug; Q.result = null; beginPreRead(slug); };
}

function renderExplain(app) {
  const E = Q.explain;
  const q = E.review[E.i];
  const n = E.review.length;
  if (!q) {
    app.innerHTML = headBar() + `<main><p class="muted">${T('Nothing to explain.', 'Không có câu để giải thích.')}</p>
      <button class="big on" id="done">${T('Done', 'Xong')}</button></main>`;
    $('#done').onclick = () => { Q.explain = null; reload(); };
    return;
  }
  let h = headBar() + `<main class="no-copy">
    <p class="muted"><b>${T('Answer review', 'Xem đáp án')}</b> ${E.i + 1} / ${n}. ${T('Your choice, the correct answer, and the English explanation. Final score only at the end.', 'Đáp án bạn chọn, đáp án đúng, và giải thích tiếng Anh. Điểm tổng chỉ hiện ở cuối.')}</p>
    <div class="card qcard ${q.ok ? 'ok' : 'bad'}">
      <div class="stem">${E.i + 1}. ${quizMath(q.stem)}</div>
      <p class="muted"><b>${q.ok ? T('You got this right', 'Bạn đúng câu này') : T('You got this wrong', 'Bạn sai câu này')}</b></p>`;
  if ((q.type || 'mcq') === 'numeric') {
    const unit = q.unit ? ' ' + q.unit : '';
    const exp = Number.isFinite(+q.exp) ? +q.exp : (Number.isFinite(+q.power10) ? +q.power10 : 0);
    const yours = (q.mantissa == null || q.mantissa === '')
      ? '–'
      : `${esc(String(q.mantissa))} * 10<sup>${exp}</sup>${quizMath(unit)}`;
    h += `<div class="muted"><b>${T('Your answer', 'Bạn chọn')}</b>: ${yours}</div>
      <div class="muted"><b>${T('Correct answer', 'Đáp án đúng')}</b>: ${esc(String(q.correct))}${quizMath(unit)}</div>`;
  } else {
    (q.choices || []).forEach((c, ci) => {
      let tag = '';
      if (ci === q.correct && ci === q.chosen) tag = ` ← ${T('your choice = correct', 'bạn chọn = đúng')}`;
      else if (ci === q.correct) tag = ` ← ${T('correct', 'đáp án đúng')}`;
      else if (ci === q.chosen) tag = ` ← ${T('your choice', 'bạn chọn')}`;
      h += `<div class="muted">${String.fromCharCode(65 + ci)}. ${quizMath(c)}${tag ? `<b>${tag}</b>` : ''}</div>`;
    });
  }
  const last = E.i + 1 >= n;
  h += `<div class="explain"><b>${T('Explanation', 'Giải thích')}</b>: ${quizMath(q.explain || 'This is the correct idea for this item.')}</div>
    </div>
    <p class="muted" id="explainWait"></p>
    <button class="big on" id="next">${last ? T('Continue to attendance', 'Tiếp tới điểm danh') : T('Next', 'Tiếp')}</button>
    </main>`;
  app.innerHTML = h;
  bindLangToggle(app);
  blockCopy(app.querySelector('main.no-copy') || app);
  const out = $('#out'); if (out) out.onclick = signOut;
  const next = $('#next');
  const waitEl = $('#explainWait');
  const doneLabel = last ? T('Continue to attendance', 'Tiếp tới điểm danh') : T('Next', 'Tiếp');
  if (E._timer) clearInterval(E._timer);
  const tick = () => {
    if (!Q.explain || Q.explain !== E) { clearInterval(E._timer); return; }
    const left = Math.max(0, E.unlockAt - Date.now());
    const sec = Math.ceil(left / 1000);
    if (left <= 0) {
      clearInterval(E._timer);
      E._timer = null;
      waitEl.textContent = '';
      next.classList.remove('wait');
      next.textContent = doneLabel;
      return;
    }
    next.classList.add('wait');
    waitEl.textContent = T(`Next unlocks in ${sec}s — keep reading. Tapping adds +10s.`, `Còn ${sec}s mới bấm tiếp — hãy đọc. Bấm sớm bị +10s.`);
    next.textContent = T(`Wait ${sec}s`, `Chờ ${sec}s`);
  };
  E._timer = setInterval(tick, 200);
  tick();
  next.onclick = () => {
    if (Date.now() < E.unlockAt) {
      E.unlockAt += 10000;
      if (!E._timer) E._timer = setInterval(tick, 200);
      tick();
      return;
    }
    if (E._timer) clearInterval(E._timer);
    if (last) { E.i = n; return showAttendanceAsk(); }
    E.i += 1;
    E.unlockAt = Date.now() + 10000;
    render();
  };
}

function reviewTimeLabel(seconds) {
  if (!seconds) return T('Session ended.', 'Phiên ôn tập đã kết thúc.');
  const time = `${Math.floor(seconds / 60)}:${String(seconds % 60).padStart(2, '0')}`;
  return T(`Session time left: ${time}`, `Thời gian còn lại: ${time}`);
}

let reviewClock;
function watchReviewClock(deadline, paint) {
  clearInterval(reviewClock);
  const tick = () => {
    const seconds = Math.max(0, Math.ceil((deadline - Date.now()) / 1000));
    if (!paint(seconds) || !seconds) clearInterval(reviewClock);
  };
  reviewClock = setInterval(tick, 1000);
  tick();
}

function showAttendanceAsk() {
  const E = Q.explain;
  if (!E) return;
  if (E._timer) clearInterval(E._timer);
  const app = $('#app');
  const askLabel = T("I'm done — please mark my attendance", 'Em xong rồi — thầy điểm danh giúp em');
  const application = E.followUp.map(q => `<fieldset class="card qcard">
    <legend>${quizMath(q.stem)}</legend>
    ${q.choices.map((choice, index) => `<label><input type="radio" name="${esc(q.id)}"
      value="${index}" ${E.followAnswers[q.id] === index ? 'checked' : ''}> ${quizMath(choice)}</label>`).join('')}
    </fieldset>`).join('');
  app.innerHTML = headBar() + `<main>
    <h2>${E.followUp.length ? T('Apply what you reviewed', 'Áp dụng kiến thức vừa ôn') : T('Ready for attendance', 'Sẵn sàng điểm danh')}</h2>
    ${application}
    <p class="muted" id="finishStatus"></p>
    <button class="big on" id="askAtt">${askLabel}</button>
    </main>`;
  bindLangToggle(app);
  const out = $('#out'); if (out) out.onclick = signOut;
  const btn = $('#askAtt');
  let pending = false;
  const update = (seconds) => {
    if (Q.explain !== E || $('#askAtt') !== btn) return false;
    const wait = Math.max(0, Math.ceil((E.finishAt - Date.now()) / 1000));
    btn.disabled = pending || (E.deadline != null && !seconds) || wait > 0
      || E.followUp.some(q => E.followAnswers[q.id] == null);
    const unlock = wait ? T(`Finish opens in ${Math.ceil(wait / 60)} min.`, `Còn ${Math.ceil(wait / 60)} phút mới hoàn tất được.`) : '';
    $('#finishStatus').textContent = E.deadline ? [reviewTimeLabel(seconds), unlock].filter(Boolean).join(' ') : '';
    return true;
  };
  const refresh = () => update(E.deadline ? Math.max(0, Math.ceil((E.deadline - Date.now()) / 1000)) : 1);
  app.querySelectorAll('fieldset input[type="radio"]').forEach(input => {
    input.onchange = () => {
      E.followAnswers[input.name] = Number(input.value);
      refresh();
    };
  });
  btn.onclick = async () => {
    pending = true;
    refresh();
    try { await finishExplain(); }
    finally { pending = false; refresh(); }
  };
  if (E.deadline) watchReviewClock(E.deadline, update);
  else refresh();
}

async function finishExplain() {
  const E = Q.explain;
  if (!E) return;
  const slug = E.slug;
  const j = await post('/api/public/quiz/finish_explain', { slug, follow_up: E.followAnswers });
  if (!j) return;
  const score = j.score != null ? j.score : E.score;
  const total = j.total != null ? j.total : E.total;
  const passScore = j.pass_score != null ? j.pass_score : E.pass_score;
  Q.explain = null;
  Q.result = null;
  const app = $('#app');
  app.innerHTML = headBar() + `<main><div class="card result pass">
    <div>${T('Passed', 'Đạt')}</div>
    <div class="score">${esc(String(score))} / ${esc(String(total))}</div>
    <div class="muted">${T('Pass mark', 'Mốc đạt')}: ${esc(String(passScore))}/${esc(String(total))}</div>
    <p class="muted"><b>${T('You are on the attendance list. The lecturer can mark you now — you may leave.', 'Bạn đã có trong danh sách điểm danh. Thầy có thể điểm danh — bạn có thể ra về.')}</b></p>
  </div>
  ${(j.follow_up_review || []).map(q => `<div class="card qcard">
    <div>${quizMath(q.stem)}</div>
    <p>${T('Correct answer', 'Đáp án đúng')}: ${quizMath(q.choices[q.correct])}</p>
    ${formatExplainBody(q.explain)}
    </div>`).join('')}
  <button class="big on" id="done">${T('OK — I understand', 'OK — Em hiểu rồi')}</button></main>`;
  bindLangToggle(app);
  const out = $('#out'); if (out) out.onclick = signOut;
  $('#done').onclick = () => reload();
}

function render() {
  $('#app-ver').disabled = !Q.preread?.localTheoryTest;
  document.documentElement.lang = LANG;
  document.title = T('Review Quiz', 'Quiz ôn tập');
  const app = $('#app');
  if (!isPhoneOrTablet()) return renderDeviceBlock(app);
  if (Q.preread) return renderPreRead(app);
  if (Q.explain) return Q.explain.i >= Q.explain.review.length ? showAttendanceAsk() : renderExplain(app);
  if (Q.paper) return renderPaper(app);
  if (Q.result) return renderResult(app);
  if (Q.me) return renderHome(app);
  return renderIdentify(app);
}

if (!isPhoneOrTablet()) render();
else reload();
