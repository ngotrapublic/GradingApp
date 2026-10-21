// PIN screen and start-up.
function renderLogin(app){
  app.innerHTML = `<div class="login card" id="lg"><h2>${T('Electric Circuit Lab – grading','Electric Circuit Lab – chấm điểm')}</h2><p class="muted" id="msg">${T('Connecting…','Đang kết nối…')}</p></div>`;
  fetch('/api/status').then(r=>r.json()).then(st=>{
    if(st.authed) return boot();
    $('#lg').innerHTML = `<div class="login-lang">${langToggle()}</div>
      <h2>${st.hasPin?T('Enter PIN','Nhập PIN'):T('Set a PIN (first time)','Đặt PIN lần đầu')}</h2>
      <p class="muted">${st.pinFromServer?T('The PIN is set in the server settings (LECTURER_PIN).','PIN được đặt trong cấu hình server (LECTURER_PIN).'):st.hasPin?T('The PIN is set by the lecturer.','PIN do giảng viên đặt.'):T('The PIN protects this page. At least 8 characters.','PIN dùng để vào trang chấm. Ít nhất 8 ký tự.')}</p>
      <input id="pin" type="password" inputmode="numeric" autocomplete="current-password">
      <button class="big on" id="go">${st.hasPin?T('Sign in','Vào'):T('Save PIN','Lưu PIN')}</button>
      <p style="text-align:center"><a href="#" id="qrl">${T('QR code to open on a phone','Mã QR để mở trên điện thoại')}</a></p>`;
    bindLangToggle($('#lg'));
    $('#qrl').onclick=e=>{e.preventDefault(); showQR();};
    const go=()=>api(st.hasPin?'/api/login':'/api/setpin',{pin:$('#pin').value}).then(boot).catch(()=>{});
    $('#go').onclick=go; $('#pin').onkeydown=e=>{if(e.key==='Enter')go()}; $('#pin').focus();
  });
}
async function boot(){ S.keys=await api('/api/keys'); S.data=await api('/api/data'); if(!S.data.classes[S.cls]) S.cls='1'; render(); }
