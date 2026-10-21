// Student page: student ID + 4-digit PIN -> your team, your card for the open labs, your marks (when released).
// The PIN is chosen by the student at the first sign-in; the lecturer can reset it (tab Class).
const ST = { info: null, sid: '', step: 'sid', need: null, name: '' };
try { ST.sid = localStorage.getItem('student_sid') || ''; } catch (e) {}

async function post(path, body) {
  const r = await fetch(path, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) });
  const j = await r.json().catch(() => ({}));
  if (!r.ok) { toast((LANG === 'vi' && j.error_vi) || j.error || T('Error', 'Lỗi')); if (r.status === 401) { ST.info = null; render(); } return null; }
  return j;
}

async function me() {   // the signed-in student's information (session cookie), or null
  const r = await fetch('/api/public/me');
  if (r.status === 401) return null;
  const j = await r.json().catch(() => ({}));
  if (!r.ok) { toast((LANG === 'vi' && j.error_vi) || j.error || T('Error', 'Lỗi')); return null; }
  return j;
}

async function reload() { const info = await me(); ST.info = info; render(); return info; }

function renderSignIn(app, head) {
  let body;
  if (ST.step === 'sid') {
    body = `<h2>${T('Your student ID', 'MSSV của bạn')}</h2>
      <p class="muted">${T('Type your student ID (SIS ID on Canvas), for example AUS15128.', 'Nhập MSSV (SIS ID trên Canvas), ví dụ AUS15128.')}</p>
      <input id="sid" autocomplete="username" autocapitalize="characters" value="${esc(ST.sid)}">
      <button class="big on" id="go">${T('Next', 'Tiếp')}</button>`;
  } else {
    const isNew = ST.need === 'new';
    body = `<h2>${isNew ? T('Choose your PIN', 'Đặt PIN của bạn') : T('Your PIN', 'PIN của bạn')}</h2>
      <p class="muted">${esc(ST.name || ST.sid)}</p>
      <p class="muted">${isNew ? T('First time: choose 4 digits and remember them. You need this PIN every time you sign in on a new phone.', 'Lần đầu: chọn 4 chữ số và nhớ kỹ. Đăng nhập trên điện thoại khác sẽ cần PIN này.')
                               : T('Forgot your PIN? Ask the lecturer to reset it.', 'Quên PIN? Nhờ giảng viên đặt lại.')}</p>
      <input id="pin" type="password" inputmode="numeric" maxlength="4" autocomplete="${isNew ? 'new-password' : 'current-password'}" placeholder="••••">
      ${isNew ? `<input id="pin2" type="password" inputmode="numeric" maxlength="4" autocomplete="new-password" placeholder="${T('Type it again', 'Nhập lại')}">` : ''}
      <button class="big on" id="go">${T('Sign in', 'Đăng nhập')}</button>
      <p style="text-align:center"><a href="#" id="back">${T('Not me / change ID', 'Không phải tôi / đổi MSSV')}</a></p>`;
  }
  app.innerHTML = head + `<main><div class="login card sidform">${body}</div></main>`;
  bindLangToggle(app);
  const go = async () => {
    if (ST.step === 'sid') {
      const sid = $('#sid').value.trim(); if (!sid) return;
      const j = await post('/api/public/login', { sid }); if (!j) return;
      ST.sid = sid; try { localStorage.setItem('student_sid', sid); } catch (e) {}
      if (j.ok) return reload();
      ST.need = j.need; ST.name = j.name || ''; ST.step = 'pin'; return render();
    }
    const pin = $('#pin').value.trim();
    if (!/^\d{4}$/.test(pin)) return toast(T('The PIN must be 4 digits.', 'PIN phải gồm 4 chữ số.'));
    if (ST.need === 'new' && pin !== $('#pin2').value.trim()) return toast(T('The two PINs are different.', 'Hai lần nhập PIN không giống nhau.'));
    const j = await post('/api/public/login', { sid: ST.sid, pin }); if (!j) return;
    ST.step = 'sid'; ST.need = null; reload();
  };
  $('#go').onclick = go;
  app.querySelectorAll('input').forEach(i => i.onkeydown = e => { if (e.key === 'Enter') go(); });
  const back = $('#back'); if (back) back.onclick = e => { e.preventDefault(); ST.step = 'sid'; ST.need = null; render(); };
  (app.querySelector('#pin') || app.querySelector('#sid')).focus();
}

