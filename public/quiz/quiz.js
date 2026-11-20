const Q = { cls: '', classInfo: null, me: null, paper: null, result: null, explain: null };

function quizMath(s) {
  let t = String(s ?? '');
  t = t.replace(/(^|[^A-Za-z0-9.])(\d+(?:\.\d+)?)[eE]([+-]?\d+)(?![A-Za-z0-9])/g, (_, p, a, b) => `${p}${a} * 10^${b}`);
  t = esc(t);
  t = t.replace(/(^|[^A-Za-z0-9_])([A-Za-zμσαβθφψΩ]{1,4})_([A-Za-z0-9,θφψα-ω]+)(?![A-Za-z0-9_])/g,
    (_, p, base, sub) => `${p}${base}<sub>${sub}</sub>`);
  t = t.replace(/\^\{([^}]+)\}/g, '<sup>$1</sup>');
  t = t.replace(/\^(-?\d+)/g, '<sup>$1</sup>');
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

async function reload() {
  Q.paper = null;
  Q.result = null;
  Q.explain = null;
  Q.cls = qsCls() || Q.cls;
  Q.classInfo = Q.cls ? await get('/api/public/quiz/class?cls=' + encodeURIComponent(Q.cls)) : null;
  Q.me = await get('/api/public/quiz/me');
  if (Q.me && Q.cls && String(Q.me.cls) !== String(Q.cls)) {
    await post('/api/public/quiz/logout', {});
    Q.me = null;
  }
  render();
}

