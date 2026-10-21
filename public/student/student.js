// Student page: student ID -> confirm your name -> password (created at the first sign-in, one password for all lab courses)
// -> choose the class (when you take several lab courses) -> your team, your card for the open labs, your marks (when released).
const ST = { me: null, info: null, step: 'sid', check: null, cls: '', draft: {} };
try { ST.cls = localStorage.getItem('student_cls') || ''; } catch (e) {}

function cacheDrafts() {
  document.querySelectorAll('.submit [data-send]').forEach(b => {
    const box = b.closest('.submit');
    ST.draft[b.dataset.send] = [...box.querySelectorAll('input[inputmode="decimal"]')].map(i => i.value);
  });
}
function formValues(lab, saved, frozen) {
  if (frozen) return (saved || []).map(v => v == null ? '' : String(v));
  const d = ST.draft[lab];
  return (d && d.length ? d : (saved || [])).map(v => v == null ? '' : String(v));
}
function clearDraft(lab) { delete ST.draft[lab]; }

async function post(path, body) {
  const r = await fetch(path, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) });
  const j = await r.json().catch(() => ({}));
  if (!r.ok) { toast((LANG === 'vi' && j.error_vi) || j.error || T('Error', 'Lỗi')); if (r.status === 401) { ST.me = null; ST.info = null; render(); } return null; }
  return j;
}
async function get(path) {
  const r = await fetch(path);
  if (r.status === 401) return null;
  const j = await r.json().catch(() => ({}));
  if (!r.ok) { toast((LANG === 'vi' && j.error_vi) || j.error || T('Error', 'Lỗi')); return null; }
  return j;
}

// who am I + the open class (the one chosen before, or the only one)
async function reload() {
  ST.me = await get('/api/public/me'); ST.info = null;
  if (ST.me) {
    const ids = ST.me.classes.map(c => String(c.id));
    if (!ids.includes(ST.cls)) ST.cls = ids.length === 1 ? ids[0] : '';
    if (ST.cls) ST.info = await get('/api/public/class/' + ST.cls);
  }
  render(); return ST.me;
}
function pick(id) { ST.cls = String(id); try { localStorage.setItem('student_cls', ST.cls); } catch (e) {} return reload(); }

function renderSignIn(app, head) {
  let body;
  const c = ST.check;
  if (ST.step === 'sid') {
    body = `<div class="sidform"><h2>${T('Your student ID', 'MSSV của bạn')}</h2>
      <p class="muted">${T('Type your student ID (SIS ID on Canvas), for example AUS15128.', 'Nhập MSSV (SIS ID trên Canvas), ví dụ AUS15128.')}</p>
      <input id="sid" autocomplete="username" autocapitalize="characters" value="${esc((c && c.sid) || '')}"></div>
      <button class="big on" id="go">${T('Next', 'Tiếp')}</button>`;
  } else if (ST.step === 'confirm') {
    body = `<h2>${T('Is this you?', 'Đây có phải bạn không?')}</h2>
      <p class="confirm"><b>${esc(c.name)}</b><br><span class="muted">${esc(c.sid)}</span></p>
      <button class="big on" id="go">${T('Yes, this is me', 'Đúng, là tôi')}</button>
      <button class="big" id="back">${T('No – change the student ID', 'Không – nhập lại MSSV')}</button>`;
  } else {
    const isNew = !c.hasPassword;
    body = `<h2>${isNew ? T('Create your password', 'Tạo mật khẩu') : T('Your password', 'Mật khẩu của bạn')}</h2>
      <p class="muted">${esc(c.name)} · ${esc(c.sid)}</p>
      <p class="muted">${isNew ? T('First sign-in: create a password (at least 6 characters). Next time you sign in with your student ID and this password – for all your lab courses.', 'Lần đầu: tạo mật khẩu (ít nhất 6 ký tự). Lần sau đăng nhập bằng MSSV và mật khẩu này – dùng cho mọi môn lab.')
                               : T('Forgot your password? Ask your lecturer to reset it.', 'Quên mật khẩu? Nhờ giảng viên đặt lại.')}</p>
      <label class="fl">${T('Password', 'Mật khẩu')}<input id="pw" type="password" autocomplete="${isNew ? 'new-password' : 'current-password'}"></label>
      ${isNew ? `<label class="fl">${T('Password again', 'Nhập lại mật khẩu')}<input id="pw2" type="password" autocomplete="new-password"></label>` : ''}
      <button class="big on" id="go">${isNew ? T('Create and sign in', 'Tạo và đăng nhập') : T('Sign in', 'Đăng nhập')}</button>
      <p style="text-align:center"><a href="#" id="back">${T('Not me / change ID', 'Không phải tôi / đổi MSSV')}</a></p>`;
  }
  app.innerHTML = head + `<main><div class="login card">${body}</div></main>`;
  bindLangToggle(app);
  const go = async () => {
    if (ST.step === 'sid') {
      const sid = $('#sid').value.trim(); if (!sid) return;
      const j = await post('/api/public/check', { sid }); if (!j) return;
      ST.check = j; ST.step = 'confirm'; return render();
    }
    if (ST.step === 'confirm') { ST.step = 'pw'; return render(); }
    const password = $('#pw').value;
    if (!c.hasPassword) {
      if (password.length < 6) return toast(T('The password needs at least 6 characters.', 'Mật khẩu cần ít nhất 6 ký tự.'));
      if (password !== $('#pw2').value) return toast(T('The two passwords are different.', 'Hai lần nhập mật khẩu không giống nhau.'));
    }
    if (!await post('/api/public/login', { sid: c.sid, password })) return;
    ST.step = 'sid'; ST.check = null; reload();
  };
  $('#go').onclick = go;
  app.querySelectorAll('input').forEach(i => i.onkeydown = e => { if (e.key === 'Enter') go(); });
  const back = $('#back'); if (back) back.onclick = e => { e.preventDefault(); ST.step = 'sid'; render(); };
  const f = app.querySelector('#pw') || app.querySelector('#sid'); if (f) f.focus();
}