function render() {
  document.documentElement.lang = LANG;
  document.title = T('Electric Circuit Lab – Student', 'Electric Circuit Lab – Sinh viên');
  const app = $('#app');
  const head = `<header><div class="row"><h1>Electric Circuit Lab</h1>${langToggle()}</div></header>`;
  if (!ST.info) return renderSignIn(app, head);
  const I = ST.info;
  let h = head + `<main><div class="card who"><div class="nm">${esc(I.name)}</div>
    <div class="sub">${esc(I.sid)} | ${esc(I.className)}</div>`;
  if (I.team) {
    h += `<div class="teambig"><div><b>${I.team}</b>${T('Team / bench', 'Nhóm / cụm máy')}</div><div><b>${I.member}</b>${T('Member', 'Thành viên')}</div><div><b>${I.variant}</b>${T('Variant', 'Mã đề')}</div></div>
      <div class="sub">${T('Your team', 'Cùng nhóm')}: ${I.teammates.length ? I.teammates.map(esc).join(', ') : '–'}</div>`;
  } else {
    h += `<p class="muted">${T('You are not in a team yet. Ask the lecturer.', 'Bạn chưa có nhóm. Hỏi giảng viên.')}</p>`;
  }
  h += `</div>`;
  let shown = 0, sum = 0, total = 0;
  I.labs.forEach(L => {
    if (!L.card && L.marks === null && !L.submit) return;
    shown++;
    h += `<div class="card lab"><h3>Lab ${L.lab}</h3>`;
    if (L.card) h += `<div class="lines">${L.card.map(l => `<div>${sub(l)}</div>`).join('')}</div>`;
    (L.figs || []).forEach(f => { h += `<img src="${f}" alt="${T('Circuit', 'Sơ đồ mạch')}" class="fig">`; });
    if (L.image) h += `<img src="${L.image}" alt="Oscilloscope screen">`;
    if (L.card && L.lab === '2') h += `<p><a class="dl" href="/student/files/Lab2_RLC_data_template.xlsx" download>⬇ ${T('Excel template for your RLC data', 'File Excel mẫu để ghi số liệu RLC')}</a></p>`;
    if (L.submit) h += submitForm(L);
    if (L.marks !== null) { sum += L.marks; total += L.total;
      h += `<div class="marks">${T('Marks', 'Điểm')}: <b>${L.marks}</b> / ${L.total}</div>`; }
    h += `</div>`;
  });
  if (!shown) h += `<p class="muted">${T('Nothing to show yet. Your card appears when the lab starts.', 'Chưa có gì để hiện. Đề sẽ hiện khi bắt đầu buổi lab.')}</p>`;
  if (total) h += `<p class="muted">${T(`Released labs: <b>${sum}</b> / ${total}. These marks are provisional – the official marks are on Canvas.`, `Các lab đã công bố: <b>${sum}</b> / ${total}. Điểm này để tham khảo – điểm chính thức trên Canvas.`)}</p>`;
  h += `<div class="btns"><button class="on" id="ref">${T('Refresh', 'Tải lại')}</button><button id="out">${T('Sign out', 'Đăng xuất')}</button></div></main>`;
  app.innerHTML = h;
  bindLangToggle(app);
  app.querySelectorAll('[data-send]').forEach(b => b.onclick = async () => {
    const lab = b.dataset.send, box = b.closest('.submit');
    const values = [...box.querySelectorAll('input')].map(i => i.value.trim());
    if (values.some(v => v !== '' && isNaN(+v.replace(',', '.')))) { toast(T('Numbers only, please.', 'Chỉ nhập số.')); return; }
    b.disabled = true;
    const j = await post('/api/public/submit', { lab, values });
    b.disabled = false;
    if (!j) return;
    toast(T('Submitted', 'Đã nộp')); reload();
  });
  app.querySelectorAll('[data-photo]').forEach(inp => inp.onchange = async () => {
    const f = inp.files[0]; if (!f) return;
    toast(T('Uploading…', 'Đang gửi ảnh…'));
    let data; try { data = await shrink(f); } catch (e) { toast(T('Could not read the photo', 'Không đọc được ảnh')); return; }
    const j = await post('/api/public/photo', { lab: inp.dataset.photo, data });
    if (!j) return;
    toast(T('Photo saved', 'Đã lưu ảnh')); reload();
  });
  app.querySelectorAll('[data-delph]').forEach(b => b.onclick = async () => {
    if (!confirm(T('Delete this photo?', 'Xóa ảnh này?'))) return;
    if (await post('/api/public/photo_delete', { lab: b.dataset.lab, id: +b.dataset.delph })) reload();
  });
  $('#ref').onclick = async () => { if (await reload()) toast(T('Updated', 'Đã cập nhật')); };
  $('#out').onclick = async () => { await post('/api/public/logout', {}); ST.info = null; ST.step = 'sid'; render(); };
}

