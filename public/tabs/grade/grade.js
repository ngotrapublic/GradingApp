// Tab "Grade": students by team, answer key, tick, manual marks.
function hasData(sid, lab=S.lab){ const r=rec(sid,lab); return (r.values||[]).some(v=>v!==null&&v!==''&&v!==undefined); }
function isSubmitted(sid, lab=S.lab){ return ['web','team'].includes(rec(sid,lab).src); }   // 'team' = confirmed the team's values
// team lab: the member who submitted for this student's team
function teamBy(s, lab=S.lab){ return s.team && C().students.find(x=>x.team===s.team && rec(x.sid,lab).src==='web'); }
function statusChip(s){
  const r=rec(s.sid);
  if(r.tick) return `<span class="chip tick">${T('Ticked','Đã tick')}</span>`;
  if(r.src==='team') return `<span class="chip sub">${T('Confirmed (team)','Đã xác nhận (nhóm)')}</span>`;
  if(isSubmitted(s.sid)) return `<span class="chip sub">${T('Submitted','Đã nộp')}</span>`;
  return `<span class="chip open">${T('Not submitted','Chưa nộp')}</span>`;
}
function marksReleased(s){ return !!(((C().publish||{})[S.lab]||{}).marks || rec(s.sid).show_marks); }
function renderGrade(m){
  const Lb=L(), st=sorted(), q=S.q.toLowerCase();
  const done=st.filter(s=>rec(s.sid).tick).length;
  const waiting=st.filter(s=>isSubmitted(s.sid)&&!rec(s.sid).tick).length;
  const open=st.filter(s=>!isSubmitted(s.sid)&&!rec(s.sid).tick).length;
  let html = labSeg() + `<div class="stats"><div><b>${st.length}</b>${T('students','SV')}</div><div><b>${done}</b>${T('ticked','đã tick')}</div><div><b>${waiting}</b>${T('submitted','đã nộp')}</div><div><b>${open}</b>${T('not submitted','chưa nộp')}</div></div>
    ${(()=>{ const ch=changedSince(S.lab); return ch.length? `<div class="card" style="padding:10px 12px;background:#fff7e0;border-color:#e0a800">${T(`Lab ${S.lab}: <b>${ch.length} student(s)</b> with marks not yet sent to Canvas.`,`Lab ${S.lab}: <b>${ch.length} SV</b> có điểm chưa đưa lên Canvas.`)} <a href="#" id="gosend">${T('Go to Canvas tab →','Gửi Canvas →')}</a></div>`:''; })()}
    ${pubBox()}
    <input type="search" id="q" placeholder="${T('Search name / student ID / variant','Tìm tên / MSSV / mã đề')}" value="${esc(S.q)}" style="margin-bottom:10px">`;
  { const notes={}; for(let b=1;b<=6;b++){ const mem=st.filter(s=>+s.team===b); if(mem.length) notes[b]=`${mem.filter(s=>rec(s.sid).tick).length}/${mem.length} ✓`; }
    html += `<details class="mapbox" ${S.bench?'open':''}><summary class="muted">${T('Room map – tap a table to show only that team','Sơ đồ phòng – bấm vào bàn để chỉ hiện nhóm đó')}${S.bench?` · <b>${T('Table','Bàn')} ${S.bench}</b>`:''}</summary>
      ${benchMap({active:S.bench, clickable:true, notes})}${S.bench?`<div class="btns"><button id="allbench">${T('Show all tables','Hiện tất cả các bàn')}</button></div>`:''}</details>`; }
  if(!st.length) html += `<p class="muted">${T('No students yet. Go to the <b>Class</b> tab to import the class list.','Chưa có danh sách SV. Vào tab <b>Lớp &amp; nhóm</b> để nhập danh sách.')}</p>`;
  const teams={}; st.forEach(s=>{ const k=s.team||'–'; (teams[k]=teams[k]||[]).push(s); });
  for(const [t, arr] of Object.entries(teams)){
    if(S.bench && String(t)!==String(S.bench)) continue;
    const vis = arr.filter(s=>!q || s.name.toLowerCase().includes(q) || s.sid.toLowerCase().includes(q) || String(variant(s)||'').includes(q));
    if(!vis.length) continue;
    let head = `<div class="team"><span class="sp">${t==='–'?T('No team','Chưa có nhóm'):T('Team ','Nhóm ')+t}</span>`;
    Lb.manual.filter(x=>x[3]==='team').forEach(mn=>{ if(t==='–') return; const cur=teamRec(t)[mn[0]];
      head += `<span class="lbl">${esc(manLabel(mn))}</span>` + mn[2].map(v=>`<button class="btn ${+cur===v&&cur!==undefined?'pri':''}" data-team="${t}" data-f="${mn[0]}" data-val="${v}" style="padding:4px 9px">${v}</button>`).join(''); });
    if(Lb.team_submit && t!=='–'){ const ready=arr.filter(s=>isSubmitted(s.sid)&&!rec(s.sid).tick);
      if(ready.length) head += `<button class="btn pri" data-tickteam="${t}" style="padding:4px 9px">${T(`Tick ${ready.length} submitted / confirmed`,`Tick ${ready.length} SV đã nộp / xác nhận`)}</button>`; }
    head += `</div>`;
    html += `<div class="card">${head}` + vis.map(s=>{
      const v=variant(s), r=rec(s.sid), sc=score(s);
      let row = `<div class="st" data-sid="${esc(s.sid)}"><div class="nm"><b>${esc(s.name)}</b><small>${esc(s.sid)} | ${T('M','TV')} ${s.member||'–'} | ${T('var.','mã')} ${v||'–'}</small></div>
        ${statusChip(s)}${marksReleased(s)?`<span class="chip marks">${T('marks on','điểm hiện')}</span>`:''}<span class="sc">${r.override!=null?'✎ ':''}${sc}</span></div>`;
      if(S.open===s.sid) row += panel(s);
      return row; }).join('') + `</div>`;
  }
  m.innerHTML = html; bindSeg(m);
  m.querySelectorAll('[data-bench]').forEach(g=>g.onclick=()=>{ S.bench = String(S.bench)===g.dataset.bench? null : g.dataset.bench; renderGrade(m); });
  if($('#allbench')) $('#allbench').onclick=()=>{ S.bench=null; renderGrade(m); };
  if($('#gosend')) $('#gosend').onclick=e=>{e.preventDefault(); S.view='sum'; render();};
  $('#q').oninput=e=>{S.q=e.target.value; const p=e.target.selectionStart; renderGrade(m); const n=$('#q'); n.focus(); n.setSelectionRange(p,p);};
  m.querySelectorAll('.st').forEach(e=>e.onclick=()=>{S.open = S.open===e.dataset.sid? null : e.dataset.sid; renderGrade(m);});
  m.querySelectorAll('[data-team]').forEach(b=>b.onclick=async ev=>{ev.stopPropagation(); const cur=teamRec(b.dataset.team)[b.dataset.f], off=cur!==undefined&&+cur===+b.dataset.val;   // tap the selected mark again = clear it
    S.data=await api('/api/team',{cls:S.cls,lab:S.lab,team:b.dataset.team,field:b.dataset.f,value:off?null:+b.dataset.val}); toast(off?T('Mark cleared','Đã bỏ chọn'):T('Saved','Đã lưu')); renderGrade(m);});
  bindPanel(m);
  m.querySelectorAll('[data-tickteam]').forEach(b=>b.onclick=async ev=>{ ev.stopPropagation(); b.disabled=true;
    for(const s of C().students.filter(x=>String(x.team)===b.dataset.tickteam && isSubmitted(x.sid) && !rec(x.sid).tick))
      S.data=await api('/api/record',{cls:S.cls,lab:S.lab,sid:s.sid,tick:true});
    toast(T('Ticked','Đã tick')); renderGrade(m); });
  m.querySelectorAll('[data-pub]').forEach(c=>c.onchange=async()=>{ S.data=await api('/api/publish',{cls:S.cls,lab:S.lab,[c.dataset.pub]:c.checked});
    toast(c.checked? T('Students can see it now','SV đã xem được') : T('Hidden from students','Đã ẩn với SV')); renderGrade(m); });
  $('#qrs').onclick=()=>showQR(true);
}
// what students may see on the student page, for this class + lab
function pubBox(){
  const p=((C().publish||{})[S.lab])||{};
  const sw=(k,label)=>`<label class="switch"><input type="checkbox" data-pub="${k}" ${p[k]?'checked':''}><span class="knob"></span>${label}</label>`;
  return `<div class="card pubbox"><div class="pubtitle">${T(`Student page – Lab ${S.lab}, ${esc(C().name)}`,`Trang SV – Lab ${S.lab}, ${esc(C().name)}`)}</div>
    <div class="btns">${sw('card',T('Show card','Cho SV xem đề'))}${sw('submit',T('Accept submissions','Nhận bài'))}${canManage()?sw('marks',T('Release marks (all)','Công bố điểm (cả lớp)')):''}
    <button class="btn" id="qrs">${T('QR for students','QR cho SV')}</button></div>
    ${canManage()?`<p class="muted" style="margin:6px 0 0">${T('Or open a student and release marks for that student only.','Hoặc mở từng SV để công bố điểm riêng.')}</p>`:''}</div>`;
}
function panel(s){
  const Lb=L(), v=variant(s), V=v&&Lb.variants[v], r=rec(s.sid);
  if(!V) return `<div class="panel"><p class="muted">${T('This student has no team / member yet, so no variant. Go to the <b>Students</b> tab.','SV chưa có nhóm / thành viên nên chưa có mã đề. Vào tab <b>SV &amp; nhóm</b>.')}</p></div>`;
  const figs=[...(V.figs||[]), ...(V.image?[`/api/asset/${C().course}/${V.image}`]:[])];
  let h = `<div class="panel"><p class="info">${V.info.map(sub).join('<br>')}</p>` +
    (figs.length?`<details class="figs"><summary class="muted">${T('Circuit / task figure','Hình đề bài')}</summary>${figs.map(f=>`<a href="${f}" target="_blank"><img src="${f}" alt=""></a>`).join('')}</details>`:'') + `<div class="scroll"><table><tr><th>${T('Quantity','Đại lượng')}</th><th>${T('Key','Đáp án')}</th><th>${T('Full marks','Đủ điểm')}</th><th>${T('Submitted','SV nộp')}</th><th>${T('Marks','Điểm')}</th></tr>`;
  const editKeys=canManage();
  Lb.questions.forEach((q,i)=>{ const k=V.keys[i], x=(r.values||[])[i], tol=qrule(q).full, calc=(qrule(q).calc==='rc_fc');
    if(!q[3]){ h += `<tr><td>${sub(q[1])}<br><small class="muted">${esc(q[2])}</small></td><td class="num">–</td><td class="num">–</td><td class="num">${fmt(x)}</td><td>–</td></tr>`; return; }
    const y=qval(q, r.values, i), mk=mark(y,k,q[3],qrule(q));
    const cl = mk===null?'':(mk===q[3]?'full':(mk>0?'half':'zero'));
    const keyCell=editKeys
      ? `<input class="keyin" inputmode="decimal" data-keyi="${i}" value="${k??''}">`
      : `<b>${fmt(k)}</b>`;
    h += `<tr><td>${sub(q[1])}<br><small class="muted">${esc(q[2])}${calc?T(' – marked on f<sub>c</sub> = 1/(2πRC), key = target f<sub>c</sub> (kHz)',' – chấm theo f<sub>c</sub> = 1/(2πRC), đáp án = f<sub>c</sub> mục tiêu (kHz)'):''}</small></td><td class="num">${keyCell}</td><td class="num">${fmt(k*(1-tol))} – ${fmt(k*(1+tol))}${tol!==K().rule.full?`<br><small class="muted">±${Math.round(tol*100)}%</small>`:''}</td>
      <td class="num">${fmt(x)}${calc&&y!==null?`<br><small class="muted">f<sub>c</sub> = ${fmt(y)} kHz</small>`:''}</td><td class="${cl}">${mk===null?'–':(r.tick?mk:'('+mk+')')}/${q[3]}</td></tr>`; });
  h += `</table></div>`;
  if(editKeys) h += `<p class="muted">${T(`Edit the keys above if they are wrong. Saving applies to <b>every student with variant ${v}</b> and updates automatic marks.`, `Sửa đáp án ở trên nếu sai. Lưu sẽ áp dụng cho <b>mọi SV mã đề ${v}</b> và cập nhật điểm tự tính.`)}${V.keys_edited?` <b>${T('(already edited)','(đã sửa)')}</b>`:''}</p>
    <div class="btns"><button class="on" data-savekeys="${v}">${T('Save answer keys','Lưu đáp án')}</button>${V.keys_edited?`<button data-resetkeys="${v}">${T('Back to original keys','Về đáp án gốc')}</button>`:''}</div>`;
  if(Lb.team_submit){ const by=teamBy(s);
    h += `<p class="muted">${by? T(`Team values submitted by <b>${esc(by.name)}</b>.`,`Số của nhóm do <b>${esc(by.name)}</b> nộp.`) : T('Nobody in this team has submitted yet.','Nhóm này chưa có ai nộp.')}</p>`;
    if(by && by.sid!==s.sid && !r.tick) h += r.src==='team'
      ? `<div class="btns"><button data-teamconf="${esc(s.sid)}" data-off="1">${T('Remove this confirmation','Bỏ xác nhận của SV này')}</button></div>`
      : `<div class="btns"><button class="on" data-teamconf="${esc(s.sid)}">${T('Confirm for this student (copy the team values)','Xác nhận thay SV này (chép số của nhóm)')}</button></div>`; }
  h += `<button class="big ${r.tick?'on':''}" data-tick="${esc(s.sid)}">${r.tick?T('✓ Ticked – tap to undo','✓ Đã tick – bấm để bỏ'):T('Tick: I saw the reading on the instrument','Tick: đã xem số đo trên máy')}</button>`;
  if(canManage()){
    const allOn=!!(((C().publish||{})[S.lab]||{}).marks), on=allOn||!!r.show_marks;
    h += `<div class="btns" style="margin-top:8px"><button class="btn ${on?'pri':''}" data-showmarks="${esc(s.sid)}" ${allOn?'disabled':''}>${on?T('Marks released to this student','Đã công bố điểm cho SV này'):T('Release marks to this student','Công bố điểm cho SV này')}</button></div>`;
    if(allOn) h += `<p class="muted">${T('Class-wide release is on. Turn it off above to release per student.', 'Đang công bố cả lớp. Tắt công tắc ở trên nếu muốn công bố từng SV.')}</p>`;
  }
  Lb.manual.filter(x=>x[3]==='student').forEach(mn=>{ const cur=(r.manual||{})[mn[0]];
    h += `<div class="btns"><span class="lbl">${esc(manLabel(mn))}:</span>` + mn[2].map(val=>`<button data-man="${mn[0]}" data-val="${val}" class="${cur!==undefined&&+cur===val?'on':''}">${val}</button>`).join('') + `</div>`; });
  const ph=((C().photos||{})[S.lab]||{})[s.sid]||[];
  h += `<div class="lbl">${T('Photos','Ảnh mạch')} (${ph.length})</div>` + (ph.length? `<div class="thumbs">${ph.map(p=>`<a href="/api/photo/${p.id}.jpg" target="_blank"><img src="/api/photo/${p.id}.jpg" alt="photo"></a>`).join('')}</div>` : `<p class="muted">${T('No photo yet.','Chưa có ảnh.')}</p>`);
  h += `<details><summary class="muted">${T('Enter / edit values by hand (if the student could not submit)','Nhập / sửa số tay (khi SV không nộp được)')}</summary><div class="edit">` +
    Lb.questions.map((q,i)=>`<div><label>${sub(q[1])} (${esc(q[2])})</label><input inputmode="decimal" data-i="${i}" value="${(r.values||[])[i]??''}"></div>`).join('') +
    `</div><div class="btns"><button class="on" data-savevals="${esc(s.sid)}">${T('Save values','Lưu số')}</button></div></details>`;
  const ov=r.override!=null;
  if(canManage()) h += `<details ${ov?'open':''}><summary class="muted">${T('Set the score by hand (special cases)','Sửa điểm tay (trường hợp đặc biệt)')}</summary>
    <p class="muted">${T('This score replaces the automatic score everywhere (list, Canvas file, Excel, student page).','Điểm này thay cho điểm tự tính ở mọi nơi (danh sách, file Canvas, Excel, trang SV).')}</p>
    <div class="edit"><div><label>${T('Score','Điểm')} (0–${Lb.total})</label><input inputmode="decimal" data-ov value="${ov?r.override:''}"></div>
    <div><label>${T('Reason','Lý do')}</label><input data-reason value="${esc(r.reason||'')}" placeholder="${T('e.g. make-up session','vd: làm bù')}"></div></div>
    <div class="btns"><button class="on" data-saveov="${esc(s.sid)}">${T('Save score','Lưu điểm')}</button>${ov?`<button data-clearov="${esc(s.sid)}">${T('Back to automatic score','Bỏ điều chỉnh')}</button>`:''}</div></details>`;
  h += `<p class="muted">${T('Total','Tổng')} Lab ${S.lab}: <b>${score(s)}</b>${ov?T(' (set by hand',' (điểm tay')+(r.reason?': '+esc(r.reason):'')+')':''} / ${Lb.total}${(r.src==='manual'?T(' | entered by hand',' | số nhập tay'):(r.src==='web'?T(` | submitted on the web ${esc(r.updated||'')}`,` | SV nộp trên web lúc ${esc(r.updated||'')}`):(r.src==='team'?T(` | confirmed the team values ${esc(r.updated||'')}`,` | xác nhận số của nhóm lúc ${esc(r.updated||'')}`):'')))}</p></div>`;
  return h;
}
function bindPanel(m){
  m.querySelectorAll('.panel').forEach(p=>p.onclick=e=>e.stopPropagation());
  m.querySelectorAll('[data-tick]').forEach(b=>b.onclick=async()=>{ const sid=b.dataset.tick; S.data=await api('/api/record',{cls:S.cls,lab:S.lab,sid,tick:!rec(sid).tick}); toast(rec(sid).tick?T('Ticked','Đã tick'):T('Tick removed','Đã bỏ tick')); renderGrade($('#main')); });
  m.querySelectorAll('[data-teamconf]').forEach(b=>b.onclick=async()=>{ const sid=b.dataset.teamconf, s=C().students.find(x=>x.sid===sid), by=teamBy(s), off=!!b.dataset.off;
    S.data=await api('/api/record',{cls:S.cls,lab:S.lab,sid,values:off?null:rec(by.sid).values,src:off?'':'team'});
    toast(off?T('Confirmation removed','Đã bỏ xác nhận'):T('Confirmed with the team values','Đã xác nhận bằng số của nhóm')); renderGrade($('#main')); });
  m.querySelectorAll('[data-showmarks]').forEach(b=>b.onclick=async()=>{ const sid=b.dataset.showmarks; const on=!rec(sid).show_marks;
    S.data=await api('/api/record',{cls:S.cls,lab:S.lab,sid,show_marks:on}); toast(on?T('Marks released to this student','Đã công bố điểm cho SV này'):T('Marks hidden for this student','Đã ẩn điểm với SV này')); renderGrade($('#main')); });
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
  m.querySelectorAll('[data-savekeys]').forEach(b=>b.onclick=async()=>{
    const panel=b.closest('.panel'), keys=[...panel.querySelectorAll('[data-keyi]')].sort((a,c)=>+a.dataset.keyi-+c.dataset.keyi).map(i=>i.value.trim());
    if(keys.some(v=>v===''||isNaN(+v.replace(',','.')))) return toast(T('Every key must be a number.','Mọi đáp án phải là số.'));
    const j=await api('/api/key_override',{cls:S.cls,lab:S.lab,variant:b.dataset.savekeys,keys:keys.map(v=>+v.replace(',','.'))});
    S.data=j.data; S.keys=j.keys; toast(T('Answer keys saved','Đã lưu đáp án')); renderGrade($('#main'));
  });
  m.querySelectorAll('[data-resetkeys]').forEach(b=>b.onclick=async()=>{
    if(!confirm(T('Restore the original keys for this variant?','Khôi phục đáp án gốc của mã đề này?'))) return;
    const j=await api('/api/key_override',{cls:S.cls,lab:S.lab,variant:b.dataset.resetkeys,keys:null});
    S.data=j.data; S.keys=j.keys; toast(T('Original keys restored','Đã về đáp án gốc')); renderGrade($('#main'));
  });
}