function renderPick(app, head) {
  const M = ST.me;
  app.innerHTML = head + `<main><div class="card who"><div class="nm">${esc(M.name)}</div><div class="sub">${esc(M.sid)}</div></div>
    <h2>${T('Choose your class', 'Chọn lớp')}</h2>
    ${M.classes.map(c => `<button class="big" data-pick="${c.id}"><b>${esc(c.name)}</b> · ${esc(c.courseName)}<br><small>${esc(c.term)}</small></button>`).join('')}
    ${M.classes.length ? '' : `<p class="muted">${T('You are not in any class at the moment.', 'Hiện bạn chưa có trong lớp nào.')}</p>`}
    <div class="btns"><button id="out">${T('Sign out', 'Đăng xuất')}</button></div></main>`;
  bindLangToggle(app);
  app.querySelectorAll('[data-pick]').forEach(b => b.onclick = () => pick(b.dataset.pick));
  $('#out').onclick = signOut;
}
async function signOut() { await post('/api/public/logout', {}); ST.me = null; ST.info = null; ST.step = 'sid'; render(); }

function render() {
  document.documentElement.lang = LANG;
  document.title = T('Lab – Student', 'Lab – Sinh viên');
  const app = $('#app');
  const head = `<header><div class="row"><h1>${ST.info ? esc(ST.info.courseName) : 'Lab'}</h1>${langToggle()}</div></header>`;
  if (!ST.me) return renderSignIn(app, head);
  if (!ST.info) return renderPick(app, head);
  const I = ST.info;
  let h = head + `<main><div class="card who"><div class="nm">${esc(I.name)}</div>
    <div class="sub">${esc(I.sid)} | ${esc(I.className)} | ${esc(I.term)}</div>`;
  if (I.team) {
    h += `<div class="teambig"><div><b>${I.team}</b>${T('Team / bench', 'Nhóm / cụm máy')}</div><div><b>${I.member}</b>${T('Member', 'Thành viên')}</div><div><b>${I.variant}</b>${T('Variant', 'Mã đề')}</div></div>
      <div class="sub">${T('Your team', 'Cùng nhóm')}: ${I.teammates.length ? I.teammates.map(esc).join(', ') : '–'}</div>`;
  } else {
    h += `<p class="muted">${T('You are not in a team yet. Ask the lecturer.', 'Bạn chưa có nhóm. Hỏi giảng viên.')}</p>`;
  }
  h += `</div>`;
  let shown = 0, sum = 0, total = 0;
  I.labs.forEach(L => {
    if (!L.card && L.marks === null && !L.submit && !(L.review && L.review.length)) return;
    shown++;
    h += `<div class="card lab"><h3>Lab ${L.lab}</h3>`;
    if (L.card) h += `<div class="lines">${L.card.map(l => `<div>${sub(l)}</div>`).join('')}</div>`;
    (L.figs || []).forEach(f => { h += `<img src="${f}" alt="${T('Circuit', 'Sơ đồ mạch')}" class="fig">`; });
    if (L.image) h += `<img src="${L.image}" alt="Oscilloscope screen">`;
    (L.files || []).forEach(f => { h += `<p><a class="dl" href="${f.url}" download>⬇ ${esc(T(f.label[0], f.label[1]))}</a></p>`; });
    if (L.marks !== null) { sum += L.marks; total += L.total;
      h += `<div class="marks">${T('Marks', 'Điểm')}: <b>${L.marks}</b> / ${L.total}</div>`; }
    if (L.submit) h += submitForm(L);
    else if (L.review && L.review.length) h += `<div class="submit">${valueFields(L, true)}</div>`;
    h += `</div>`;
  });
  if (!shown) h += `<p class="muted">${T('Nothing to show yet. Your card appears when the lab starts.', 'Chưa có gì để hiện. Đề sẽ hiện khi bắt đầu buổi lab.')}</p>`;
  if (total) h += `<p class="muted">${T(`Released labs: <b>${sum}</b> / ${total}. These marks are provisional – the official marks are on Canvas.`, `Các lab đã công bố: <b>${sum}</b> / ${total}. Điểm này để tham khảo – điểm chính thức trên Canvas.`)}</p>`;
  h += `<div class="btns"><button class="on" id="ref">${T('Refresh', 'Tải lại')}</button>${ST.me.classes.length > 1 ? `<button id="other">${T('Other class', 'Lớp khác')}</button>` : ''}<button id="out">${T('Sign out', 'Đăng xuất')}</button></div></main>`;
  app.innerHTML = h;
  bindLangToggle(app);
  app.querySelectorAll('.submit input[inputmode="decimal"]').forEach(i => i.oninput = () => cacheDrafts());
  app.querySelectorAll('[data-send]').forEach(b => b.onclick = async () => {
    const lab = b.dataset.send, box = b.closest('.submit');
    const values = [...box.querySelectorAll('input[inputmode="decimal"]')].map(i => i.value.trim());
    if (values.some(v => v !== '' && isNaN(+v.replace(',', '.')))) { toast(T('Numbers only, please.', 'Chỉ nhập số.')); return; }
    b.disabled = true;
    const j = await post('/api/public/submit', { cls: I.id, lab, values });
    b.disabled = false;
    if (!j) return;
    clearDraft(lab); toast(T('Submitted', 'Đã nộp')); reload();
  });
  app.querySelectorAll('[data-unsubmit]').forEach(b => b.onclick = async () => {
    if (!confirm(T('Unsubmit so you can edit? Call the lecturer again after you resubmit.', 'Hủy nộp để sửa? Sau khi nộp lại phải gọi giảng viên xác nhận lại.'))) return;
    b.disabled = true;
    const j = await post('/api/public/unsubmit', { cls: I.id, lab: b.dataset.unsubmit });
    b.disabled = false;
    if (!j) return;
    toast(T('Unsubmitted – you can edit now', 'Đã hủy nộp – có thể sửa')); reload();
  });
  app.querySelectorAll('[data-photo]').forEach(inp => inp.onchange = async () => {
    const f = inp.files[0]; if (!f) return;
    cacheDrafts();
    toast(T('Uploading…', 'Đang gửi ảnh…'));
    let data; try { data = await shrink(f); } catch (e) { toast(T('Could not read the photo', 'Không đọc được ảnh')); return; }
    const j = await post('/api/public/photo', { cls: I.id, lab: inp.dataset.photo, data });
    if (!j) return;
    toast(T('Photo saved', 'Đã lưu ảnh')); reload();
  });
  app.querySelectorAll('[data-delph]').forEach(b => b.onclick = async () => {
    if (!confirm(T('Delete this photo?', 'Xóa ảnh này?'))) return;
    cacheDrafts();
    if (await post('/api/public/photo_delete', { cls: I.id, lab: b.dataset.lab, id: +b.dataset.delph })) reload();
  });
  $('#ref').onclick = async () => { cacheDrafts(); if (await reload()) toast(T('Updated', 'Đã cập nhật')); };
  $('#out').onclick = signOut;
  const other = $('#other'); if (other) other.onclick = () => { ST.info = null; ST.cls = ''; try { localStorage.removeItem('student_cls'); } catch (e) {} render(); };
}

