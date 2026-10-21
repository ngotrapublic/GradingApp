// QR code popup with the phone address.
async function showQR(forStudents){
  const r=await fetch('/api/qr.svg'+(forStudents===true?'?target=student':'')); const d=document.createElement('div'); d.className='modal';
  if(!r.ok){ const j=await r.json().catch(()=>({})); d.innerHTML=`<div class="box"><p>${esc((LANG==='vi'&&j.error_vi)||j.error||T('Could not create the QR code','Không tạo được mã QR'))}</p><button class="btn pri">${T('Close','Đóng')}</button></div>`; }
  else { const url=r.headers.get('X-Url'); const svg=URL.createObjectURL(await r.blob());
    d.innerHTML=`<div class="box"><h2 style="margin-top:0">${forStudents===true?T('Students: your team, card and marks','Sinh viên: nhóm, đề và điểm'):T('Open on a phone','Mở trên điện thoại')}</h2><p class="muted">${forStudents===true?T('Scan the code, type your student ID and your password.','Quét mã, nhập MSSV và mật khẩu.'):T('Open the phone camera and scan:','Mở camera điện thoại và quét mã:')}${/^http:/.test(url)?' '+T('(this laptop address works only on the <b>same Wi-Fi</b>)','(địa chỉ laptop này chỉ dùng được khi <b>cùng wifi</b>)'):''}</p>
      <img src="${svg}" alt="QR"><p><b>${esc(url)}</b></p><button class="btn pri">${T('Close','Đóng')}</button></div>`; }
  d.onclick=e=>{ if(e.target===d||e.target.tagName==='BUTTON') d.remove(); }; document.body.appendChild(d);
}