async function signOut() {
  disarmLeaveGuard();
  await post('/api/public/quiz/logout', {});
  Q.me = null; Q.paper = null; Q.result = null; Q.explain = null;
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

function disarmLeaveGuard() {
  leaveArmed = false;
  document.removeEventListener('visibilitychange', onLeaveApp);
  window.removeEventListener('pagehide', onLeaveApp);
}

function armLeaveGuard() {
  disarmLeaveGuard();
  leaveDone = false;
  leaveArmed = true;
  document.addEventListener('visibilitychange', onLeaveApp);
  window.addEventListener('pagehide', onLeaveApp);
}

function onLeaveApp(ev) {
  if (!leaveArmed || leaveDone || !Q.paper) return;
  if (ev && ev.type === 'visibilitychange' && !document.hidden) return;
  leaveDone = true;
  const P = Q.paper;
  if (P && P._hintTimer) clearInterval(P._hintTimer);
  closeHintPopup();
  disarmLeaveGuard();
  try {
    fetch('/api/public/quiz/submit', {
      method: 'POST',
      headers: quizHeaders({ 'Content-Type': 'application/json' }),
      body: JSON.stringify({ attempt_id: P.attempt_id, answers: {} }),
      keepalive: true,
      credentials: 'same-origin',
    });
  } catch (e) {}
  Q.paper = null;
  Q.result = {
    passed: false,
    score: 0,
    total: P.total,
    pass_score: P.pass_score,
    slug: P.slug,
    left_app: true,
  };
  render();
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
    <p class="muted">${T('Each student gets a different shuffled paper. Pass the quiz, then read every English explanation. Attendance is given only after that.', 'Mỗi bạn một đề xáo khác nhau. Đạt quiz rồi phải đọc hết giải thích tiếng Anh. Điểm danh chỉ sau bước đó.')}</p>`;
  if (!I.sets.length) h += `<p class="muted">${T('No open quiz right now.', 'Hiện chưa có quiz nào mở.')}</p>`;
  I.sets.forEach(s => {
    let badge, btn;
    if (s.attendance_done) {
      badge = `<span class="badge ok">${T('Attendance done', 'Đã điểm danh')} ${s.best}/${s.n_pick}</span>`;
      btn = `<p class="muted">${T('You may leave.', 'Bạn có thể ra về.')}</p>`;
    } else if (s.needs_explanations) {
      badge = `<span class="badge warn">${T('Passed — read explanations', 'Đạt — đọc giải thích')} ${s.best}/${s.n_pick}</span>`;
      btn = `<button class="big on" data-explain="${esc(s.slug)}">${T('Continue explanations', 'Tiếp tục đọc giải thích')}</button>`;
    } else if (s.passed) {
      badge = `<span class="badge ok">${T('Passed', 'Đạt')} ${s.best}/${s.n_pick}</span>`;
      btn = `<p class="muted">${T('Done.', 'Đã xong.')}</p>`;
    } else {
      badge = s.tries
        ? `<span class="badge warn">${T('Best', 'Cao nhất')} ${s.best}/${s.n_pick}</span>`
        : `<span class="badge">${T('Not tried', 'Chưa làm')}</span>`;
      btn = `<button class="big on" data-start="${esc(s.slug)}">${s.tries ? T('Retry', 'Làm lại') : T('Start', 'Bắt đầu')}</button>`;
    }
    h += `<div class="card qcard"><div class="stem">${esc(s.title)}</div>
      <div class="muted">${badge} · ${T('tries', 'lần')}: ${s.tries} · pass ${s.pass_score}/${s.n_pick}</div>
      ${btn}</div>`;
  });
  h += `<div class="btns"><button class="on" id="ref">${T('Refresh', 'Tải lại')}</button></div></main>`;
  app.innerHTML = h;
  bindLangToggle(app);
  const out = $('#out'); if (out) out.onclick = signOut;
  $('#ref').onclick = () => reload();
  app.querySelectorAll('[data-start]').forEach(b => b.onclick = () => startQuiz(b.dataset.start));
  app.querySelectorAll('[data-explain]').forEach(b => b.onclick = () => resumeExplain(b.dataset.explain));
}

async function startQuiz(slug) {
  const j = await post('/api/public/quiz/start', { slug });
  if (!j) return;
  j.startedAt = Date.now();
  j.hints_unlocked = !!j.hints_ready;
  j.hint_after_sec = Number(j.hint_after_sec) || 20 * 60;
  Q.paper = j;
  Q.result = null;
  Q.explain = null;
  render();
}

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
    review: payload.review || [],
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
    <p class="muted" id="hintBanner">${hintsOn
      ? `<b>${T('Hints unlocked — tap the lightbulb on each question.', 'Đã mở gợi ý — bấm bóng đèn ở từng câu.')}</b>`
      : T(`Lightbulb unlocks after ${mins} min, after 5+ tries, or from attempt 4 if scores stay between 10 and 14.`, `Bóng đèn mở sau ${mins} phút, sau trên 5 lần thử, hoặc từ lần 4 nếu điểm cứ trong khoảng 10–14.`)}</p>`;
  P.questions.forEach((q, qi) => {
    const bulb = q.hint
      ? `<button type="button" class="hintbulb ${hintsOn ? 'on' : ''}" data-qid="${esc(q.id)}" data-qn="${qi + 1}"
          ${hintsOn ? '' : 'disabled'} aria-label="${T('Hint', 'Gợi ý')}">💡</button>`
      : '';
    h += `<div class="card qcard" data-qid="${esc(q.id)}" data-type="${esc(q.type || 'mcq')}">
      <div class="stemrow"><div class="stem">${qi + 1}. ${quizMath(q.stem)}</div>${bulb}</div>`;
    if ((q.type || 'mcq') === 'numeric') {
      const p10 = Number.isFinite(+q.power10) ? +q.power10 : 0;
      h += `<label class="fl numans">${T('Your answer', 'Nhập đáp án')}
        <span class="numrow"><input inputmode="numeric" autocomplete="off" name="q_${esc(q.id)}" placeholder="${T('integer', 'số nguyên')}">
        <span class="scale">* 10<sup>${p10}</sup></span>
        ${q.unit ? `<span class="unit">${quizMath(q.unit)}</span>` : ''}</span></label>
        <p class="muted">${T('Enter the integer coefficient only; *10 power is fixed.', 'Chỉ nhập hệ số nguyên; mũ 10 đã cho sẵn.')}</p>`;
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
  if (!hintsOn) {
    P._hintTimer = setInterval(() => {
      if (!Q.paper || Q.paper.attempt_id !== P.attempt_id) { clearInterval(P._hintTimer); return; }
      if (paperHintsOn()) {
        clearInterval(P._hintTimer);
        unlockPaperHints(app);
      }
    }, 5000);
  }
  armLeaveGuard();
  $('#cancel').onclick = () => { if (P._hintTimer) clearInterval(P._hintTimer); closeHintPopup(); disarmLeaveGuard(); Q.paper = null; render(); };
  $('#submit').onclick = async () => {
    const answers = {};
    let missing = 0;
    P.questions.forEach(q => {
      if ((q.type || 'mcq') === 'numeric') {
        const inp = app.querySelector(`input[name="q_${q.id}"]`);
        const v = inp ? inp.value.trim() : '';
        if (!v) missing += 1;
        answers[q.id] = v;
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
    Q.paper = null;
    if (j.passed && j.needs_explanations && j.review) beginExplain(j);
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
    h += `<p class="muted"><b>${T('Attempt ended because you left this app.', 'Bài bị hủy vì bạn đã thoát khỏi app.')}</b>
      ${T('You can retry.', 'Bạn có thể làm lại.')}</p>`;
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
  if (retry) retry.onclick = () => { const slug = R.slug; Q.result = null; startQuiz(slug); };
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
    <p class="muted">${T('Explanation', 'Giải thích')} ${E.i + 1} / ${n}. ${T('Read carefully (English).', 'Đọc kỹ (tiếng Anh).')}</p>
    <div class="card qcard ${q.ok ? 'ok' : 'bad'}">
      <div class="stem">${E.i + 1}. ${quizMath(q.stem)}</div>`;
  if ((q.type || 'mcq') === 'numeric') {
    const unit = q.unit ? ' ' + q.unit : '';
    const p10 = Number.isFinite(+q.power10) ? +q.power10 : 0;
    const yours = (q.mantissa == null || q.mantissa === '')
      ? '–'
      : `${esc(String(q.mantissa))} * 10<sup>${p10}</sup>${quizMath(unit)}`;
    h += `<div class="muted">${T('Your answer', 'Bạn nhập')}: ${yours}</div>
      <div class="muted">${T('Correct', 'Đáp án đúng')}: ${esc(String(q.correct))}${quizMath(unit)}</div>`;
  } else {
    (q.choices || []).forEach((c, ci) => {
      const mark = ci === q.correct ? ' ✓' : (ci === q.chosen ? ' ✗' : '');
      h += `<div class="muted">${String.fromCharCode(65 + ci)}. ${quizMath(c)}${mark}</div>`;
    });
  }
  h += `<div class="explain">${quizMath(q.explain || 'This is the correct idea for this item.')}</div>
    </div>
    <p class="muted" id="explainWait"></p>
    <button class="big on" id="next" disabled>${E.i + 1 >= n ? T('Finish', 'Hoàn thành') : T('Next', 'Tiếp')}</button>
    </main>`;
  app.innerHTML = h;
  bindLangToggle(app);
  blockCopy(app.querySelector('main.no-copy') || app);
  const out = $('#out'); if (out) out.onclick = signOut;
  const next = $('#next');
  const waitEl = $('#explainWait');
  const doneLabel = E.i + 1 >= n ? T('Finish', 'Hoàn thành') : T('Next', 'Tiếp');
  if (E._timer) clearInterval(E._timer);
  const tick = () => {
    if (!Q.explain || Q.explain !== E) { clearInterval(E._timer); return; }
    const left = Math.max(0, E.unlockAt - Date.now());
    const sec = Math.ceil(left / 1000);
    if (left <= 0) {
      clearInterval(E._timer);
      E._timer = null;
      waitEl.textContent = '';
      next.disabled = false;
      next.textContent = doneLabel;
      return;
    }
    next.disabled = true;
    waitEl.textContent = T(`Next unlocks in ${sec}s — keep reading.`, `Còn ${sec}s mới bấm tiếp — hãy đọc tiếp.`);
    next.textContent = T(`Wait ${sec}s`, `Chờ ${sec}s`);
  };
  E._timer = setInterval(tick, 200);
  tick();
  next.onclick = () => {
    if (Date.now() < E.unlockAt || next.disabled) return;
    if (E._timer) clearInterval(E._timer);
    if (E.i + 1 >= n) return finishExplain();
    E.i += 1;
    E.unlockAt = Date.now() + 10000;
    render();
  };
}

async function finishExplain() {
  const slug = Q.explain.slug;
  const j = await post('/api/public/quiz/finish_explain', { slug });
  if (!j) return;
  Q.explain = null;
  Q.result = {
    passed: true,
    attendance_done: true,
    score: '—',
    total: '—',
    pass_score: '—',
    slug,
    doneMsg: true,
  };
  const app = $('#app');
  app.innerHTML = headBar() + `<main><div class="card result pass">
    <div>${T('Attendance recorded', 'Đã điểm danh')}</div>
    <div class="score">✓</div>
    <p class="muted">${T('You have completed the quiz and all explanations. You may leave now.', 'Bạn đã hoàn thành quiz và toàn bộ giải thích. Bạn có thể ra về.')}</p>
  </div>
  <button class="big on" id="done">${T('OK', 'OK')}</button></main>`;
  bindLangToggle(app);
  const out = $('#out'); if (out) out.onclick = signOut;
  $('#done').onclick = () => { Q.result = null; reload(); };
}

function render() {
  document.documentElement.lang = LANG;
  document.title = T('Review Quiz', 'Quiz ôn tập');
  const app = $('#app');
  if (!isPhoneOrTablet()) return renderDeviceBlock(app);
  if (Q.explain) return renderExplain(app);
  if (Q.paper) return renderPaper(app);
  if (Q.result) return renderResult(app);
  if (Q.me) return renderHome(app);
  return renderIdentify(app);
}

if (!isPhoneOrTablet()) render();
else reload();
