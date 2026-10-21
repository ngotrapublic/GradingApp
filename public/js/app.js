// Page frame: header, language toggle, tabs, lab selector. Loaded last.
function render(){
  const app=$('#app');
  document.documentElement.lang=LANG;
  if(!S.data){ return renderLogin(app); }
  const cls = Object.entries(S.data.classes).map(([k,c])=>`<option value="${k}" ${k===S.cls?'selected':''}>${esc(c.name)}</option>`).join('');
  const tabs=[['grade',T('Grade','Chấm')],['sum',T('Canvas','Gửi Canvas')],['roster',T('Class','Lớp & nhóm')]];
  app.innerHTML = `<header><div class="row"><h1>${T('Lab grading','Chấm Lab')}</h1>${langToggle()}<button class="qrbtn" id="qr" title="${T('QR code to open on a phone','Mã QR để mở trên điện thoại')}">QR</button><select id="cls">${cls}</select></div>
    <nav>${tabs.map(([k,t])=>`<button data-v="${k}" class="${S.view===k?'on':''}">${t}</button>`).join('')}</nav></header><main id="main"></main>`;
  $('#cls').onchange=e=>{S.cls=e.target.value;localStorage.setItem('cls',S.cls);S.open=null;S.preview=null;S.draft=null;S.gbNew=null;render();};
  app.querySelectorAll('nav button').forEach(b=>b.onclick=()=>{S.view=b.dataset.v;S.preview=null;render();});
  $('#qr').onclick=showQR; bindLangToggle(app);
  ({grade:renderGrade, roster:renderRoster, sum:renderSum})[S.view]($('#main'));
}
function labSeg(){ return `<div class="seg">${['1','2','3','4'].map(l=>`<button data-l="${l}" class="${S.lab===l?'on':''}">Lab ${l}</button>`).join('')}</div>`; }
function bindSeg(root, cb){ root.querySelectorAll('.seg button').forEach(b=>b.onclick=()=>{S.lab=b.dataset.l;localStorage.setItem('lab',S.lab);S.open=null;S.preview=null;cb?cb():render();}); }

document.title=T('Lab grading – Electric Circuit Lab','Chấm Lab – Electric Circuit Lab');
render();
