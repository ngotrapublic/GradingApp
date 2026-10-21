// Tab "Accounts" (admin only): create lecturer / TA / admin accounts, change role, lock, set a new password.
async function renderUsers(m){
  await loadUsers();
  const me=ME(), roleSel=(cur,attr)=>`<select ${attr}>${['lecturer','ta','admin'].map(r=>`<option value="${r}" ${r===cur?'selected':''}>${ROLE(r)}</option>`).join('')}</select>`;
  m.innerHTML=`<h2>${T('Create an account','Tạo tài khoản')}</h2><div class="card pad">
      <div class="two"><label class="fl">${T('Username (a–z, 0–9, . - _)','Username (a–z, 0–9, . - _)')}<input id="nu-u" autocapitalize="none"></label>
        <label class="fl">${T('Role','Vai trò')}${roleSel('lecturer','id="nu-r"')}</label></div>
      <label class="fl">${T('Full name','Họ tên')}<input id="nu-n"></label>
      <label class="fl">${T('First password (8+ characters) – give it to the person, they can change it','Mật khẩu ban đầu (từ 8 ký tự) – gửi cho người đó, họ tự đổi sau')}<input id="nu-p" autocomplete="new-password"></label>
      <div class="btns"><button class="on" id="nu-go">${T('Create account','Tạo tài khoản')}</button><button id="nu-gen">${T('Make a random password','Tạo mật khẩu ngẫu nhiên')}</button></div></div>
    <h2>${T('Accounts','Tài khoản')} (${S.users.length})</h2>
    <div class="card scroll"><table><tr><th>Username</th><th>${T('Name','Họ tên')}</th><th>${T('Role','Vai trò')}</th><th>${T('Active','Hoạt động')}</th><th></th></tr>
    ${S.users.map(u=>`<tr data-u="${u.id}"><td>${esc(u.username)}</td><td>${esc(u.name)}</td>
      <td>${u.id===me.id?ROLE(u.role):roleSel(u.role,'data-role')}</td>
      <td>${u.id===me.id?'✓':`<input type="checkbox" data-active ${u.active?'checked':''}>`}</td>
      <td><button class="btn" data-pw style="padding:3px 8px">${T('New password','Đặt lại MK')}</button></td></tr>`).join('')}</table></div>
    <p class="muted">${T('A locked account cannot sign in. Lecturers see only their own classes; a TA sees the classes a lecturer added them to.','Tài khoản bị khóa không đăng nhập được. Giảng viên chỉ thấy lớp của mình; TA chỉ thấy lớp được giảng viên thêm vào.')}</p>`;
  $('#nu-gen').onclick=()=>{ const a='abcdefghjkmnpqrstuvwxyz23456789'; $('#nu-p').value=Array.from(crypto.getRandomValues(new Uint8Array(10)),x=>a[x%a.length]).join(''); };
  $('#nu-go').onclick=async()=>{ await api('/api/user_create',{username:$('#nu-u').value.trim().toLowerCase(), name:$('#nu-n').value.trim(), role:$('#nu-r').value, password:$('#nu-p').value});
    toast(T('Account created','Đã tạo tài khoản')); renderUsers(m); };
  const upd=async(el,body)=>{ await api('/api/user_update',{id:+el.closest('[data-u]').dataset.u, ...body}); toast(T('Saved','Đã lưu')); renderUsers(m); };
  m.querySelectorAll('[data-role]').forEach(s=>s.onchange=()=>upd(s,{role:s.value}));
  m.querySelectorAll('[data-active]').forEach(c=>c.onchange=()=>upd(c,{active:c.checked}));
  m.querySelectorAll('[data-pw]').forEach(b=>b.onclick=()=>{ const p=prompt(T('New password for this account (8+ characters):','Mật khẩu mới cho tài khoản này (từ 8 ký tự):')); if(p) upd(b,{password:p}); });
}