reload();

// values form under the card: editable until the lecturer ticks
function submitForm(L) {
  const S_ = L.submit, vals = S_.values || [];
  let h = `<div class="submit"><div class="subhead">${T('Your measured values', 'Số liệu đo của bạn')}</div>`;
  if (S_.locked) h += `<p class="ok">${T('Checked by the lecturer – locked.', 'Giảng viên đã xác nhận – đã khóa.')}</p>`;
  h += S_.questions.map((q, i) => `<label>${sub(q[0])} <small>(${esc(q[1])})</small>
      <input inputmode="decimal" ${S_.locked ? 'disabled' : ''} value="${vals[i] ?? ''}" placeholder="${T('number', 'số')}"></label>`).join('');
  // photos of the real circuit (evidence), 1–3 per lab
  const P = S_.photos || [];
  h += `<div class="subhead">${T('Photos of your circuit (1–3)', 'Ảnh mạch thật (1–3 ảnh)')}</div>`;
  if (!P.length) h += `<p class="zero">${T('No photo yet – required. Take a photo of your breadboard (and the instrument screen).', 'Chưa có ảnh – bắt buộc. Chụp breadboard (và màn hình máy đo).')}</p>`;
  h += `<div class="thumbs">${P.map(p => `<div class="th"><a href="${p.url}" target="_blank"><img src="${p.url}" alt="photo"></a>${S_.locked ? '' : `<button data-delph="${p.id}" data-lab="${L.lab}" title="${T('Delete', 'Xóa')}">×</button>`}</div>`).join('')}</div>`;
  if (!S_.locked && P.length < 3) h += `<label class="btn pri photo-btn">${T('Take / choose a photo', 'Chụp / chọn ảnh')}<input type="file" accept="image/*" capture="environment" data-photo="${L.lab}" hidden></label>`;
  if (!S_.locked) h += `<button class="big on" data-send="${L.lab}">${S_.time ? T('Update', 'Nộp lại') : T('Submit', 'Nộp')}</button>`;
  if (S_.time) h += `<p class="muted">${T('Last submitted', 'Nộp lần cuối')}: ${esc(S_.time)}</p>`;
  h += `<p class="muted">${T('Use measured values, in the unit shown. You can change them until the lecturer checks your reading.', 'Dùng số đo thật, đúng đơn vị ghi bên cạnh. Sửa được cho đến khi giảng viên xác nhận.')}</p></div>`;
  return h;
}

// make the photo small before sending (max 1280 px, JPEG) – saves mobile data and database space
function shrink(file) {
  return new Promise((ok, fail) => {
    const img = new Image(), url = URL.createObjectURL(file);
    img.onload = () => {
      const k = Math.min(1, 1280 / Math.max(img.width, img.height));
      const c = document.createElement('canvas'); c.width = Math.round(img.width * k); c.height = Math.round(img.height * k);
      c.getContext('2d').drawImage(img, 0, 0, c.width, c.height); URL.revokeObjectURL(url);
      ok(c.toDataURL('image/jpeg', 0.8));
    };
    img.onerror = fail; img.src = url;
  });
}
