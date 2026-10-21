// Sign-in (username + password), first-time setup of the admin account, the account menu (change password, sign out).
const ROLE = r => ({admin:T('Admin','Admin'), lecturer:T('Lecturer','Giảng viên'), ta:T('TA','Trợ giảng (TA)')})[r]||r;
function renderLogin(app){
  app.innerHTML = `<div class="login card" id="lg"><h2>${T('Lab grading','Chấm Lab')}</h2><p class="muted">${T('Connecting…','Đang kết nối…')}</p></div>`;
  fetch('/api/status').then(r=>r.json()).then(st=>{
    if(st.me) return boot();
    const setup=st.needSetup;
    $('#lg').innerHTML = `<div class="login-lang">${langToggle()}</div>
      <h2>${setup?T('First start: create the admin account','Lần đầu: tạo tài khoản admin'):T('Sign in','Đăng nhập')}</h2>
      ${setup?`<p class="muted">${T('The admin creates the accounts of lecturers and TAs.','Admin tạo tài khoản cho giảng viên và TA.')}</p>`:''}
      <label class="fl">${T('Username','Username')}<input id="u" autocomplete="username" autocapitalize="none" value="${setup?'admin':''}"></label>
      ${setup?`<label class="fl">${T('Your name','Họ tên')}<input id="n" autocomplete="name"></label>`:''}
      <label class="fl">${T('Password','Mật khẩu')}<input id="p" type="password" autocomplete="${setup?'new-password':'current-password'}"></label>
      ${setup?`<label class="fl">${T('Password again','Nhập lại mật khẩu')}<input id="p2" type="password" autocomplete="new-password"></label>
               <p class="muted">${T('At least 8 characters.','Ít nhất 8 ký tự.')}</p>`:''}
      <button class="big on" id="go">${setup?T('Create and sign in','Tạo và đăng nhập'):T('Sign in','Đăng nhập')}</button>
      <p style="text-align:center"><a href="#" id="qrl">${T('QR code to open on a phone','Mã QR để mở trên điện thoại')}</a></p>`;
    bindLangToggle($('#lg'));
    $('#qrl').onclick=e=>{e.preventDefault(); showQR();};
    const go=()=>{
      const username=$('#u').value.trim().toLowerCase(), password=$('#p').value;
      if(setup && password!==$('#p2').value) return toast(T('The two passwords are different.','Hai lần nhập mật khẩu không giống nhau.'));
      api(setup?'/api/setup':'/api/login', setup?{username, name:$('#n').value.trim(), password}:{username, password}).then(boot).catch(()=>{});
    };
    $('#go').onclick=go; $('#lg').querySelectorAll('input').forEach(i=>i.onkeydown=e=>{if(e.key==='Enter')go()}); $('#u').focus();
  });
}
async function boot(){ S.keys=await api('/api/keys'); S.data=await api('/api/data'); render(); }

function showAccount(){
  const me=ME(), d=document.createElement('div'); d.className='modal';
  d.innerHTML=`<div class="box" style="text-align:left"><h2 style="margin-top:0">${esc(me.name||me.username)}</h2>
    <p class="muted">${esc(me.username)} · ${ROLE(me.role)}</p>
    <h2>${T('Change my password','Đổi mật khẩu')}</h2>
    <label class="fl">${T('Current password','Mật khẩu hiện tại')}<input type="password" id="pw0" autocomplete="current-password"></label>
    <label class="fl">${T('New password (8+ characters)','Mật khẩu mới (từ 8 ký tự)')}<input type="password" id="pw1" autocomplete="new-password"></label>
    <label class="fl">${T('New password again','Nhập lại mật khẩu mới')}<input type="password" id="pw2" autocomplete="new-password"></label>
    <div class="btns"><button class="on" id="pwsave">${T('Save password','Lưu mật khẩu')}</button></div>
    <div class="btns" style="margin-top:14px"><button class="btn warn" id="out">${T('Sign out','Đăng xuất')}</button><button id="close">${T('Close','Đóng')}</button></div></div>`;
  document.body.appendChild(d);
  d.onclick=e=>{ if(e.target===d) d.remove(); }; $('#close').onclick=()=>d.remove();
  $('#pwsave').onclick=async()=>{ if($('#pw1').value!==$('#pw2').value) return toast(T('The two passwords are different.','Hai lần nhập mật khẩu không giống nhau.'));
    await api('/api/password',{old:$('#pw0').value, new:$('#pw1').value}); toast(T('Password changed','Đã đổi mật khẩu')); d.remove(); };
  $('#out').onclick=async()=>{ await api('/api/logout',{}).catch(()=>{}); d.remove(); S.data=null; render(); };
}