reload();

// measured-value fields; when marks are released, color the field and show the key under it
function valueFields(L, frozen) {
  const S_ = L.submit, rev = L.review || [];
  const vals = S_ ? formValues(L.lab, S_.values, frozen) : rev.map(r => r.yours == null ? '' : String(r.yours));
  const qs = S_ ? S_.questions : rev.map(r => [r.label, r.unit]);
  let h = qs.map((q, i) => {
    const r = rev[i], cls = r ? (r.ok ? 'ok' : 'bad') : '';
    return `<label class="val ${cls}">${sub(q[0])} <small>(${esc(q[1])})</small>
      <input inputmode="decimal" ${frozen ? 'disabled' : ''} value="${esc(vals[i] ?? '')}" placeholder="${T('number', 'số')}">
      ${r ? `<span class="keyline">${T('Key', 'Đáp án')}: <b>${fmt(r.key)}</b></span>` : ''}</label>`;
  }).join('');
  if (rev.length) h += `<p class="muted">${T('Green = within ±10% of the key. Red = outside that (including near-miss).', 'Xanh = trong khoảng ±10% đáp án. Đỏ = ngoài khoảng đó (kể cả gần đúng).')}</p>`;
  return h;
}

// values form: edit while drafting; after submit view-only until Unsubmit; after lecturer tick view-only forever
function submitForm(L) {
  const S_ = L.submit, frozen = !!(S_.locked || S_.submitted || L.review);
  let h = `<div class="submit">`;
  if (!S_.locked && !L.review) h += `<div class="howto"><b>${T('How to finish this lab', 'Cách kết thúc lab này')}</b>
    <ol>
      <li>${T('Measure on your bench, type the values below, take <b>one photo of your circuit</b> (breadboard), then <span class="nowrap">tap <b>Submit.</b></span>', 'Đo trên cụm máy, nhập số vào các ô bên dưới, chụp <b>đúng một ảnh mạch</b> (breadboard), rồi <span class="nowrap">bấm <b>Nộp.</b></span>')}</li>
      <li>${T('To change after submitting: tap <b>Unsubmit</b>, edit, then submit again.', 'Muốn sửa sau khi đã nộp: bấm <b>Hủy nộp</b>, sửa, rồi nộp lại.')}</li>
      <li>${T('<b>Call the lecturer or TA to your bench.</b> Do not pack up or leave until they have ticked you. Submitting on the phone alone is not enough.', '<b>Gọi giảng viên hoặc TA xuống cụm máy của bạn.</b> Chưa được tháo mạch / về khi họ chưa tick. Chỉ nộp trên điện thoại là chưa đủ.')}</li>
      <li>${T('They will check the number <span class="nowrap">on the <b>instrument</b></span> (must match what you submitted), your circuit and photo, then confirm at your bench. Only after that confirmation do your measured values count for marks.', 'Họ sẽ kiểm tra số <span class="nowrap">trên <b>máy đo</b></span> (khớp với số bạn nộp), mạch và ảnh của bạn, rồi xác nhận tại cụm máy. Chỉ sau khi được xác nhận thì số đo mới tính điểm.')}</li>
    </ol></div>`;
  h += `<div class="subhead">${T('Your measured values', 'Số liệu đo của bạn')}</div>`;
  if (S_.locked) h += `<p class="ok">${T('Checked by the lecturer – locked. You may pack up.', 'Giảng viên đã xác nhận (đã tick) – đã khóa. Bạn có thể tháo mạch.')}</p>`;
  else if (S_.submitted) h += `<p class="ok">${T('Submitted. Unsubmit if you need to edit.', 'Đã nộp. Muốn sửa thì bấm Hủy nộp.')}</p>`;
  h += valueFields(L, frozen);
  const P = S_.photos || [];
  h += `<div class="subhead">${T('Photo of your circuit (required, one only)', 'Ảnh mạch thật (bắt buộc, đúng 1 tấm)')}</div>`;
  if (!P.length) h += `<p class="zero">${T('No photo yet. Take one photo of your breadboard.', 'Chưa có ảnh. Chụp đúng một tấm breadboard.')}</p>`;
  h += `<div class="thumbs">${P.map(p => `<div class="th"><a href="${p.url}" target="_blank"><img src="${p.url}" alt="photo"></a>${frozen ? '' : `<button data-delph="${p.id}" data-lab="${L.lab}" title="${T('Delete', 'Xóa')}">×</button>`}</div>`).join('')}</div>`;
  if (!frozen && P.length < 1) h += `<label class="btn pri photo-btn">${T('Take / choose a photo', 'Chụp / chọn ảnh')}<input type="file" accept="image/*" capture="environment" data-photo="${L.lab}" hidden></label>`;
  if (S_.locked || L.review) { /* view only */ }
  else if (S_.submitted) h += `<button class="big" data-unsubmit="${L.lab}">${T('Unsubmit to edit', 'Hủy nộp để sửa')}</button>`;
  else h += `<button class="big on" data-send="${L.lab}">${T('Submit', 'Nộp')}</button>`;
  if (S_.time) h += `<p class="muted">${T('Last submitted', 'Nộp lần cuối')}: ${esc(S_.time)}</p>`;
  if (!frozen) h += `<p class="muted">${T('Use real measured values, in the unit shown.', 'Dùng số đo thật, đúng đơn vị ghi bên cạnh.')}</p>`;
  h += `</div>`;
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
