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
      <button class="btn" id="qqr">${T('QR for students', 'QR cho SV')}</button></p>
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
  let h = `<div class="card" style="padding:12px"><h2>${esc(slug)} – ${T('Roster', 'Danh sách')}</h2>
    <table><thead><tr><th>${T('Name', 'Tên')}</th><th>MSSV</th><th>${T('Best', 'Cao nhất')}</th><th>${T('Tries', 'Lần')}</th><th>${T('Pass', 'Đạt')}</th><th>${T('Solutions', 'Đáp án')}</th><th></th></tr></thead><tbody>`;
  j.roster.forEach(r => {
    h += `<tr><td>${esc(r.name)}</td><td>${esc(r.sid)}</td><td>${r.best == null ? '–' : r.best}</td><td>${r.tries}</td>
      <td>${r.passed ? '✓' : '–'}</td><td>${r.solutions_seen ? '✓' : '–'}</td>
      <td><button class="btn warn" data-reset="${esc(r.sid)}" data-slug="${esc(slug)}">${T('Reset', 'Reset')}</button></td></tr>`;
  });
  h += `</tbody></table></div>`;
  box.innerHTML = h;
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
