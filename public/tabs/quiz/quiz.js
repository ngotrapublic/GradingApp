async function renderQuiz(root) {
  let j;
  try {
    j = await api('/api/quiz?cls=' + encodeURIComponent(S.cls));
  } catch (e) {
    root.innerHTML = `<p class="muted">${T('Could not load quiz.', 'Không tải được quiz.')}</p>`;
    return;
  }
  if (!j.has_quizzes) {
    root.innerHTML = `<p class="muted">${T('This course has no quiz banks.', 'Môn này chưa có ngân hàng quiz.')}</p>`;
    return;
  }
  let h = `<div class="card" style="padding:12px">
    <p>${T('Student page', 'Trang SV')}: <code>${esc(j.quiz_url || '/quiz/')}</code>
      <button class="btn" id="qqr">${T('QR + student notice', 'QR + thông báo SV')}</button></p>
    <p class="muted">${T('Open QR to show the link and the English student notice (copyable) side by side.', 'Bấm QR để hiện link và thông báo tiếng Anh cho SV (copy được) cạnh nhau.')}</p>
    <p class="muted">${T('Free name+ID. Each student gets a unique shuffle. Pass then forced English explanations (silent 10s/item) before attendance. Reset clears a student.', 'Họ tên+MSSV tự do. Mỗi SV một đề xáo riêng. Đạt rồi phải đọc giải thích tiếng Anh (im lặng ≥10s/câu) mới điểm danh. Reset để cho làm lại.')}</p>
  </div>`;
  j.sets.forEach(s => {
    h += `<div class="card" style="padding:12px;margin-bottom:10px">
      <div style="display:flex;justify-content:space-between;gap:8px;align-items:center;flex-wrap:wrap">
        <div><b>${esc(s.title)}</b><div class="muted">${s.slug} · ${T('bank', 'ngân hàng')} ${s.n} · pick ${s.n_pick} · pass ${s.pass_score}</div>
          <div class="muted">${T('Attempted', 'Đã làm')}: ${s.attempted} · ${T('Passed', 'Đạt')}: ${s.passed}</div></div>
        <button class="btn ${s.open ? 'pri' : ''}" data-tog="${esc(s.slug)}" data-open="${s.open ? 0 : 1}">
          ${s.open ? T('Close', 'Đóng') : T('Open', 'Mở')}</button>
      </div>
      <button class="btn" data-roster="${esc(s.slug)}" style="margin-top:8px">${T('Roster', 'Danh sách')}</button>
    </div>`;
  });
  h += `<div id="qroster"></div>`;
  root.innerHTML = h;
  $('#qqr').onclick = () => showQR('quiz', S.cls);
  root.querySelectorAll('[data-tog]').forEach(b => b.onclick = async () => {
    b.disabled = true;
    try {
      const ok = await api('/api/quiz', { cls: +S.cls, slug: b.dataset.tog, open: b.dataset.open === '1' });
      toast(ok.open ? T('Opened', 'Đã mở') : T('Closed', 'Đã đóng'));
      renderQuiz(root);
    } catch (e) {
      b.disabled = false;
    }
  });
  root.querySelectorAll('[data-roster]').forEach(b => b.onclick = () => loadQuizRoster(b.dataset.roster));
}

