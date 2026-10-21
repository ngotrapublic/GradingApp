// Sign-in (username + password), first-time setup of the admin account, the account menu (change password, sign out).
const ROLE = r => ({admin:T('Admin','Admin'), lecturer:T('Lecturer','Giảng viên'), ta:T('TA','Trợ giảng (TA)')})[r]||r;
function renderLogin(app){
  app.innerHTML = `<div class="login card" id="lg"><h2>${T('Lab grading','Chấm Lab')}</h2><p class="muted">${T('Connecting…','Đang kết nối…')}</p></div>`;
  fetch('/api/status').then(r=>r.json()).then(st=>{
    if(st.me) return boot();
    $('#lg').innerHTML = `<div class="login-lang">${langToggle()}</div>
      <h2>${T('Sign in','Đăng nhập')}</h2>
      <label class="fl">${T('Username','Username')}<input id="u" autocomplete="username" autocapitalize="none"></label>
      <label class="fl">${T('Password','Mật khẩu')}<input id="p" type="password" autocomplete="current-password"></label>
      <button class="big on" id="go">${T('Sign in','Đăng nhập')}</button>
      <p style="text-align:center"><a href="#" id="qrl">${T('QR code to open on a phone','Mã QR để mở trên điện thoại')}</a></p>`;
    bindLangToggle($('#lg'));
    $('#qrl').onclick=e=>{e.preventDefault(); showQR();};
    const go=()=>api('/api/login',{username:$('#u').value.trim().toLowerCase(), password:$('#p').value}).then(boot).catch(()=>{});
    $('#go').onclick=go; $('#lg').querySelectorAll('input').forEach(i=>i.onkeydown=e=>{if(e.key==='Enter')go()}); $('#u').focus();
  });
}
// first sign-in with a password someone else gave (default admin, new account, reset): choose your own before anything else
function renderChangePw(app){
  const me=ME();
  app.innerHTML = `<div class="login card" id="lg"><div class="login-lang">${langToggle()}</div>
    <h2>${T('Choose your own password','Đặt mật khẩu của bạn')}</h2>
    <p class="muted">${esc(me.username)} · ${ROLE(me.role)}</p>
    <p class="muted">${T('You signed in with a password given to you. Choose a new one (at least 8 characters) to continue.','Bạn vừa đăng nhập bằng mật khẩu được cấp. Đặt mật khẩu mới (ít nhất 8 ký tự) để tiếp tục.')}</p>
    <label class="fl">${T('Current password','Mật khẩu hiện tại')}<input type="password" id="pw0" autocomplete="current-password"></label>
    <label class="fl">${T('New password','Mật khẩu mới')}<input type="password" id="pw1" autocomplete="new-password"></label>
    <label class="fl">${T('New password again','Nhập lại mật khẩu mới')}<input type="password" id="pw2" autocomplete="new-password"></label>
    <button class="big on" id="go">${T('Save and continue','Lưu và tiếp tục')}</button>
    <p style="text-align:center"><a href="#" id="out">${T('Sign out','Đăng xuất')}</a></p></div>`;
  bindLangToggle($('#lg'));
  const go=async()=>{ if($('#pw1').value!==$('#pw2').value) return toast(T('The two passwords are different.','Hai lần nhập mật khẩu không giống nhau.'));
    await api('/api/password',{old:$('#pw0').value, new:$('#pw1').value}); toast(T('Password changed','Đã đổi mật khẩu')); boot(); };
  $('#go').onclick=()=>go().catch(()=>{}); $('#lg').querySelectorAll('input').forEach(i=>i.onkeydown=e=>{if(e.key==='Enter')go().catch(()=>{})});
  $('#out').onclick=async e=>{ e.preventDefault(); await api('/api/logout',{}).catch(()=>{}); S.data=null; render(); };
  $('#pw0').focus();
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
