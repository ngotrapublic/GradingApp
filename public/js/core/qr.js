// QR code popup with the phone address.
async function showQR(forStudents){
  const r=await fetch('/api/qr.svg'+(forStudents===true?'?target=student':'')); const d=document.createElement('div'); d.className='modal';
  if(!r.ok){ const j=await r.json().catch(()=>({})); d.innerHTML=`<div class="box"><p>${esc((LANG==='vi'&&j.error_vi)||j.error||T('Could not create the QR code','Không tạo được mã QR'))}</p><button class="btn pri">${T('Close','Đóng')}</button></div>`; }
  else { const url=r.headers.get('X-Url'); const svg=URL.createObjectURL(await r.blob());
    d.innerHTML=`<div class="box"><h2 style="margin-top:0">${forStudents===true?T('Students: your team, card and marks','Sinh viên: nhóm, đề và điểm'):T('Open on a phone','Mở trên điện thoại')}</h2><p class="muted">${forStudents===true?T('Connect to the <b>lab Wi-Fi</b>, scan the code and type your student ID.','Kết nối <b>wifi phòng lab</b>, quét mã rồi nhập MSSV.'):T('The phone must be on the <b>same Wi-Fi</b> as the computer running this page. Open the camera and scan:','Điện thoại phải dùng <b>cùng wifi</b> với máy chạy web. Mở camera, quét mã:')}</p>
      <img src="${svg}" alt="QR"><p><b>${esc(url)}</b></p><button class="btn pri">${T('Close','Đóng')}</button></div>`; }
  d.onclick=e=>{ if(e.target===d||e.target.tagName==='BUTTON') d.remove(); }; document.body.appendChild(d);
}
