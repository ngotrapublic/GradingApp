// Tab "Grade": students by team, answer key, tick, manual marks.
function renderGrade(m){
  const Lb=L(), st=sorted(), q=S.q.toLowerCase();
  const done=st.filter(s=>rec(s.sid).tick).length, sub_=st.filter(s=>(rec(s.sid).values||[]).some(v=>v!==null&&v!=='')).length;
  let html = labSeg() + `<div class="stats"><div><b>${st.length}</b>${T('students','SV')}</div><div><b>${done}</b>${T('ticked','đã tick')}</div><div><b>${sub_}</b>${T('with data','có số liệu')}</div></div>
    ${(()=>{ const ch=changedSince(S.lab); return ch.length? `<div class="card" style="padding:10px 12px;background:#fff7e0;border-color:#e0a800">${T(`Lab ${S.lab}: <b>${ch.length} student(s)</b> with marks not yet sent to Canvas.`,`Lab ${S.lab}: <b>${ch.length} SV</b> có điểm chưa đưa lên Canvas.`)} <a href="#" id="gosend">${T('Go to Canvas tab →','Gửi Canvas →')}</a></div>`:''; })()}
    ${pubBox()}
    <input type="search" id="q" placeholder="${T('Search name / student ID / variant','Tìm tên / MSSV / mã đề')}" value="${esc(S.q)}" style="margin-bottom:10px">`;
  if(!st.length) html += `<p class="muted">${T('No students yet. Go to the <b>Class</b> tab to import the class list.','Chưa có danh sách SV. Vào tab <b>Lớp &amp; nhóm</b> để nhập danh sách.')}</p>`;
  const teams={}; st.forEach(s=>{ const k=s.team||'–'; (teams[k]=teams[k]||[]).push(s); });
  for(const [t, arr] of Object.entries(teams)){
    const vis = arr.filter(s=>!q || s.name.toLowerCase().includes(q) || s.sid.toLowerCase().includes(q) || String(variant(s)||'').includes(q));
    if(!vis.length) continue;
    let head = `<div class="team"><span class="sp">${t==='–'?T('No team','Chưa có nhóm'):T('Team ','Nhóm ')+t}</span>`;
    Lb.manual.filter(x=>x[3]==='team').forEach(mn=>{ if(t==='–') return; const cur=teamRec(t)[mn[0]];
      head += `<span class="lbl">${esc(manLabel(mn))}</span>` + mn[2].map(v=>`<button class="btn ${+cur===v&&cur!==undefined?'pri':''}" data-team="${t}" data-f="${mn[0]}" data-val="${v}" style="padding:4px 9px">${v}</button>`).join(''); });
    head += `</div>`;
    html += `<div class="card">${head}` + vis.map(s=>{
      const v=variant(s), r=rec(s.sid), sc=score(s);
      let row = `<div class="st" data-sid="${esc(s.sid)}"><div class="nm"><b>${esc(s.name)}</b><small>${esc(s.sid)} | ${T('M','TV')} ${s.member||'–'} | ${T('var.','mã')} ${v||'–'}</small></div>
        <span class="chip ${r.tick?'tick':''}">${r.tick?'✓ tick':T('not ticked','chưa tick')}</span><span class="sc">${r.override!=null?'✎ ':''}${sc}</span></div>`;
      if(S.open===s.sid) row += panel(s);
      return row; }).join('') + `</div>`;
  }
  m.innerHTML = html; bindSeg(m);
  if($('#gosend')) $('#gosend').onclick=e=>{e.preventDefault(); S.view='sum'; render();};
  $('#q').oninput=e=>{S.q=e.target.value; const p=e.target.selectionStart; renderGrade(m); const n=$('#q'); n.focus(); n.setSelectionRange(p,p);};
  m.querySelectorAll('.st').forEach(e=>e.onclick=()=>{S.open = S.open===e.dataset.sid? null : e.dataset.sid; renderGrade(m);});
  m.querySelectorAll('[data-team]').forEach(b=>b.onclick=async ev=>{ev.stopPropagation(); const cur=teamRec(b.dataset.team)[b.dataset.f], off=cur!==undefined&&+cur===+b.dataset.val;   // tap the selected mark again = clear it
    S.data=await api('/api/team',{cls:S.cls,lab:S.lab,team:b.dataset.team,field:b.dataset.f,value:off?null:+b.dataset.val}); toast(off?T('Mark cleared','Đã bỏ chọn'):T('Saved','Đã lưu')); renderGrade(m);});
  bindPanel(m);
  m.querySelectorAll('[data-pub]').forEach(c=>c.onchange=async()=>{ S.data=await api('/api/publish',{cls:S.cls,lab:S.lab,[c.dataset.pub]:c.checked});
    toast(c.checked? T('Students can see it now','SV đã xem được') : T('Hidden from students','Đã ẩn với SV')); renderGrade(m); });
  $('#qrs').onclick=()=>showQR(true);
}
// what students may see on the student page, for this class + lab
function pubBox(){
  const p=((C().publish||{})[S.lab])||{};
  const sw=(k,label)=>`<label class="switch"><input type="checkbox" data-pub="${k}" ${p[k]?'checked':''}><span class="knob"></span>${label}</label>`;
  return `<div class="card pubbox"><div class="pubtitle">${T(`Student page – Lab ${S.lab}, ${esc(C().name)}`,`Trang SV – Lab ${S.lab}, ${esc(C().name)}`)}</div>
    <div class="btns">${sw('card',T('Show card','Cho SV xem đề'))}${sw('submit',T('Accept submissions','Nhận bài'))}${sw('marks',T('Show marks','Cho SV xem điểm'))}
    <button class="btn" id="qrs">${T('QR for students','QR cho SV')}</button></div></div>`;
}
function panel(s){
  const Lb=L(), v=variant(s), K=v&&Lb.variants[v], r=rec(s.sid);
  if(!K) return `<div class="panel"><p class="muted">${T('This student has no team / member yet, so no variant. Go to the <b>Class</b> tab.','SV chưa có nhóm / thành viên nên chưa có mã đề. Vào tab <b>Lớp &amp; nhóm</b>.')}</p></div>`;
  const figs=[...(K.figs||[]), ...(S.lab==='3'?[`/api/lab3/${v}.png`]:[])];
  let h = `<div class="panel"><p class="info">${K.info.map(sub).join('<br>')}</p>` +
    (figs.length?`<details class="figs"><summary class="muted">${T('Circuit / task figure','Hình đề bài')}</summary>${figs.map(f=>`<a href="${f}" target="_blank"><img src="${f}" alt=""></a>`).join('')}</details>`:'') + `<div class="scroll"><table><tr><th>${T('Quantity','Đại lượng')}</th><th>${T('Key','Đáp án')}</th><th>±10%</th><th>${T('Submitted','SV nộp')}</th><th>${T('Marks','Điểm')}</th></tr>`;
  Lb.questions.forEach((q,i)=>{ const k=K.keys[i], x=(r.values||[])[i], mk=mark(x,k,q[3]);
    const cl = mk===null?'':(mk===q[3]?'full':(mk>0?'half':'zero'));
    h += `<tr><td>${sub(q[1])}<br><small class="muted">${esc(q[2])}</small></td><td class="num"><b>${fmt(k)}</b></td><td class="num">${fmt(k*0.9)} – ${fmt(k*1.1)}</td>
      <td class="num">${fmt(x)}</td><td class="${cl}">${mk===null?'–':(r.tick?mk:'('+mk+')')}/${q[3]}</td></tr>`; });
  h += `</table></div><button class="big ${r.tick?'on':''}" data-tick="${esc(s.sid)}">${r.tick?T('✓ Ticked – tap to undo','✓ Đã tick – bấm để bỏ'):T('Tick: I saw the reading on the instrument','Tick: đã xem số đo trên máy')}</button>`;
  Lb.manual.filter(x=>x[3]==='student').forEach(mn=>{ const cur=(r.manual||{})[mn[0]];
    h += `<div class="btns"><span class="lbl">${esc(manLabel(mn))}:</span>` + mn[2].map(val=>`<button data-man="${mn[0]}" data-val="${val}" class="${cur!==undefined&&+cur===val?'on':''}">${val}</button>`).join('') + `</div>`; });
  const ph=((C().photos||{})[S.lab]||{})[s.sid]||[];
  h += `<div class="lbl">${T('Photos','Ảnh mạch')} (${ph.length})</div>` + (ph.length? `<div class="thumbs">${ph.map(p=>`<a href="/api/photo/${p.id}.jpg" target="_blank"><img src="/api/photo/${p.id}.jpg" alt="photo"></a>`).join('')}</div>` : `<p class="muted">${T('No photo yet.','Chưa có ảnh.')}</p>`);
  h += `<details><summary class="muted">${T('Enter / edit values by hand (if the student could not submit)','Nhập / sửa số tay (khi SV không nộp được)')}</summary><div class="edit">` +
    Lb.questions.map((q,i)=>`<div><label>${sub(q[1])} (${esc(q[2])})</label><input inputmode="decimal" data-i="${i}" value="${(r.values||[])[i]??''}"></div>`).join('') +
    `</div><div class="btns"><button class="on" data-savevals="${esc(s.sid)}">${T('Save values','Lưu số')}</button></div></details>`;
  const ov=r.override!=null;
  h += `<details ${ov?'open':''}><summary class="muted">${T('Set the score by hand (special cases)','Sửa điểm tay (trường hợp đặc biệt)')}</summary>
    <p class="muted">${T('This score replaces the automatic score everywhere (list, Canvas file, Excel, student page).','Điểm này thay cho điểm tự tính ở mọi nơi (danh sách, file Canvas, Excel, trang SV).')}</p>
    <div class="edit"><div><label>${T('Score','Điểm')} (0–${Lb.total})</label><input inputmode="decimal" data-ov value="${ov?r.override:''}"></div>
    <div><label>${T('Reason','Lý do')}</label><input data-reason value="${esc(r.reason||'')}" placeholder="${T('e.g. make-up session','vd: làm bù')}"></div></div>
    <div class="btns"><button class="on" data-saveov="${esc(s.sid)}">${T('Save score','Lưu điểm')}</button>${ov?`<button data-clearov="${esc(s.sid)}">${T('Back to automatic score','Bỏ điều chỉnh')}</button>`:''}</div></details>`;
  h += `<p class="muted">${T('Total','Tổng')} Lab ${S.lab}: <b>${score(s)}</b>${ov?T(' (set by hand',' (điểm tay')+(r.reason?': '+esc(r.reason):'')+')':''} / ${Lb.total}${(r.src==='manual'?T(' | entered by hand',' | số nhập tay'):(r.src==='web'?T(` | submitted on the web ${esc(r.updated||'')}`,` | SV nộp trên web lúc ${esc(r.updated||'')}`):''))}</p></div>`;
  return h;
}
function bindPanel(m){
  m.querySelectorAll('.panel').forEach(p=>p.onclick=e=>e.stopPropagation());
  m.querySelectorAll('[data-tick]').forEach(b=>b.onclick=async()=>{ const sid=b.dataset.tick; S.data=await api('/api/record',{cls:S.cls,lab:S.lab,sid,tick:!rec(sid).tick}); toast(rec(sid).tick?T('Ticked','Đã tick'):T('Tick removed','Đã bỏ tick')); renderGrade($('#main')); });
  m.querySelectorAll('[data-man]').forEach(b=>b.onclick=async()=>{ const sid=S.open, man={...(rec(sid).manual||{})}, k=b.dataset.man, off=man[k]!==undefined&&+man[k]===+b.dataset.val;   // tap the selected mark again = clear it
    if(off) delete man[k]; else man[k]=+b.dataset.val;
    S.data=await api('/api/record',{cls:S.cls,lab:S.lab,sid,manual:man}); toast(off?T('Mark cleared','Đã bỏ chọn'):T('Saved','Đã lưu')); renderGrade($('#main')); });
  m.querySelectorAll('[data-savevals]').forEach(b=>b.onclick=async()=>{ const sid=b.dataset.savevals; const vals=[...b.closest('details').querySelectorAll('input')].map(i=>i.value.trim()===''?null:+i.value.replace(',','.'));
    S.data=await api('/api/record',{cls:S.cls,lab:S.lab,sid,values:vals,src:'manual'}); toast(T('Values saved','Đã lưu số')); renderGrade($('#main')); });
  m.querySelectorAll('[data-saveov]').forEach(b=>b.onclick=async()=>{ const sid=b.dataset.saveov, d=b.closest('details'), raw=d.querySelector('[data-ov]').value.trim().replace(',','.');
    if(raw===''||isNaN(+raw)) return toast(T('Type a score first','Nhập điểm trước'));
    S.data=await api('/api/record',{cls:S.cls,lab:S.lab,sid,override:+raw,reason:d.querySelector('[data-reason]').value.trim()}); toast(T('Score saved','Đã lưu điểm')); renderGrade($('#main')); });
  m.querySelectorAll('[data-clearov]').forEach(b=>b.onclick=async()=>{ const sid=b.dataset.clearov;
    S.data=await api('/api/record',{cls:S.cls,lab:S.lab,sid,override:null,reason:''}); toast(T('Automatic score restored','Đã về điểm tự tính')); renderGrade($('#main')); });
}
