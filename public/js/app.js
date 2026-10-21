// Page frame: header (class picker, language, QR, account), tabs, lab selector. Loaded last.
function render(){
  const app=$('#app');
  document.documentElement.lang=LANG;
  if(!S.data){ return renderLogin(app); }
  const ids=Object.keys(S.data.classes);
  if(!S.data.classes[S.cls]) S.cls=ids[0]||'';
  const hasCls=!!S.cls, me=ME(), staffOnly=me.role==='ta';
  const tabs=[];
  if(hasCls) tabs.push(['grade',T('Grade','Chấm')]);
  if(hasCls && canManage()) tabs.push(['sum',T('Canvas','Gửi Canvas')],['roster',T('Students','SV & nhóm')]);
  if(!staffOnly) tabs.push(['classes',T('Classes','Lớp')]);
  if(me.role==='admin') tabs.push(['users',T('Accounts','Tài khoản')]);
  if(!tabs.some(t=>t[0]===S.view)) S.view=tabs.length? tabs[0][0] : 'none';
  // class picker, grouped by term (newest first)
  const terms=[...new Set(ids.map(i=>S.data.classes[i].term))].sort(termOrder);
  const opts=terms.map(t=>`<optgroup label="${esc(t)}">${ids.filter(i=>S.data.classes[i].term===t).map(i=>{ const c=S.data.classes[i];
    return `<option value="${i}" ${i===S.cls?'selected':''}>${esc(c.name)} · ${esc(c.course)} · ${esc(c.term)}${c.role==='ta'?' (TA)':''}</option>`; }).join('')}</optgroup>`).join('');
  app.innerHTML = `<header><div class="row"><h1>${T('Lab grading','Chấm Lab')}</h1>${langToggle()}<button class="qrbtn" id="qr" title="${T('QR code to open on a phone','Mã QR để mở trên điện thoại')}">QR</button>
      <button class="qrbtn" id="acct" title="${esc(me.username)}">👤</button></div>
    ${hasCls?`<div class="row" style="margin-top:8px"><select id="cls" style="flex:1;max-width:none">${opts}</select></div>`:''}
    <nav>${tabs.map(([k,t])=>`<button data-v="${k}" class="${S.view===k?'on':''}">${t}</button>`).join('')}</nav></header><main id="main"></main>`;
  if(hasCls) $('#cls').onchange=e=>{S.cls=e.target.value;localStorage.setItem('cls',S.cls);S.open=null;S.preview=null;S.draft=null;S.gbNew=null;
    if(!labs().includes(S.lab)) S.lab=labs()[0]; render();};
  app.querySelectorAll('nav button').forEach(b=>b.onclick=()=>{S.view=b.dataset.v;S.preview=null;render();});
  $('#qr').onclick=showQR; $('#acct').onclick=showAccount; bindLangToggle(app);
  if(hasCls && !labs().includes(S.lab)) S.lab=labs()[0];
  const view={grade:renderGrade, roster:renderRoster, sum:renderSum, classes:renderClasses, users:renderUsers}[S.view];
  if(view) view($('#main'));
  else $('#main').innerHTML=`<p class="muted">${T('You are not in any class yet. Ask the lecturer to add you as a TA.','Bạn chưa được thêm vào lớp nào. Nhờ giảng viên thêm bạn làm TA.')}</p>`;
}
// "Fall 2027" > "Summer 2027" > "Spring 2027" > "Fall 2026" … (newest first)
function termOrder(a,b){ const k=t=>{ const m=/(spring|summer|fall)\s*(\d{4})/i.exec(t||''); return m? +m[2]*3+['spring','summer','fall'].indexOf(m[1].toLowerCase()) : -1; };
  return k(b)-k(a) || String(a).localeCompare(String(b)); }
function labSeg(){ return `<div class="seg">${labs().map(l=>`<button data-l="${l}" class="${S.lab===l?'on':''}">Lab ${l}</button>`).join('')}</div>`; }
function bindSeg(root, cb){ root.querySelectorAll('.seg button').forEach(b=>b.onclick=()=>{S.lab=b.dataset.l;localStorage.setItem('lab',S.lab);S.open=null;S.preview=null;cb?cb():render();}); }

document.title=T('Lab grading','Chấm Lab');
render();