async function loadQuizRoster(slug) {
  const box = $('#qroster');
  if (!box) return;
  box.innerHTML = `<p class="muted">${T('Loading…', 'Đang tải…')}</p>`;
  let j;
  try {
    j = await api('/api/quiz?cls=' + encodeURIComponent(S.cls) + '&slug=' + encodeURIComponent(slug));
  } catch (e) {
    box.innerHTML = '';
    return;
  }
  const stLabel = {
    pass: T('Pass', 'Đạt'),
    fail: T('Fail', 'Trượt'),
    left: T('Left app / empty', 'Thoát app / trống'),
    open: T('Started (no submit)', 'Mở đề (chưa nộp)'),
  };
  const logBySid = {};
  (j.log || []).forEach(a => {
    (logBySid[a.sid] || (logBySid[a.sid] = [])).push(a);
  });
  let h = `<div class="card" style="padding:12px"><h2>${esc(slug)} – ${T('Roster', 'Danh sách')}</h2>
    <p class="muted">${T('Unchecked first (by pass time). Checked move to the bottom (blue). Tap Log for one student.', 'Chưa check ở trên (theo giờ đạt). Đã check xuống dưới (xanh dương). Bấm Log từng SV.')}</p>
    <table><thead><tr><th>${T('Time', 'Giờ')}</th><th>${T('Name', 'Tên')}</th><th>MSSV</th><th>${T('Best', 'Cao nhất')}</th><th>${T('Tries', 'Lần')}</th><th>${T('Pass', 'Đạt')}</th><th>${T('Solutions', 'Đáp án')}</th><th></th></tr></thead><tbody>`;
  j.roster.forEach(r => {
    const rowCls = r.staff_checked ? 'quiz-staff-ok' : (r.solutions_seen ? 'quiz-att-done' : (r.passed ? 'quiz-passed' : ''));
    const checkBtn = r.solutions_seen
      ? `<button class="btn ${r.staff_checked ? 'pri' : ''}" data-check="${esc(r.sid)}" data-slug="${esc(slug)}">${r.staff_checked ? T('Uncheck', 'Bỏ check') : T('Checked', 'Đã check')}</button>`
      : '';
    h += `<tr class="${rowCls}" data-sid="${esc(r.sid)}"><td>${esc(r.pass_at || '–')}</td><td>${esc(r.name)}</td><td>${esc(r.sid)}</td><td>${r.best == null ? '–' : r.best}</td><td>${r.tries}</td>
      <td>${r.passed ? '✓' : '–'}</td><td>${r.solutions_seen ? '✓' : '–'}</td>
      <td style="white-space:nowrap">
        ${checkBtn}
        <button class="btn" data-log="${esc(r.sid)}">${T('Log', 'Log')}</button>
        <button class="btn warn" data-reset="${esc(r.sid)}" data-slug="${esc(slug)}">${T('Reset', 'Reset')}</button>
      </td></tr>
      <tr class="quiz-log-row" data-logfor="${esc(r.sid)}" hidden><td colspan="8" id="qlog-${esc(r.sid)}"></td></tr>`;
  });
  h += `</tbody></table></div>`;
  box.innerHTML = h;
  const renderOneLog = (sid) => {
    const cell = box.querySelector('#qlog-' + CSS.escape(sid));
    const row = box.querySelector(`[data-logfor="${CSS.escape(sid)}"]`);
    if (!cell || !row) return;
    const rows = logBySid[sid] || [];
    if (!rows.length) {
      cell.innerHTML = `<p class="muted" style="margin:6px 0">${T('No attempts yet.', 'Chưa có lần làm nào.')}</p>`;
    } else {
      let t = `<table style="margin:6px 0"><thead><tr><th>${T('Opened', 'Mở đề')}</th><th>${T('Submitted or ended', 'Nộp hoặc kết thúc')}</th><th>${T('Duration', 'Thời lượng')}</th><th>${T('Score', 'Điểm')}</th><th>${T('Result', 'Kết quả')}</th></tr></thead><tbody>`;
      rows.forEach(a => {
        const sc = a.score == null ? '–' : `${a.score}/${a.total == null ? '–' : a.total}`;
        const submitted = a.submitted_at == null ? '–' : new Date(a.submitted_at * 1000)
          .toLocaleString('en-GB', { timeZone: 'Asia/Ho_Chi_Minh' });
        const duration = a.duration_sec == null ? '–' : `${Math.floor(a.duration_sec / 60)}m ${a.duration_sec % 60}s`;
        t += `<tr><td>${esc(a.created || '–')}</td><td>${esc(submitted)}</td><td>${duration}</td><td>${sc}</td><td>${esc(stLabel[a.status] || a.status)}</td></tr>`;
      });
      t += `</tbody></table>`;
      cell.innerHTML = t;
    }
    row.hidden = false;
  };
  box.querySelectorAll('[data-log]').forEach(b => b.onclick = () => {
    const sid = b.dataset.log;
    const row = box.querySelector(`[data-logfor="${CSS.escape(sid)}"]`);
    if (!row) return;
    if (!row.hidden) { row.hidden = true; return; }
    box.querySelectorAll('.quiz-log-row').forEach(r => { r.hidden = true; });
    renderOneLog(sid);
  });
  box.querySelectorAll('[data-check]').forEach(b => b.onclick = async () => {
    b.disabled = true;
    try {
      const r = await api('/api/quiz', { cls: +S.cls, slug: b.dataset.slug, action: 'check', sid: b.dataset.check });
      toast(r.staff_checked ? T('Marked checked', 'Đã check') : T('Unchecked', 'Đã bỏ check'));
      loadQuizRoster(b.dataset.slug);
    } catch (e) {
      b.disabled = false;
    }
  });
  box.querySelectorAll('[data-reset]').forEach(b => b.onclick = async () => {
    const sid = b.dataset.reset;
    if (!confirm(T(`Reset ${sid}? They can take the quiz again.`, `Reset ${sid}? Sinh viên sẽ làm lại được.`))) return;
    b.disabled = true;
    try {
      await api('/api/quiz', { cls: +S.cls, slug: b.dataset.slug, action: 'reset', sid });
      toast(T('Reset done', 'Đã reset'));
      loadQuizRoster(b.dataset.slug);
    } catch (e) {
      b.disabled = false;
    }
  });
}
